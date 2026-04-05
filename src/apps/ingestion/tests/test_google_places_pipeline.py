import pytest
from django.core.management import call_command

from apps.ingestion.management.commands.geocode_places import is_too_generic
from apps.ingestion.management.commands.promote_places import (
    build_place_from_record,
    load_taxonomy,
)
from apps.ingestion.models import ImportedPlaceRecord, Source, SourceDataset
from apps.places.models import Place
from apps.taxonomy.models import Category, Subcategory


@pytest.mark.django_db
def test_build_place_from_record_skips_noisy_refugio_result():
    source = Source.objects.create(name="Google Places", slug="google-places", kind="api")
    dataset = SourceDataset.objects.create(source=source, name="RM", slug="rm-test")
    category = Category.objects.create(name="Refugios", slug="refugios-albergues", is_active=True)
    Subcategory.objects.create(category=category, name="Refugios", slug="refugios", is_active=True)

    record = ImportedPlaceRecord.objects.create(
        dataset=dataset,
        source=source,
        external_id="place-123",
        raw_name="Hotel de Mascotas Fonoguau",
        raw_address="Arica, Chile",
        raw_payload={
            "google": {
                "name": "Hotel de Mascotas Fonoguau",
                "formatted_address": "Arica, Chile",
                "geometry": {"location": {"lat": -18.4, "lng": -70.3}},
                "types": ["lodging", "point_of_interest"],
            },
            "meta": {
                "category_slug": "refugio",
                "commune_target": "Arica",
                "region_target": "Región de Arica y Parinacota",
                "search_keyword": "refugio de animales",
            },
        },
    )

    place, error = build_place_from_record(record, *load_taxonomy())

    assert place is None
    assert "refugio" in error


@pytest.mark.django_db
def test_build_place_from_record_accepts_veterinary_place_by_google_type():
    source = Source.objects.create(name="Google Places", slug="google-places", kind="api")
    dataset = SourceDataset.objects.create(source=source, name="RM", slug="rm-vet-test")
    category = Category.objects.create(name="Veterinarias", slug="veterinarias", is_active=True)
    Subcategory.objects.create(category=category, name="Consulta", slug="consulta", is_active=True)

    record = ImportedPlaceRecord.objects.create(
        dataset=dataset,
        source=source,
        external_id="place-456",
        raw_name="Centro Animal Norte",
        raw_address="Santiago, Chile",
        raw_payload={
            "google": {
                "name": "Centro Animal Norte",
                "formatted_address": "Santiago, Chile",
                "geometry": {"location": {"lat": -33.4, "lng": -70.6}},
                "types": ["veterinary_care", "point_of_interest"],
            },
            "meta": {
                "category_slug": "veterinaria",
                "commune_target": "Santiago",
                "region_target": "Región Metropolitana",
                "search_keyword": "veterinaria",
            },
        },
    )

    place, contact_points = build_place_from_record(record, *load_taxonomy())

    assert place is not None
    assert place.category.slug == "veterinarias"
    assert isinstance(contact_points, list)


def test_is_too_generic_only_blocks_placeholder_addresses():
    assert is_too_generic("Santiago Centro, Región Metropolitana, Chile") is True
    assert is_too_generic("Av. Providencia 1234, Providencia, Región Metropolitana, Chile") is False
    assert is_too_generic("Camino al Volcán 31087, San José de Maipo, Región Metropolitana, Chile") is False


