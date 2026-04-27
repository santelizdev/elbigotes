from datetime import timedelta

import pytest
from django.contrib.gis.geos import Point
from django.core.exceptions import ValidationError
from django.utils import timezone
from rest_framework.test import APIClient

from apps.accounts.models import (
    BusinessKind,
    BusinessProfile,
    PetOwnerProfile,
    PetProfile,
    SavedPlace,
    User,
    UserRole,
)
from apps.accounts.tokens import create_access_token
from apps.lost_pets.models import LostPetReport
from apps.memberships.models import (
    MembershipAssignment,
    MembershipAssignmentStatus,
    MembershipAudience,
    MembershipBillingInterval,
    MembershipPlan,
)
from apps.places.models import Place
from apps.taxonomy.models import Category


@pytest.mark.django_db
def test_register_business_account_creates_profile_and_primary_place():
    client = APIClient()
    Category.objects.create(name="Veterinarias", slug="veterinarias")

    response = client.post(
        "/api/v1/accounts/register/business/",
        data={
            "email": "vet@example.com",
            "password": "Password123!",
            "first_name": "Paula",
            "last_name": "Rojas",
            "business_name": "Vet Central",
            "business_kind": BusinessKind.VETERINARY,
            "phone": "+56911111111",
            "commune": "Providencia",
            "region": "Región Metropolitana",
            "place_label": "Punto confirmado en mapa",
            "latitude": -33.4257,
            "longitude": -70.6175,
            "marketing_opt_in": True,
        },
        format="json",
    )

    assert response.status_code == 201
    user = User.objects.get(email="vet@example.com")
    profile = BusinessProfile.objects.get(user=user)

    assert user.role == UserRole.BUSINESS_OWNER
    assert user.email_verified is True
    assert profile.place is not None
    assert profile.place.category.slug == "veterinarias"
    assert profile.place.status == "draft"
    assert profile.place.owner_business_profile == profile
    membership = MembershipAssignment.objects.get(owner_object_id=profile.id)
    assert membership.plan.slug == "business-trial"
    assert membership.status == MembershipAssignmentStatus.TRIAL
    assert membership.ends_at is not None
    assert membership.renews_at is not None
    assert response.data["profile"]["memberships"][0]["plan_slug"] == "business-trial"
    assert response.data["profile"]["memberships"][0]["access_tier"] == "business_trial"


@pytest.mark.django_db
def test_register_non_billable_business_assigns_lifetime_free_membership():
    client = APIClient()
    Category.objects.create(name="Refugios", slug="refugios-albergues")

    response = client.post(
        "/api/v1/accounts/register/business/",
        data={
            "email": "refugio@example.com",
            "password": "Password123!",
            "first_name": "Paula",
            "last_name": "Rojas",
            "business_name": "Refugio Esperanza",
            "business_kind": BusinessKind.SHELTER,
            "phone": "+56911111111",
            "commune": "Providencia",
            "region": "Región Metropolitana",
            "place_label": "Punto confirmado en mapa",
            "latitude": -33.4257,
            "longitude": -70.6175,
            "marketing_opt_in": True,
        },
        format="json",
    )

    assert response.status_code == 201
    profile = BusinessProfile.objects.get(user__email="refugio@example.com")
    membership = MembershipAssignment.objects.get(owner_object_id=profile.id)

    assert membership.plan.slug == "business-free-lifetime"
    assert membership.status == MembershipAssignmentStatus.ACTIVE
    assert membership.ends_at is None
    assert response.data["profile"]["memberships"][0]["access_tier"] == "business_free_lifetime"


@pytest.mark.django_db
def test_register_pet_owner_account_creates_profile_and_initial_pet():
    client = APIClient()

    response = client.post(
        "/api/v1/accounts/register/pet-owner/",
        data={
            "email": "tutor@example.com",
            "password": "Password123!",
            "first_name": "Camila",
            "last_name": "Diaz",
            "phone": "+56922222222",
            "commune": "Ñuñoa",
            "region": "Región Metropolitana",
            "marketing_opt_in": True,
            "pet": {
                "name": "Luna",
                "species": "dog",
                "breed": "Mestiza",
                "sex": "female",
            },
        },
        format="json",
    )

    assert response.status_code == 201

    user = User.objects.get(email="tutor@example.com")
    profile = PetOwnerProfile.objects.get(user=user)
    pet = PetProfile.objects.get(owner=profile)

    assert user.role == UserRole.PET_OWNER
    assert user.email_verified is True
    assert pet.name == "Luna"
    assert pet.species == "dog"
    membership = MembershipAssignment.objects.get(owner_object_id=profile.id)
    assert membership.plan.slug == "pet-owner-free"
    assert membership.status == MembershipAssignmentStatus.ACTIVE
    assert response.data["profile"]["memberships"][0]["plan_slug"] == "pet-owner-free"


