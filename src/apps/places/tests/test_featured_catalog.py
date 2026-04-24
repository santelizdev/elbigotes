import pytest
from django.core.exceptions import ValidationError

from apps.places.models import FeaturedCatalogItem, Place, PlaceFeaturedCatalogItem
from apps.taxonomy.models import Category


@pytest.mark.django_db
def test_place_featured_catalog_item_requires_matching_category():
    matching_category = Category.objects.create(name="Veterinarias", slug="veterinarias")
    other_category = Category.objects.create(name="Guarderías", slug="guarderias")
    place = Place.objects.create(
        name="Vet Centro",
        slug="vet-centro",
        category=matching_category,
        commune="Santiago",
        region="Región Metropolitana",
        formatted_address="Santiago, Región Metropolitana, Chile",
        summary="Atención general",
    )
    featured_item = FeaturedCatalogItem.objects.create(
        title="Plan dental",
        slug="plan-dental",
        description="Servicio especializado",
        item_type="service",
        category=other_category,
    )

    with pytest.raises(ValidationError) as exc_info:
        PlaceFeaturedCatalogItem.objects.create(
            place=place,
            featured_item=featured_item,
        )

    assert "featured_item" in exc_info.value.message_dict