@pytest.mark.django_db
def test_build_place_from_record_accepts_emergency_veterinary_place():
    source = Source.objects.create(name="Google Places", slug="google-places", kind="api")
    dataset = SourceDataset.objects.create(source=source, name="RM Emergencias", slug="rm-emergencias")
    category = Category.objects.create(
        name="Emergencias veterinarias 24/7",
        slug="emergencias-veterinarias",
        is_active=True,
    )
    Subcategory.objects.create(category=category, name="Urgencias", slug="urgencias", is_active=True)

    record = ImportedPlaceRecord.objects.create(
        dataset=dataset,
        source=source,
        external_id="place-emergency",
        raw_name="Hospital Veterinario 24 Horas Central",
        raw_address="Santiago, Chile",
        raw_payload={
            "google": {
                "name": "Hospital Veterinario 24 Horas Central",
                "formatted_address": "Santiago, Chile",
                "geometry": {"location": {"lat": -33.4, "lng": -70.6}},
                "types": ["veterinary_care", "point_of_interest"],
            },
            "meta": {
                "category_slug": "emergencia-veterinaria",
                "commune_target": "Santiago",
                "region_target": "Región Metropolitana",
                "search_keyword": "urgencia veterinaria",
            },
        },
    )

    place, _contact_points = build_place_from_record(record, *load_taxonomy())

    assert place is not None
    assert place.category.slug == "emergencias-veterinarias"
    assert place.is_emergency_service is True
    assert place.is_open_24_7 is True


@pytest.mark.django_db
def test_build_place_from_record_accepts_park_place():
    source = Source.objects.create(name="Google Places", slug="google-places", kind="api")
    dataset = SourceDataset.objects.create(source=source, name="RM Parques", slug="rm-parques")
    Category.objects.create(name="Parques pet friendly", slug="parques-pet-friendly", is_active=True)

    record = ImportedPlaceRecord.objects.create(
        dataset=dataset,
        source=source,
        external_id="place-park",
        raw_name="Parque Canino Apoquindo",
        raw_address="Las Condes, Chile",
        raw_payload={
            "google": {
                "name": "Parque Canino Apoquindo",
                "formatted_address": "Las Condes, Chile",
                "geometry": {"location": {"lat": -33.4, "lng": -70.5}},
                "types": ["park", "point_of_interest"],
            },
            "meta": {
                "category_slug": "parque",
                "commune_target": "Santiago",
                "region_target": "Región Metropolitana",
                "search_keyword": "parque canino",
            },
        },
    )

    place, _contact_points = build_place_from_record(record, *load_taxonomy())

    assert place is not None
    assert place.category.slug == "parques-pet-friendly"


@pytest.mark.django_db
def test_build_place_from_record_parses_commune_from_formatted_address_without_details():
    source = Source.objects.create(name="Google Places", slug="google-places", kind="api")
    dataset = SourceDataset.objects.create(source=source, name="Bio Bio", slug="bio-bio-vets")
    category = Category.objects.create(name="Veterinarias", slug="veterinarias", is_active=True)
    Subcategory.objects.create(category=category, name="Consulta", slug="consulta", is_active=True)

    record = ImportedPlaceRecord.objects.create(
        dataset=dataset,
        source=source,
        external_id="place-talcahuano",
        raw_name="Clínica Costa Animal",
        raw_address="Colón 2870, Talcahuano",
        raw_payload={
            "google": {
                "name": "Clínica Costa Animal",
                "formatted_address": "Colón 2870, Talcahuano",
                "geometry": {"location": {"lat": -36.72, "lng": -73.11}},
                "types": ["veterinary_care", "point_of_interest"],
                "address_components": [],
            },
            "meta": {
                "category_slug": "veterinaria",
                "commune_target": "Concepción",
                "region_target": "Región del Biobío",
                "search_keyword": "veterinaria",
            },
        },
    )

    place, _contact_points = build_place_from_record(record, *load_taxonomy())

    assert place is not None
    assert place.commune == "Talcahuano"
    assert place.region == "Región del Biobío"


@pytest.mark.django_db
def test_build_place_from_record_falls_back_to_target_commune_when_address_token_is_not_valid():
    source = Source.objects.create(name="Google Places", slug="google-places", kind="api")
    dataset = SourceDataset.objects.create(source=source, name="Coquimbo", slug="coquimbo-vets")
    category = Category.objects.create(name="Veterinarias", slug="veterinarias", is_active=True)
    Subcategory.objects.create(category=category, name="Consulta", slug="consulta", is_active=True)

    record = ImportedPlaceRecord.objects.create(
        dataset=dataset,
        source=source,
        external_id="place-la-serena-fallback",
        raw_name="Veterinaria Costera",
        raw_address="José Miguel Castillo, Región de Coquimbo, Chile",
        raw_payload={
            "google": {
                "name": "Veterinaria Costera",
                "formatted_address": "José Miguel Castillo, Región de Coquimbo, Chile",
                "geometry": {"location": {"lat": -29.9, "lng": -71.25}},
                "types": ["veterinary_care", "point_of_interest"],
                "address_components": [],
            },
            "meta": {
                "category_slug": "veterinaria",
                "commune_target": "La Serena",
                "region_target": "Región de Coquimbo",
                "search_keyword": "veterinaria",
            },
        },
    )

    place, _contact_points = build_place_from_record(record, *load_taxonomy())

    assert place is not None
    assert place.commune == "La Serena"
    assert place.region == "Región de Coquimbo"