@pytest.mark.django_db
def test_business_login_workspace_update_and_branch_creation():
    client = APIClient()
    Category.objects.create(name="Veterinarias", slug="veterinarias")

    registration_response = client.post(
        "/api/v1/accounts/register/business/",
        data={
            "email": "owner@example.com",
            "password": "Password123!",
            "first_name": "Vale",
            "last_name": "Paz",
            "business_name": "Vet Norte",
            "business_kind": BusinessKind.VETERINARY,
            "phone": "+56955556666",
            "commune": "Providencia",
            "region": "Región Metropolitana",
            "place_label": "Providencia 123",
            "latitude": -33.4257,
            "longitude": -70.6175,
            "marketing_opt_in": True,
        },
        format="json",
    )

    assert registration_response.status_code == 201

    login_response = client.post(
        "/api/v1/accounts/login/",
        data={"email": "owner@example.com", "password": "Password123!"},
        format="json",
    )
    assert login_response.status_code == 201
    token = login_response.data["token"]

    auth_client = APIClient()
    auth_client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    workspace_response = auth_client.get("/api/v1/accounts/me/business/")
    assert workspace_response.status_code == 200
    assert workspace_response.data["profile"]["business_name"] == "Vet Norte"
    assert len(workspace_response.data["places"]) == 1
    assert workspace_response.data["profile"]["memberships"][0]["plan_slug"] == "business-trial"

    update_response = auth_client.patch(
        "/api/v1/accounts/me/business/",
        data={
            "first_name": "Valentina",
            "last_name": "Paz",
            "business_name": "Vet Norte Premium",
            "phone": "+56955556666",
            "commune": "Providencia",
            "region": "Región Metropolitana",
            "website": "https://vetnorte.cl",
            "marketing_opt_in": True,
            "notes": "Atención extendida",
        },
        format="json",
    )
    assert update_response.status_code == 200
    assert update_response.data["profile"]["business_name"] == "Vet Norte Premium"

    branch_response = auth_client.post(
        "/api/v1/accounts/me/business/branches/",
        data={
            "branch_name": "Vet Norte Maipu",
            "phone": "+56977778888",
            "commune": "Maipú",
            "region": "Región Metropolitana",
            "website": "",
            "place_label": "Pajaritos 456",
            "latitude": -33.5124,
            "longitude": -70.7611,
            "notes": "",
        },
        format="json",
    )
    assert branch_response.status_code == 201
    assert branch_response.data["status"] == "draft"

    profile = BusinessProfile.objects.get(user__email="owner@example.com")
    assert profile.owned_places.count() == 2


@pytest.mark.django_db
def test_business_workspace_requires_authenticated_business_owner():
    client = APIClient()

    unauthenticated_response = client.get("/api/v1/accounts/me/business/")
    assert unauthenticated_response.status_code == 403

    user = User.objects.create_user(
        email="pet-owner@example.com",
        password="Password123!",
        role=UserRole.PET_OWNER,
    )
    token = create_access_token(user)

    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    forbidden_response = client.get("/api/v1/accounts/me/business/")

    assert forbidden_response.status_code == 403


@pytest.mark.django_db
def test_business_workspace_backfills_default_membership_for_legacy_profile():
    client = APIClient()
    user = User.objects.create_user(
        email="legacy-biz@example.com",
        password="Password123!",
        role=UserRole.BUSINESS_OWNER,
    )
    profile = BusinessProfile.objects.create(
        user=user,
        business_name="Veterinaria Histórica",
        business_kind=BusinessKind.VETERINARY,
        phone="+56944445555",
        commune="Providencia",
        region="Región Metropolitana",
    )
    token = create_access_token(user)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    response = client.get("/api/v1/accounts/me/business/")

    assert response.status_code == 200
    profile.refresh_from_db()
    membership = MembershipAssignment.objects.get(owner_object_id=profile.id)
    assert membership.plan.slug == "business-trial"
    assert response.data["profile"]["memberships"][0]["access_tier"] == "business_trial"


