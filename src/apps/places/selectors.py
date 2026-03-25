from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D
from rest_framework.exceptions import ValidationError

from apps.places.choices import PlaceStatus
from apps.places.models import Place


def build_place_queryset(params):
    """
    Centraliza la lectura pública para que filtros geográficos y optimizaciones no vivan en la vista.
    """

    queryset = (
        Place.objects.select_related("category", "subcategory", "source")
        .prefetch_related("contact_points")
        .filter(status=PlaceStatus.ACTIVE)
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