@pytest.mark.django_db
def test_build_place_from_record_requires_coordinates_for_map_results():
    source = Source.objects.create(name="Google Places", slug="google-places", kind="api")
    dataset = SourceDataset.objects.create(source=source, name="RM", slug="rm-no-geo")
    category = Category.objects.create(name="Veterinarias", slug="veterinarias", is_active=True)
    Subcategory.objects.create(category=category, name="Consulta", slug="consulta", is_active=True)

    record = ImportedPlaceRecord.objects.create(
        dataset=dataset,
        source=source,
        external_id="place-no-geo",
        raw_name="Veterinaria Sin Coordenadas",
        raw_address="Providencia, Región Metropolitana, Chile",
        raw_payload={
            "google": {
                "name": "Veterinaria Sin Coordenadas",
                "formatted_address": "Providencia, Región Metropolitana, Chile",
                "geometry": {"location": {}},
                "types": ["veterinary_care", "point_of_interest"],
            },
            "meta": {
                "category_slug": "veterinaria",
                "commune_target": "Providencia",
                "region_target": "Región Metropolitana",
                "search_keyword": "veterinaria",
            },
        },
    )

    place, error = build_place_from_record(record, *load_taxonomy())

    assert place is None
    assert "coordenadas" in error


@pytest.mark.django_db
def test_promote_places_force_updates_existing_place_instead_of_recreating_it():
    source = Source.objects.create(name="Google Places", slug="google-places", kind="api")
    dataset = SourceDataset.objects.create(source=source, name="Bio Bio", slug="bio-bio-vets")
    category = Category.objects.create(name="Veterinarias", slug="veterinarias", is_active=True)
    Subcategory.objects.create(category=category, name="Consulta", slug="consulta", is_active=True)

    existing_place = Place.objects.create(
        name="Clínica Costa Animal",
        slug="clinica-costa-animal",
        category=category,
        source=source,
        status="active",
        commune="Concepción",
        region="Región del Biobío",
        formatted_address="Concepción, Región del Biobío, Chile",
        street_address="Concepción, Región del Biobío, Chile",
        summary="Atención general",
        metadata={"google_place_id": "place-talcahuano"},
    )

    record = ImportedPlaceRecord.objects.create(
        dataset=dataset,
        source=source,
        external_id="place-talcahuano",
        status="imported",
        imported_place=existing_place,
        raw_name="Clínica Costa Animal",
        raw_address="Colón 2870, Talcahuano",
        raw_payload={
            "google": {
                "name": "Clínica Costa Animal",
                "formatted_address": "Colón 2870, Talcahuano",
                "geometry": {"location": {"lat": -36.72, "lng": -73.11}},
                "types": ["veterinary_care", "point_of_interest"],
                "address_components": [],
            },
            "meta": {
                "category_slug": "veterinaria",
                "commune_target": "Concepción",
                "region_target": "Región del Biobío",
                "search_keyword": "veterinaria",
            },
        },
    )

    call_command("promote_places", dataset="bio-bio-vets", force=True)

    existing_place.refresh_from_db()
    record.refresh_from_db()

    assert Place.objects.count() == 1
    assert existing_place.id == record.imported_place_id
    assert existing_place.slug == "clinica-costa-animal"
    assert existing_place.status == "active"
    assert existing_place.commune == "Talcahuano"
    assert existing_place.formatted_address == "Colón 2870, Talcahuano"
