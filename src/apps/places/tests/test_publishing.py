import pytest
from django.contrib.gis.geos import Point

from apps.ingestion.models import Source
from apps.places.models import Place
from apps.places.services.publishing import get_publishable_places, publish_ready_places
from apps.taxonomy.models import Category


@pytest.mark.django_db
def test_publish_ready_places_only_activates_ready_places_with_location():
    source = Source.objects.create(name="Seed Manual", slug="seed-manual")
    category = Category.objects.create(name="Veterinarias", slug="veterinarias")
    point = Point(-70.6175, -33.4257, srid=4326)

    ready_place = Place.objects.create(
        name="Vet Lista",
        slug="vet-lista",
        category=category,
        source=source,
        status="draft",
        summary="Lista para publicar",
        formatted_address="Providencia, Región Metropolitana, Chile",
        commune="Providencia",
        region="Región Metropolitana",
        location=point,
        metadata={"review_status": "ready"},
    )
    Place.objects.create(
        name="Vet Pendiente",
        slug="vet-pendiente",
        category=category,
        source=source,
        status="draft",
        summary="Pendiente",
        formatted_address="Santiago, Región Metropolitana, Chile",
        commune="Santiago",
        region="Región Metropolitana",
        location=point,
        metadata={"review_status": "pending"},
    )

    assert get_publishable_places().count() == 1
    assert publish_ready_places() == 1

    ready_place.refresh_from_db()
    assert ready_place.status == "active"


@pytest.mark.django_db
def test_publish_ready_places_can_include_address_only_records():
    source = Source.objects.create(name="Seed Manual", slug="seed-manual")
    category = Category.objects.create(name="Refugios", slug="refugios-albergues")

    address_only = Place.objects.create(
        name="Refugio Publicable",
        slug="refugio-publicable",
        category=category,
        source=source,
        status="draft",
        summary="Con dirección y datos básicos",
        formatted_address="Ñuñoa, Región Metropolitana, Chile",
        commune="Ñuñoa",
        region="Región Metropolitana",
        metadata={"review_status": "pending"},
    )

    assert get_publishable_places().count() == 0
    assert get_publishable_places(include_address_only=True).count() == 1
    assert publish_ready_places(include_address_only=True) == 1

    address_only.refresh_from_db()
    assert address_only.status == "active"


@pytest.mark.django_db
def test_publish_ready_places_can_scope_to_dataset_and_ignore_review_status():
    source = Source.objects.create(name="Google Places", slug="google-places")
    category = Category.objects.create(name="Veterinarias", slug="veterinarias")
    point = Point(-70.6175, -33.4257, srid=4326)

    imported_place = Place.objects.create(
        name="Veterinaria Importada",
        slug="veterinaria-importada",
        category=category,
        source=source,
        status="draft",
        summary="Lote Google validado",
        formatted_address="Providencia, Región Metropolitana, Chile",
        commune="Providencia",
        region="Región Metropolitana",
        location=point,
        metadata={"review_status": "pending", "imported_from": "rm-lanzamiento-v1"},
    )
    other_place = Place.objects.create(
        name="Veterinaria Otro Lote",
        slug="veterinaria-otro-lote",
        category=category,
        source=source,
        status="draft",
        summary="Otro dataset",
        formatted_address="Santiago, Región Metropolitana, Chile",
        commune="Santiago",
        region="Región Metropolitana",
        location=point,
        metadata={"review_status": "pending", "imported_from": "otro-lote"},
    )

    assert (
        get_publishable_places(
            dataset_slug="rm-lanzamiento-v1",
            ignore_review_status=True,
        ).count()
        == 1
    )
    assert (
        publish_ready_places(
            dataset_slug="rm-lanzamiento-v1",
            ignore_review_status=True,
        )
        == 1
    )

    imported_place.refresh_from_db()
    other_place.refresh_from_db()
    assert imported_place.status == "active"
    assert other_place.status == "draft"
