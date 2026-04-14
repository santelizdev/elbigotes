import pytest
from rest_framework.test import APIClient

from apps.claims.models import ClaimRequest
from apps.ingestion.models import Source
from apps.places.choices import PlaceVerificationStatus
from apps.places.models import Place
from apps.taxonomy.models import Category


@pytest.mark.django_db
def test_create_claim_request_for_unverified_active_place():
    client = APIClient()
    source = Source.objects.create(name="Seed Manual", slug="seed-manual")
    category = Category.objects.create(name="Veterinarias", slug="veterinarias")
    place = Place.objects.create(
        name="Vet Centro",
        slug="vet-centro",
        category=category,
        source=source,
        status="active",
        is_verified=False,
        summary="Atención general",
        formatted_address="Santiago, Región Metropolitana, Chile",
    )

    response = client.post(
        f"/api/v1/claims/places/{place.slug}/requests/",
        data={
            "claimer_name": "Paula Rojas",
            "organization_name": "Vet Centro",
            "email": "paula@example.com",
            "phone": "+56912345678",
            "relationship_to_place": "Propietaria",
            "message": "Quiero administrar esta ficha.",
            "evidence_url": "https://example.com/documento",
        },
        format="json",
    )

    assert response.status_code == 201
    claim = ClaimRequest.objects.get(place=place, email="paula@example.com")
    place.refresh_from_db()
    assert claim.claimer_name == "Paula Rojas"
    assert claim.status == "pending"
    assert place.verification_status == PlaceVerificationStatus.CLAIM_REQUESTED


@pytest.mark.django_db
def test_create_claim_request_rejects_verified_place():
    client = APIClient()
    source = Source.objects.create(name="Seed Manual", slug="seed-manual")
    category = Category.objects.create(name="Guarderías", slug="guarderias")
    place = Place.objects.create(
        name="Guardería Centro",
        slug="guarderia-centro",
        category=category,
        source=source,
        status="active",
        is_verified=True,
        summary="Cuidado diario",
        formatted_address="Santiago, Región Metropolitana, Chile",
    )

    response = client.post(
        f"/api/v1/claims/places/{place.slug}/requests/",
        data={
            "claimer_name": "Camila",
            "email": "camila@example.com",
            "relationship_to_place": "Encargada",
            "message": "Necesito reclamar la propiedad.",
        },
        format="json",
    )

    assert response.status_code == 400
    assert "ya está verificada" in str(response.data)


@pytest.mark.django_db
def test_create_claim_request_rejects_place_with_open_claim_in_review():
    client = APIClient()
    source = Source.objects.create(name="Seed Manual", slug="seed-manual")
    category = Category.objects.create(name="Veterinarias", slug="veterinarias")
    place = Place.objects.create(
        name="Vet Norte",
        slug="vet-norte",
        category=category,
        source=source,
        status="active",
        verification_status=PlaceVerificationStatus.CLAIM_REQUESTED,
        summary="Atención general",
        formatted_address="Santiago, Región Metropolitana, Chile",
    )
    ClaimRequest.objects.create(
        place=place,
        status="pending",
        claimer_name="Paula",
        email="paula@example.com",
        relationship_to_place="Dueña",
    )

    response = client.post(
        f"/api/v1/claims/places/{place.slug}/requests/",
        data={
            "claimer_name": "Camila",
            "email": "camila@example.com",
            "relationship_to_place": "Encargada",
            "message": "Necesito reclamar la propiedad.",
        },
        format="json",
    )

    assert response.status_code == 400
    assert "ya tiene una solicitud" in str(response.data)
