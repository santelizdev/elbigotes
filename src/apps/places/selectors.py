from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D
from django.db.models import Prefetch
from rest_framework.exceptions import ValidationError

from apps.places.choices import PlaceStatus
from apps.places.models import Place, PlaceFeaturedCatalogItem, PublicPetOperation


def build_place_queryset(params, *, include_featured_items=False):
    """
    Centraliza la lectura pública para que filtros geográficos y optimizaciones no vivan en la vista.
    """

    queryset = (
        Place.objects.select_related("category", "subcategory", "source", "owner_business_profile")
        .prefetch_related("contact_points", "claim_requests")
        .filter(status=PlaceStatus.ACTIVE)
    )

    if include_featured_items:
        queryset = queryset.prefetch_related(
            Prefetch(
                "featured_catalog_assignments",
                queryset=(
                    PlaceFeaturedCatalogItem.objects.select_related("featured_item")
                    .filter(is_active=True, featured_item__is_active=True)
                    .order_by("sort_order", "id")
                ),
                to_attr="prefetched_featured_catalog_assignments",
            )
        )

    lat = params.get("lat")
    lng = params.get("lng")
    radius_km = params.get("radius_km")

    if (lat and not lng) or (lng and not lat):
        raise ValidationError({"detail": "Los parámetros lat y lng deben enviarse juntos."})

    if not lat and not lng:
        return queryset

    try:
        point = Point(float(lng), float(lat), srid=4326)
    except (TypeError, ValueError) as exc:
        raise ValidationError({"detail": "Los parámetros lat y lng deben ser numéricos."}) from exc

    queryset = queryset.annotate(distance_m=Distance("location", point)).order_by("distance_m", "name")

    if radius_km:
        try:
            queryset = queryset.filter(location__distance_lte=(point, D(km=float(radius_km))))
        except (TypeError, ValueError) as exc:
            raise ValidationError({"detail": "El parámetro radius_km debe ser numérico."}) from exc

    return queryset


def build_public_pet_operation_queryset(*, include_expired=False):
    queryset = PublicPetOperation.objects.with_related()
    if include_expired:
        return queryset.non_draft()
    return queryset.publicly_visible()
