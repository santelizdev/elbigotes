from __future__ import annotations

from datetime import timedelta
from decimal import Decimal, InvalidOperation

from django.db.models import Count
from django.db.models.functions import TruncDate, TruncHour
from django.utils import timezone

from apps.analytics.models import AnalyticsDeviceType, PlaceViewEvent, SearchEvent
from apps.places.services.verification import (
    PLACE_EFFECTIVE_VERIFICATION_PREMIUM,
    get_place_effective_verification_status,
)


PHONE_USER_AGENT_MARKERS = ("iphone", "android", "mobile", "windows phone")
TABLET_USER_AGENT_MARKERS = ("ipad", "tablet")


def detect_device_type(user_agent: str) -> str:
    normalized = (user_agent or "").lower()
    if any(marker in normalized for marker in TABLET_USER_AGENT_MARKERS):
        return AnalyticsDeviceType.TABLET
    if any(marker in normalized for marker in PHONE_USER_AGENT_MARKERS):
        return AnalyticsDeviceType.PHONE
    if normalized:
        return AnalyticsDeviceType.PC
    return AnalyticsDeviceType.UNKNOWN


def _to_decimal(value):
    if value in (None, ""):
        return None
    try:
        return Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        return None


def record_search_event(*, user=None, user_agent: str = "", payload: dict) -> SearchEvent:
    return SearchEvent.objects.create(
        user=user if getattr(user, "is_authenticated", False) else None,
        category_slug=(payload.get("category_slug") or "")[:120],
        search_term=(payload.get("search_term") or "")[:160],
        region=(payload.get("region") or "")[:120],
        commune=(payload.get("commune") or "")[:120],
        has_user_location=bool(payload.get("has_user_location")),
        user_latitude=_to_decimal(payload.get("user_latitude")),
        user_longitude=_to_decimal(payload.get("user_longitude")),
        radius_km=payload.get("radius_km") or None,
        verified_only=bool(payload.get("verified_only")),
        result_count=max(int(payload.get("result_count") or 0), 0),
        is_registered=bool(getattr(user, "is_authenticated", False)),
        device_type=detect_device_type(user_agent),
        path=(payload.get("path") or "")[:255],
        user_agent=user_agent[:1000],
    )


def record_place_view_event(*, user=None, user_agent: str = "", place, payload: dict) -> PlaceViewEvent:
    return PlaceViewEvent.objects.create(
        user=user if getattr(user, "is_authenticated", False) else None,
        place=place,
        category_slug=place.category.slug if place.category_id else "",
        region=place.region[:120],
        commune=place.commune[:120],
        verification_status=(payload.get("verification_status") or "")[:40],
        is_registered=bool(getattr(user, "is_authenticated", False)),
        device_type=detect_device_type(user_agent),
        path=(payload.get("path") or "")[:255],
        user_agent=user_agent[:1000],
    )


def build_kpi_overview(*, days: int = 7) -> dict:
    days = max(1, min(days, 90))
    since = timezone.now() - timedelta(days=days)

    searches = SearchEvent.objects.filter(created_at__gte=since)
    place_views = PlaceViewEvent.objects.filter(created_at__gte=since)

    searches_by_day = list(
        searches.annotate(bucket=TruncDate("created_at"))
        .values("bucket")
        .annotate(total=Count("id"))
        .order_by("bucket")
    )
    searches_by_hour = list(
        searches.annotate(bucket=TruncHour("created_at"))
        .values("bucket")
        .annotate(total=Count("id"))
        .order_by("bucket")
    )
    top_categories = list(
        searches.exclude(category_slug="")
        .values("category_slug")
        .annotate(total=Count("id"))
        .order_by("-total", "category_slug")[:10]
    )
    top_regions = list(
        searches.exclude(region="")
        .values("region")
        .annotate(total=Count("id"))
        .order_by("-total", "region")[:10]
    )
    top_communes = list(
        searches.exclude(commune="")
        .values("commune")
        .annotate(total=Count("id"))
        .order_by("-total", "commune")[:10]
    )
    place_views_top = list(
        place_views.values("place__slug", "place__name")
        .annotate(total=Count("id"))
        .order_by("-total", "place__name")[:10]
    )

    from apps.places.models import Place

    verified_businesses = Place.objects.filter(verification_status="verified", status="active").count()
    claim_requested_businesses = Place.objects.filter(
        verification_status="claim_requested",
        status="active",
    ).count()
    premium_verified_businesses = sum(
        1
        for place in Place.objects.filter(status="active")
        if get_place_effective_verification_status(place) == PLACE_EFFECTIVE_VERIFICATION_PREMIUM
    )

    return {
        "window_days": days,
        "searches_total": searches.count(),
        "place_views_total": place_views.count(),
        "searches_registered_total": searches.filter(is_registered=True).count(),
        "searches_anonymous_total": searches.filter(is_registered=False).count(),
        "searches_phone_total": searches.filter(device_type=AnalyticsDeviceType.PHONE).count(),
        "searches_pc_total": searches.filter(device_type=AnalyticsDeviceType.PC).count(),
        "verified_businesses_total": verified_businesses,
        "claim_requested_businesses_total": claim_requested_businesses,
        "premium_verified_businesses_total": premium_verified_businesses,
        "searches_by_day": [
            {"date": item["bucket"].isoformat(), "total": item["total"]}
            for item in searches_by_day
            if item["bucket"] is not None
        ],
        "searches_by_hour": [
            {"hour": item["bucket"].isoformat(), "total": item["total"]}
            for item in searches_by_hour
            if item["bucket"] is not None
        ],
        "top_categories": [
            {"category_slug": item["category_slug"], "total": item["total"]}
            for item in top_categories
        ],
        "top_regions": [{"region": item["region"], "total": item["total"]} for item in top_regions],
        "top_communes": [
            {"commune": item["commune"], "total": item["total"]}
            for item in top_communes
        ],
        "top_viewed_places": [
            {"slug": item["place__slug"], "name": item["place__name"], "total": item["total"]}
            for item in place_views_top
        ],
    }
