import pytest
from rest_framework.test import APIClient

from apps.accounts.models import (
    BusinessKind,
    BusinessProfile,
    MembershipStatus,
    PetOwnerProfile,
    PetProfile,
    User,
    UserRole,
)
from apps.accounts.tokens import create_access_token
from apps.taxonomy.models import Category


@pytest.mark.django_db
def test_register_business_account_creates_grace_or_free_profile():
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
    assert profile.membership_status == MembershipStatus.GRACE
    assert profile.grace_expires_at is not None
    assert profile.place is not None
    assert profile.place.category.slug == "veterinarias"
    assert profile.place.status == "draft"
    assert profile.place.owner_business_profile == profile


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
    assert pet.name == "Luna"
    assert pet.species == "dog"


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
