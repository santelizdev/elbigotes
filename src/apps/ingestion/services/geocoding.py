import json
from dataclasses import dataclass
from typing import Protocol
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from django.conf import settings
from django.contrib.gis.geos import Point

from apps.ingestion.models import GeocodingLog, GeocodingStatus


@dataclass
class GeocodingCandidate:
    latitude: float
    longitude: float
    display_name: str
    raw: dict


class Geocoder(Protocol):
    provider_name: str

    def geocode(self, query: str) -> GeocodingCandidate | None: ...


class NominatimGeocoder:
    provider_name = "nominatim"

    def geocode(self, query: str) -> GeocodingCandidate | None:
        params = urlencode(
            {
                "format": "jsonv2",
                "limit": 1,
                "countrycodes": "cl",
                "q": query,
            }
        )
        request = Request(
            f"https://nominatim.openstreetmap.org/search?{params}",
            headers={"User-Agent": settings.GEOCODING_USER_AGENT},
        )

        with urlopen(request, timeout=settings.GEOCODING_TIMEOUT) as response:
            payload = json.loads(response.read().decode("utf-8"))

        if not payload:
            return None

        candidate = payload[0]
        return GeocodingCandidate(
            latitude=float(candidate["lat"]),
            longitude=float(candidate["lon"]),
            display_name=candidate.get("display_name", query),
            raw=candidate,
        )


def build_geocoder() -> Geocoder:
    if settings.GEOCODING_PROVIDER == "nominatim":
        return NominatimGeocoder()
    raise ValueError(f"Proveedor de geocodificación no soportado: {settings.GEOCODING_PROVIDER}")


def geocode_place_instance(place, *, triggered_by=None):
    geocoder = build_geocoder()
    query = place.geocoding_query

    if not query:
        return GeocodingLog.objects.create(
            place=place,
            provider=geocoder.provider_name,
            query="",
            status=GeocodingStatus.FAILED,
            error_message="El lugar no tiene una dirección suficiente para geocodificar.",
            triggered_by=triggered_by,
        )

    try:
        candidate = geocoder.geocode(query)
    except Exception as exc:  # noqa: BLE001
        return GeocodingLog.objects.create(
            place=place,
            provider=geocoder.provider_name,
            query=query,
            status=GeocodingStatus.FAILED,
            error_message=str(exc),
            triggered_by=triggered_by,
        )

    if not candidate:
        return GeocodingLog.objects.create(
            place=place,
            provider=geocoder.provider_name,
            query=query,
            status=GeocodingStatus.FAILED,
            error_message="No se encontró una coincidencia para la dirección.",
            triggered_by=triggered_by,
        )

    place.location = Point(candidate.longitude, candidate.latitude, srid=4326)
    if not place.formatted_address:
        place.formatted_address = candidate.display_name
    place.save(update_fields=["location", "formatted_address", "updated_at"])

    return GeocodingLog.objects.create(
        place=place,
        provider=geocoder.provider_name,
        query=query,
        status=GeocodingStatus.SUCCEEDED,
        matched_address=candidate.display_name,
        latitude=candidate.latitude,
        longitude=candidate.longitude,
        raw_response=candidate.raw,
        triggered_by=triggered_by,
    )

