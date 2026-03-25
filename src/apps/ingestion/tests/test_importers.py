import pytest

from apps.ingestion.models import ImportedPlaceRecord, Source, SourceDataset
from apps.ingestion.services.importers import import_pet_places_from_csv, import_places_from_csv
from apps.places.models import Place, PlaceQualityIssue
from apps.taxonomy.models import Category, Subcategory


@pytest.mark.django_db
def test_import_places_from_csv_creates_place_and_import_record(tmp_path):
    Source.objects.create(name="CSV Manual", slug="csv-manual")
    category = Category.objects.create(name="Veterinarias", slug="veterinarias")
    Subcategory.objects.create(category=category, name="Consulta general", slug="consulta")

    csv_path = tmp_path / "places.csv"
    csv_path.write_text(
        "\n".join(
            [
                (
                    "external_id,name,summary,category,subcategory,formatted_address,commune,"
                    "region,country,latitude,longitude,phone,email,website,is_verified"
                ),
                (
                    "ext-001,Clínica Central,Atención general,veterinarias,consulta,"
                    "Santiago Centro,Santiago,Región Metropolitana,Chile,-33.45,-70.66,"
                    "+56911111111,info@example.com,https://example.com,true"
                ),
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    summary = import_places_from_csv(
        str(csv_path),
        source_slug="csv-manual",
        dataset_slug="primer-lote",
    )

    assert summary.created == 1
    assert ImportedPlaceRecord.objects.filter(external_id="ext-001").exists()
    imported_place = ImportedPlaceRecord.objects.get(external_id="ext-001").imported_place
    assert imported_place.name == "Clínica Central"
    assert imported_place.category.slug == "veterinarias"
    assert imported_place.contact_points.count() == 3


@pytest.mark.django_db
def test_import_pet_places_from_csv_creates_active_and_pending_review_places(tmp_path):
    Category.objects.create(name="Veterinarias", slug="veterinarias")
    Category.objects.create(name="Parques", slug="parques-pet-friendly")

    csv_path = tmp_path / "pet-places.csv"
    csv_path.write_text(
        "\n".join(
            [
                (
                    "country,region,commune,category,name,address,latitude,longitude,phone,"
                    "email,website,source,notes"
                ),
                (
                    "Chile,Región Metropolitana,Providencia,veterinarias,Clinica Providencia,"
                    "Av. Providencia 100,-33.4255,-70.6172,+56911111111,contacto@clinica.cl,"
                    "https://clinica.cl,manual_seed,Atención general"
                ),
                (
                    "Chile,Región Metropolitana,Las Condes,parques,Parque Canino Apoquindo,"
                    "Av. Apoquindo 4500,,,,,https://parque.cl,web_research,"
                    "Sin coordenadas por ahora"
                ),
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    summary = import_pet_places_from_csv(str(csv_path))

    assert summary.processed == 2
    assert summary.created == 2
    assert summary.geocoding_needed == 1

    clinic = Place.objects.get(name="Clinica Providencia")
    park = Place.objects.get(name="Parque Canino Apoquindo")

    assert clinic.status == "active"
    assert clinic.location is not None
    assert park.status == "draft"
    assert PlaceQualityIssue.objects.filter(place=park, code="missing_location").exists()
    assert ImportedPlaceRecord.objects.filter(imported_place=clinic, status="imported").exists()
    assert Source.objects.filter(slug="manual-seed").exists()
    assert Source.objects.filter(slug="web-research").exists()
    assert SourceDataset.objects.count() == 2


@pytest.mark.django_db
def test_import_pet_places_from_csv_skips_reasonable_duplicate_without_update(tmp_path):
    category = Category.objects.create(name="Refugios", slug="refugios-albergues")
    source = Source.objects.create(name="Manual Seed", slug="manual-seed")
    Place.objects.create(
        name="Refugio Centro",
        category=category,
        source=source,
        commune="Santiago",
        region="Región Metropolitana",
        formatted_address="Santiago Centro, Santiago, Chile",
        summary="Registro inicial",
    )

    csv_path = tmp_path / "duplicates.csv"
    csv_path.write_text(
        "\n".join(
            [
                (
                    "country,region,commune,category,name,address,latitude,longitude,phone,"
                    "email,website,source,notes"
                ),
                (
                    "Chile,Región Metropolitana,Santiago,refugios,Refugio Centro,"
                    "Santiago Centro,,,+56922222222,,https://refugio.cl,manual_seed,"
                    "No debería actualizar sin flag"
                ),
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    summary = import_pet_places_from_csv(str(csv_path))

    assert summary.processed == 1
    assert summary.ignored == 1
    assert ImportedPlaceRecord.objects.filter(status="skipped").exists()