@pytest.mark.django_db
def test_business_workspace_marks_expired_trial_membership():
    client = APIClient()
    user = User.objects.create_user(
        email="expired-biz@example.com",
        password="Password123!",
        role=UserRole.BUSINESS_OWNER,
    )
    profile = BusinessProfile.objects.create(
        user=user,
        business_name="Veterinaria Expirada",
        business_kind=BusinessKind.VETERINARY,
        phone="+56944445555",
        commune="Providencia",
        region="Región Metropolitana",
    )
    plan = MembershipPlan.objects.create(
        name="Trial Manual",
        slug="trial-manual",
        audience=MembershipAudience.BUSINESS,
        billing_interval=MembershipBillingInterval.MONTHLY,
        price_amount=0,
        metadata={"lifecycle": "business_trial"},
    )
    MembershipAssignment.objects.create(
        plan=plan,
        owner=profile,
        status=MembershipAssignmentStatus.TRIAL,
        starts_at=timezone.now() - timedelta(days=45),
        ends_at=timezone.now() - timedelta(days=15),
        renews_at=timezone.now() - timedelta(days=15),
    )
    token = create_access_token(user)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    response = client.get("/api/v1/accounts/me/business/")

    assert response.status_code == 200
    assert response.data["profile"]["memberships"][0]["status"] == "expired"
    assert response.data["profile"]["memberships"][0]["renewal_required"] is True


@pytest.mark.django_db
def test_pet_owner_workspace_returns_pets_reports_and_memberships():
    client = APIClient()
    user = User.objects.create_user(
        email="pet-owner@example.com",
        password="Password123!",
        first_name="Camila",
        role=UserRole.PET_OWNER,
    )
    profile = PetOwnerProfile.objects.create(
        user=user,
        phone="+56999990000",
        commune="Ñuñoa",
        region="Región Metropolitana",
        marketing_opt_in=True,
    )
    pet = PetProfile.objects.create(owner=profile, name="Luna", species="dog", sex="female")
    plan = MembershipPlan.objects.create(
        name="Tutor Plus",
        audience=MembershipAudience.PET_OWNER,
        billing_interval=MembershipBillingInterval.MONTHLY,
        price_amount=4990,
    )
    MembershipAssignment.objects.create(
        plan=plan,
        owner=profile,
        status=MembershipAssignmentStatus.ACTIVE,
        starts_at=timezone.now(),
        renews_at=timezone.now() + timedelta(days=30),
    )
    report = LostPetReport.objects.create(
        pet_name="Luna",
        species="dog",
        sex="female",
        color_description="Blanca",
        status="lost",
        last_seen_at="2026-03-20T12:30:00Z",
        last_seen_address="Diagonal 123, Ñuñoa",
        reporter_name="Camila",
        reporter_phone="+56999990000",
        reporter_email="pet-owner@example.com",
        moderation_status="approved",
        pet_profile=pet,
        metadata={"pet_owner_profile_id": profile.id, "pet_profile_id": pet.id},
    )

    token = create_access_token(user)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    response = client.get("/api/v1/accounts/me/pet-owner/")

    assert response.status_code == 200
    assert response.data["profile"]["phone"] == "+56999990000"
    assert len(response.data["profile"]["pets"]) == 1
    assert response.data["profile"]["pets"][0]["name"] == "Luna"
    assert len(response.data["profile"]["memberships"]) == 1
    assert response.data["profile"]["memberships"][0]["plan_slug"] == "tutor-plus"
    assert len(response.data["reports"]) == 1
    assert response.data["reports"][0]["id"] == str(report.id)
    assert response.data["saved_places"] == []


@pytest.mark.django_db
def test_pet_owner_can_save_check_and_remove_places():
    client = APIClient()
    user = User.objects.create_user(
        email="saved@example.com",
        password="Password123!",
        role=UserRole.PET_OWNER,
    )
    PetOwnerProfile.objects.create(
        user=user,
        phone="+56999990000",
        commune="Providencia",
        region="Región Metropolitana",
    )
    category = Category.objects.create(name="Veterinarias", slug="veterinarias")
    place = Place.objects.create(
        name="Vet Favorita",
        slug="vet-favorita",
        category=category,
        status="active",
        commune="Providencia",
        region="Región Metropolitana",
        formatted_address="Providencia 123, Santiago, Chile",
        summary="Atención cercana",
        location=Point(-70.6175, -33.4257, srid=4326),
        google_rating="4.9",
        google_reviews_count=83,
    )

    token = create_access_token(user)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    save_response = client.post(
        "/api/v1/accounts/me/saved-places/",
        data={"place_slug": place.slug},
        format="json",
    )

    assert save_response.status_code == 201
    assert save_response.data["slug"] == place.slug
    assert save_response.data["google_rating"] == 4.9
    assert SavedPlace.objects.filter(user=user, place=place).exists() is True

    status_response = client.get(f"/api/v1/accounts/me/saved-places/{place.slug}/")
    assert status_response.status_code == 200
    assert status_response.data["is_saved"] is True
    assert status_response.data["item"]["slug"] == place.slug

    duplicate_response = client.post(
        "/api/v1/accounts/me/saved-places/",
        data={"place_slug": place.slug},
        format="json",
    )
    assert duplicate_response.status_code == 200
    assert SavedPlace.objects.filter(user=user, place=place).count() == 1

    list_response = client.get("/api/v1/accounts/me/saved-places/")
    assert list_response.status_code == 200
    assert len(list_response.data) == 1
    assert list_response.data[0]["slug"] == place.slug

    delete_response = client.delete(f"/api/v1/accounts/me/saved-places/{place.slug}/")
    assert delete_response.status_code == 204
    assert SavedPlace.objects.filter(user=user, place=place).exists() is False

    status_after_delete = client.get(f"/api/v1/accounts/me/saved-places/{place.slug}/")
    assert status_after_delete.status_code == 200
    assert status_after_delete.data["is_saved"] is False
    assert status_after_delete.data["item"] is None


