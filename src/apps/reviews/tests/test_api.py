import pytest
from rest_framework.test import APIClient

from apps.ingestion.models import Source
from apps.places.models import Place
from apps.reviews.models import PlaceReview, ReviewStatus
from apps.taxonomy.models import Category


@pytest.mark.django_db
def test_reviews_list_only_returns_published_reviews():
    client = APIClient()
    source = Source.objects.create(name="Seed Manual", slug="seed-manual")
    category = Category.objects.create(name="Veterinarias", slug="veterinarias")
    place = Place.objects.create(
        name="Vet Centro",
        slug="vet-centro",
        category=category,
        source=source,
        status="active",
        summary="Atención general",
        formatted_address="Santiago, Región Metropolitana, Chile",
    )
    PlaceReview.objects.create(
        place=place,
        reviewer_name="Ana",
        reviewer_email="ana@example.com",
        rating=5,
        title="Excelente",
        body="Muy buena atención",
        status=ReviewStatus.PUBLISHED,
    )
    PlaceReview.objects.create(
        place=place,
        reviewer_name="Luis",
        reviewer_email="luis@example.com",
        rating=3,
        title="Pendiente",
        body="A la espera",
        status=ReviewStatus.PENDING,
    )

    response = client.get("/api/v1/reviews/")

    assert response.status_code == 200
    assert response.data["count"] == 1
    assert response.data["results"][0]["reviewer_name"] == "Ana"


@pytest.mark.django_db
def test_reviews_create_creates_pending_review_for_active_place():
    client = APIClient()
    source = Source.objects.create(name="Seed Manual", slug="seed-manual")
    category = Category.objects.create(name="Guarderías", slug="guarderias")
    place = Place.objects.create(
        name="Guardería Centro",
        slug="guarderia-centro",
        category=category,
        source=source,
        status="active",
        summary="Cuidado diario",
        formatted_address="Santiago, Región Metropolitana, Chile",
    )

    response = client.post(
        "/api/v1/reviews/",
        data={
            "place_slug": place.slug,
            "reviewer_name": "Camila",
            "reviewer_email": "camila@example.com",
            "rating": 4,
            "title": "Buen servicio",
            "body": "Mi experiencia fue positiva.",
            "is_verified_visit": True,
        },
        format="json",
    )

    assert response.status_code == 201
    review = PlaceReview.objects.get(place=place, reviewer_email="camila@example.com")
    assert review.status == ReviewStatus.PENDING
    assert review.rating == 4
