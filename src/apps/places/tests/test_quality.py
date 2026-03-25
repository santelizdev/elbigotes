import pytest

from apps.ingestion.models import Source
from apps.places.models import Place, PlaceQualityIssue
from apps.places.services.quality import audit_single_place
from apps.taxonomy.models import Category


@pytest.mark.django_db
def test_audit_single_place_flags_verified_place_without_contact():
    source = Source.objects.create(name="Manual", slug="manual")
    category = Category.objects.create(name="Veterinarias", slug="veterinarias")
    place = Place.objects.create(
        name="Veterinaria Sin Contacto",
        category=category,
        source=source,
        is_verified=True,
        formatted_address="Providencia, Santiago, Chile",
        summary="Atención general",
    )

    findings = audit_single_place(place)

    assert any(finding.code == "verified_without_contact" for finding in findings)
    assert PlaceQualityIssue.objects.filter(place=place, code="verified_without_contact").exists()
    place.refresh_from_db()
    assert place.quality_score < 100