@pytest.mark.django_db
def test_pet_owner_workspace_includes_saved_places():
    client = APIClient()
    user = User.objects.create_user(
        email="workspace-saved@example.com",
        password="Password123!",
        first_name="Josefa",
        role=UserRole.PET_OWNER,
    )
    profile = PetOwnerProfile.objects.create(
        user=user,
        phone="+56988887777",
        commune="Santiago",
        region="Región Metropolitana",
        marketing_opt_in=True,
    )
    category = Category.objects.create(name="Guarderías", slug="guarderias")
    place = Place.objects.create(
        name="Guarderia Central",
        slug="guarderia-central",
        category=category,
        status="active",
        commune="Santiago",
        region="Región Metropolitana",
        formatted_address="Santiago Centro, Chile",
        summary="Cuidado diario para perros",
        google_rating="4.6",
        google_reviews_count=41,
    )
    SavedPlace.objects.create(user=user, place=place)

    token = create_access_token(user)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    response = client.get("/api/v1/accounts/me/pet-owner/")

    assert response.status_code == 200
    assert response.data["profile"]["phone"] == profile.phone
    assert len(response.data["saved_places"]) == 1
    assert response.data["saved_places"][0]["slug"] == place.slug
    assert response.data["saved_places"][0]["name"] == place.name


@pytest.mark.django_db
def test_saved_places_require_authenticated_pet_owner():
    client = APIClient()
    category = Category.objects.create(name="Parques", slug="parques-pet-friendly")
    place = Place.objects.create(
        name="Parque Guardado",
        slug="parque-guardado",
        category=category,
        status="active",
        commune="Providencia",
        region="Región Metropolitana",
        formatted_address="Providencia, Chile",
        summary="Lugar abierto",
    )

    unauthenticated_response = client.post(
        "/api/v1/accounts/me/saved-places/",
        data={"place_slug": place.slug},
        format="json",
    )
    assert unauthenticated_response.status_code == 403

    business_user = User.objects.create_user(
        email="biz-save@example.com",
        password="Password123!",
        role=UserRole.BUSINESS_OWNER,
    )
    BusinessProfile.objects.create(
        user=business_user,
        business_name="Vet Norte",
        business_kind=BusinessKind.VETERINARY,
        phone="+56944445555",
        commune="Providencia",
        region="Región Metropolitana",
    )
    token = create_access_token(business_user)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    forbidden_response = client.get(f"/api/v1/accounts/me/saved-places/{place.slug}/")
    assert forbidden_response.status_code == 403


@pytest.mark.django_db
def test_membership_assignment_rejects_wrong_owner_type_for_plan():
    business_user = User.objects.create_user(
        email="biz@example.com",
        password="Password123!",
        role=UserRole.BUSINESS_OWNER,
    )
    business_profile = BusinessProfile.objects.create(
        user=business_user,
        business_name="Vet Sur",
        business_kind=BusinessKind.VETERINARY,
        phone="+56944445555",
        commune="Providencia",
        region="Región Metropolitana",
    )
    pet_owner_user = User.objects.create_user(
        email="pet@example.com",
        password="Password123!",
        role=UserRole.PET_OWNER,
    )
    pet_owner_profile = PetOwnerProfile.objects.create(
        user=pet_owner_user,
        phone="+56911112222",
    )
    plan = MembershipPlan.objects.create(
        name="Tutor Base",
        audience=MembershipAudience.PET_OWNER,
        billing_interval=MembershipBillingInterval.MONTHLY,
    )

    with pytest.raises(ValidationError):
        MembershipAssignment.objects.create(
            plan=plan,
            owner=business_profile,
            status=MembershipAssignmentStatus.TRIAL,
            starts_at=timezone.now(),
        )

    valid_assignment = MembershipAssignment.objects.create(
        plan=plan,
        owner=pet_owner_profile,
        status=MembershipAssignmentStatus.TRIAL,
        starts_at=timezone.now(),
    )

    assert valid_assignment.owner_object_id == pet_owner_profile.id
