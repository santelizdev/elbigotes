import pytest
from django.contrib.gis.geos import Point

from apps.ingestion.models import Source
from apps.places.models import DuplicatePlaceCandidate, Place
from apps.places.services.duplicates import rebuild_duplicate_candidates
from apps.taxonomy.models import Category


@pytest.mark.django_db
def test_rebuild_duplicate_candidates_creates_match_for_similar_names():
    source = Source.objects.create(name="Manual", slug="manual")
    category = Category.objects.create(name="Veterinarias", slug="veterinarias")
    Place.objects.create(
        name="Clínica Vet Andes",
        category=category,
        source=source,
        commune="Ñuñoa",
        region="Región Metropolitana",
        location=Point(-70.6032, -33.4569, srid=4326),
    )
    Place.objects.create(
        name="Clinica Vet Andes",
        category=category,
        source=source,
        commune="Ñuñoa",
        region="Región Metropolitana",
        location=Point(-70.6031, -33.4568, srid=4326),
    )

    total = rebuild_duplicate_candidates()

    assert total == 1
    assert DuplicatePlaceCandidate.objects.count() == 1

