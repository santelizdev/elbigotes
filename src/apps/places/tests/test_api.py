import pytest
from django.contrib.gis.geos import Point
from rest_framework.test import APIClient

from apps.ingestion.models import Source
from apps.places.models import Place
from apps.taxonomy.models import Category


@pytest.mark.django_db
def test_places_list_returns_only_active_places_and_supports_commune_and_verified_filters():
    client = APIClient()
    source = Source.objects.create(name="Seed Manual", slug="seed-manual")
    category = Category.objects.create(name="Veterinarias", slug="veterinarias")

    Place.objects.create(
        name="Vet Providencia",
        slug="vet-providencia",
        category=category,
        source=source,
        status="active",
        is_verified=True,
        commune="Providencia",
        region="Región Metropolitana",
        formatted_address="Providencia, Región Metropolitana, Chile",
        summary="Atención general",
    )
    Place.objects.create(
        name="Vet Santiago",
        slug="vet-santiago",
        category=category,
        source=source,
        status="active",
        is_verified=False,
        commune="Santiago",
        region="Región Metropolitana",
        formatted_address="Santiago, Región Metropolitana, Chile",
        summary="Atención general",
    )
    Place.objects.create(
        name="Vet Draft",
        slug="vet-draft",
        category=category,
        source=source,
        status="draft",
        commune="Providencia",
        region="Región Metropolitana",
        formatted_address="Providencia, Región Metropolitana, Chile",
        summary="No debería verse",
    )

    response = client.get(
        "/api/v1/places/",
        {
            "commune": "providencia",
            "verified_only": "true",
        },
    )

    assert response.status_code == 200
    assert response.data["count"] == 1
    assert response.data["results"][0]["slug"] == "vet-providencia"


@pytest.mark.django_db
def test_places_list_supports_radius_queries_and_distance_annotations():
    client = APIClient()
    source = Source.objects.create(name="Seed Manual", slug="seed-manual")
    category = Category.objects.create(name="Parques", slug="parques-pet-friendly")

    Place.objects.create(
        name="Parque Cerca",
        slug="parque-cerca",
        category=category,
        source=source,
        status="active",
        commune="Providencia",
        region="Región Metropolitana",
        formatted_address="Providencia, Región Metropolitana, Chile",
        summary="A poca distancia",
        location=Point(-70.6175, -33.4257, srid=4326),
    )
    Place.objects.create(
        name="Parque Lejos",
        slug="parque-lejos",
        category=category,
        source=source,
        status="active",
        commune="Maipú",
        region="Región Metropolitana",
        formatted_address="Maipú, Región Metropolitana, Chile",
        summary="Más lejano",
        location=Point(-70.7611, -33.5124, srid=4326),
    )

    response = client.get(
        "/api/v1/places/",
        {
            "lat": "-33.4257",
            "lng": "-70.6175",
            "radius_km": "5",
        },
    )

    assert response.status_code == 200
    assert response.data["count"] == 1
    assert response.data["results"][0]["slug"] == "parque-cerca"
    assert response.data["results"][0]["distance_km"] == 0.0


@pytest.mark.django_db
def test_place_detail_returns_public_metadata_and_source():
    client = APIClient()
    source = Source.objects.create(name="Seed Manual", slug="seed-manual")
    category = Category.objects.create(name="Guarderías", slug="guarderias")
    place = Place.objects.create(
        name="Guardería Centro",
        slug="guarderia-centro",
        category=category,
        source=source,
        status="active",
        commune="Santiago",
        region="Región Metropolitana",
        formatted_address="Santiago, Región Metropolitana, Chile",
        summary="Cuidado diario",
        description="Detalle operativo de la guardería.",
        metadata={"review_status": "ready"},
    )

    response = client.get(f"/api/v1/places/{place.slug}/")

    assert response.status_code == 200
    assert response.data["slug"] == "guarderia-centro"
    assert response.data["source"] == "seed-manual"
    assert response.data["metadata"]["review_status"] == "ready"
