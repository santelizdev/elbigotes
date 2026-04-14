import pytest
from rest_framework.test import APIClient

from apps.accounts.models import User, UserRole
from apps.accounts.tokens import create_access_token
from apps.analytics.models import PlaceViewEvent, SearchEvent
from apps.ingestion.models import Source
from apps.memberships.models import MembershipAssignment, MembershipAssignmentStatus, MembershipPlan
from apps.places.models import Place
from apps.taxonomy.models import Category


@pytest.mark.django_db
def test_search_event_endpoint_records_anonymous_search_with_device_context():
    client = APIClient()

    response = client.post(
        "/api/v1/analytics/events/searches/",
        data={
            "category_slug": "veterinarias",
            "search_term": "urgencia",
            "region": "Región Metropolitana",
            "commune": "Providencia",
            "has_user_location": True,
            "user_latitude": "-33.425700",
            "user_longitude": "-70.617500",
            "radius_km": 5,
            "verified_only": True,
            "result_count": 12,
            "path": "/?category=veterinarias",
        },
        format="json",
        HTTP_USER_AGENT="Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X)",
    )

    assert response.status_code == 204
    event = SearchEvent.objects.get()
    assert event.category_slug == "veterinarias"
    assert event.is_registered is False
    assert event.device_type == "phone"
    assert event.result_count == 12


@pytest.mark.django_db
def test_place_view_event_endpoint_records_registered_user_visit():
    client = APIClient()
    user = User.objects.create_user(
        email="owner@example.com",
        password="Password123!",
        role=UserRole.BUSINESS_OWNER,
    )
    token = create_access_token(user)
    source = Source.objects.create(name="Seed Manual", slug="seed-manual")
    category = Category.objects.create(name="Veterinarias", slug="veterinarias")
    place = Place.objects.create(
        name="Vet Centro",
        slug="vet-centro",
        category=category,
        source=source,
        status="active",
        verification_status="verified",
        summary="Atención general",
        formatted_address="Santiago, Región Metropolitana, Chile",
        commune="Santiago",
        region="Región Metropolitana",
    )

    response = client.post(
        "/api/v1/analytics/events/place-views/",
        data={"place_slug": place.slug, "path": f"/lugares/{place.slug}"},
        format="json",
        HTTP_AUTHORIZATION=f"Bearer {token}",
        HTTP_USER_AGENT="Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0)",
    )

    assert response.status_code == 204
    event = PlaceViewEvent.objects.get()
    assert event.place == place
    assert event.is_registered is True
    assert event.device_type == "pc"
    assert event.verification_status == "verified"


@pytest.mark.django_db
def test_analytics_overview_requires_internal_user_and_returns_kpi_summary():
    client = APIClient()
    internal_user = User.objects.create_user(
        email="analyst@example.com",
        password="Password123!",
        role=UserRole.ANALYST,
    )
    token = create_access_token(internal_user)
    source = Source.objects.create(name="Seed Manual", slug="seed-manual")
    category = Category.objects.create(name="Veterinarias", slug="veterinarias")
    place = Place.objects.create(
        name="Vet Premium",
        slug="vet-premium",
        category=category,
        source=source,
        status="active",
        verification_status="verified",
        summary="Atención general",
        formatted_address="Providencia, Región Metropolitana, Chile",
        commune="Providencia",
        region="Región Metropolitana",
    )
    plan = MembershipPlan.objects.create(
        name="Premium KPI",
        slug="premium-kpi",
        audience="business",
        billing_interval="monthly",
        price_amount=9990,
        metadata={"lifecycle": "business_paid"},
    )
    # The place does not need an owner for the KPI endpoint to work; this search + view data
    # still exercises the overview aggregations and current verified counters.
    SearchEvent.objects.create(
        category_slug="veterinarias",
        region="Región Metropolitana",
        commune="Providencia",
        result_count=8,
        device_type="pc",
        is_registered=False,
    )
    PlaceViewEvent.objects.create(
        place=place,
        category_slug="veterinarias",
        region="Región Metropolitana",
        commune="Providencia",
        verification_status="verified",
        device_type="pc",
        is_registered=True,
    )
    MembershipAssignment.objects.none()
    del plan

    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    response = client.get("/api/v1/analytics/overview/?days=7")

    assert response.status_code == 200
    assert response.data["searches_total"] == 1
    assert response.data["place_views_total"] == 1
    assert response.data["verified_businesses_total"] == 1
    assert response.data["top_categories"][0]["category_slug"] == "veterinarias"


@pytest.mark.django_db
def test_analytics_overview_rejects_non_internal_users():
    client = APIClient()
    business_user = User.objects.create_user(
        email="biz@example.com",
        password="Password123!",
        role=UserRole.BUSINESS_OWNER,
    )
    token = create_access_token(business_user)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    response = client.get("/api/v1/analytics/overview/")

    assert response.status_code == 403
