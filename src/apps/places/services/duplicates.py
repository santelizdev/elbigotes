from decimal import Decimal
from difflib import SequenceMatcher
from itertools import combinations
from math import asin, cos, radians, sin, sqrt

from apps.places.models import DuplicatePlaceCandidate, Place


def _normalize_name(value: str) -> str:
    return " ".join(value.lower().split())


def _haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    radius = 6371
    d_lat = radians(lat2 - lat1)
    d_lon = radians(lon2 - lon1)
    a = (
        sin(d_lat / 2) ** 2
        + cos(radians(lat1)) * cos(radians(lat2)) * sin(d_lon / 2) ** 2
    )
    return 2 * radius * asin(sqrt(a))


def _candidate_score(first: Place, second: Place) -> tuple[float, str] | None:
    similarity = SequenceMatcher(None, _normalize_name(first.name), _normalize_name(second.name)).ratio()

    if first.commune and second.commune and first.commune.lower() == second.commune.lower() and similarity >= 0.86:
        return similarity * 100, "Nombre muy similar en la misma comuna."

    if (
        first.location
        and second.location
        and first.category_id == second.category_id
        and similarity >= 0.8
        and _haversine_km(first.location.y, first.location.x, second.location.y, second.location.x) <= 0.5
    ):
        return similarity * 100, "Nombre similar y coordenadas cercanas en la misma categoría."

    return None


def rebuild_duplicate_candidates(queryset=None) -> int:
    queryset = list(queryset or Place.objects.all())
    created_or_updated = 0

    for first, second in combinations(queryset, 2):
        if first.id == second.id:
            continue

        score_payload = _candidate_score(first, second)
        if not score_payload:
            continue

        score, reason = score_payload
        ordered = sorted([first, second], key=lambda place: place.id)
        candidate, created = DuplicatePlaceCandidate.objects.update_or_create(
            primary_place=ordered[0],
            candidate_place=ordered[1],
            defaults={
                "similarity_score": Decimal(f"{score:.2f}"),
                "reason": reason,
            },
        )
        if created or candidate:
            created_or_updated += 1

    return created_or_updated

