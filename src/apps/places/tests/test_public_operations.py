from datetime import timedelta
from io import StringIO

import pytest
from django.core.exceptions import ValidationError
from django.core.management import call_command
from django.utils import timezone
from rest_framework.test import APIClient

from apps.places.models import PublicPetOperation


@pytest.mark.django_db
def test_public_operations_list_returns_only_published_and_current_by_default():
    client = APIClient()
    now = timezone.now()

    visible_operation = PublicPetOperation.objects.create(
        title="Vacunación Quilicura",
        slug="vacunacion-quilicura",
        operation_type="vaccination",
        creator_type="public",
        creator_name="Municipalidad de Quilicura",
        address="Av. Principal 123",
        commune="Quilicura",
        region="Región Metropolitana",
        latitude=-33.363201,
        longitude=-70.746512,
        starts_at=now + timedelta(days=2),
        status="published",
    )
    PublicPetOperation.objects.create(
        title="Operativo vencido",
        slug="operativo-vencido",
        operation_type="microchip",
        creator_type="public",
        creator_name="Municipalidad de Quilicura",
        address="Pasaje 456",
        commune="Quilicura",
        region="Región Metropolitana",
        latitude=-33.360101,
        longitude=-70.743221,
        starts_at=now - timedelta(days=2),
        ends_at=now - timedelta(days=1),
        status="published",
    )
    PublicPetOperation.objects.create(
        title="Borrador interno",
        slug="borrador-interno",
        operation_type="other",
        creator_type="private",
        creator_name="Fundación Aliada",
        address="Interno 789",
        commune="Santiago",
        region="Región Metropolitana",
        starts_at=now + timedelta(days=5),
        status="draft",
    )

    response = client.get("/api/v1/places/public-operations/")

    assert response.status_code == 200
    assert [item["slug"] for item in response.data["results"]] == [visible_operation.slug]
    assert response.data["results"][0]["creator_name"] == "Municipalidad de Quilicura"


@pytest.mark.django_db
def test_public_operations_list_supports_filters_and_include_expired():
    client = APIClient()
    now = timezone.now()

    PublicPetOperation.objects.create(
        title="Adopción Maipú",
        slug="adopcion-maipu",
        operation_type="adoption",
        creator_type="private",
        creator_name="Fundación Maipú Adopta",
        address="Plaza Maipú",
        commune="Maipú",
        region="Región Metropolitana",
        latitude=-33.510921,
        longitude=-70.760017,
        starts_at=now + timedelta(days=1),
        status="published",
    )
    expired_operation = PublicPetOperation.objects.create(
        title="Esterilización Maipú",
        slug="esterilizacion-maipu",
        operation_type="sterilization",
        creator_type="public",
        creator_name="Municipalidad de Maipú",
        address="Centro Comunitario",
        commune="Maipú",
        region="Región Metropolitana",
        latitude=-33.512911,
        longitude=-70.758201,
        starts_at=now - timedelta(days=3),
        ends_at=now - timedelta(days=2),
        status="expired",
    )

    response = client.get(
        "/api/v1/places/public-operations/",
        {
            "commune": "Maipú",
            "status": "expired",
            "include_expired": "true",
        },
    )

    assert response.status_code == 200
    assert [item["slug"] for item in response.data["results"]] == [expired_operation.slug]


@pytest.mark.django_db
def test_public_operations_list_supports_upcoming_filter():
    client = APIClient()
    now = timezone.now()

    PublicPetOperation.objects.create(
        title="Microchip futuro",
        slug="microchip-futuro",
        operation_type="microchip",
        creator_type="public",
        creator_name="Municipalidad de Santiago",
        address="Av. Futuro 100",
        commune="Santiago",
        region="Región Metropolitana",
        latitude=-33.448610,
        longitude=-70.669265,
        starts_at=now + timedelta(hours=3),
        status="published",
    )
    PublicPetOperation.objects.create(
        title="Microchip pasado",
        slug="microchip-pasado",
        operation_type="microchip",
        creator_type="public",
        creator_name="Municipalidad de Santiago",
        address="Av. Pasado 200",
        commune="Santiago",
        region="Región Metropolitana",
        latitude=-33.446991,
        longitude=-70.668101,
        starts_at=now - timedelta(hours=3),
        ends_at=now + timedelta(hours=1),
        status="published",
    )

    response = client.get(
        "/api/v1/places/public-operations/",
        {
            "operation_type": "microchip",
            "upcoming": "true",
        },
    )

    assert response.status_code == 200
    assert [item["slug"] for item in response.data["results"]] == ["microchip-futuro"]


@pytest.mark.django_db
def test_public_operations_detail_hides_expired_by_default_but_can_include_them():
    client = APIClient()
    now = timezone.now()
    operation = PublicPetOperation.objects.create(
        title="Operativo histórico",
        slug="operativo-historico",
        operation_type="other",
        creator_type="private",
        creator_name="Fundación Archivo",
        address="Archivo 123",
        commune="Santiago",
        region="Región Metropolitana",
        latitude=-33.450001,
        longitude=-70.667111,
        starts_at=now - timedelta(days=2),
        ends_at=now - timedelta(days=1),
        status="expired",
    )

    hidden_response = client.get(f"/api/v1/places/public-operations/{operation.slug}/")
    visible_response = client.get(
        f"/api/v1/places/public-operations/{operation.slug}/",
        {"include_expired": "true"},
    )

    assert hidden_response.status_code == 404
    assert visible_response.status_code == 200
    assert visible_response.data["slug"] == operation.slug


@pytest.mark.django_db
def test_public_operation_visibility_properties_and_expire_command():
    now = timezone.now()
    published_future = PublicPetOperation.objects.create(
        title="Vacunación futura",
        slug="vacunacion-futura",
        operation_type="vaccination",
        creator_type="public",
        creator_name="Municipalidad de Providencia",
        address="Futuro 1",
        commune="Providencia",
        region="Región Metropolitana",
        latitude=-33.427812,
        longitude=-70.615443,
        starts_at=now + timedelta(days=1),
        status="published",
    )
    published_past = PublicPetOperation.objects.create(
        title="Vacunación pasada",
        slug="vacunacion-pasada",
        operation_type="vaccination",
        creator_type="public",
        creator_name="Municipalidad de Providencia",
        address="Pasada 1",
        commune="Providencia",
        region="Región Metropolitana",
        latitude=-33.429010,
        longitude=-70.613920,
        starts_at=now - timedelta(days=3),
        status="published",
    )

    assert published_future.is_publicly_visible is True
    assert published_future.is_expired is False
    assert published_past.is_publicly_visible is False
    assert published_past.is_expired is True

    stdout = StringIO()
    call_command("expire_public_pet_operations", stdout=stdout)

    published_past.refresh_from_db()
    published_future.refresh_from_db()
    assert published_past.status == "expired"
    assert published_future.status == "published"
    assert "Se expiraron 1 operativos públicos." in stdout.getvalue()


@pytest.mark.django_db
def test_public_operation_requires_matching_region_commune_and_coordinates_when_published():
    with pytest.raises(ValidationError):
        PublicPetOperation.objects.create(
            title="Operativo inválido",
            slug="operativo-invalido",
            operation_type="other",
            creator_type="public",
            creator_name="Municipalidad inválida",
            address="Sin coordenadas",
            commune="Providencia",
            region="Valparaíso",
            starts_at=timezone.now() + timedelta(days=1),
            status="published",
        )
