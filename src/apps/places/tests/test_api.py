import pytest
from django.contrib.gis.geos import Point
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from django.utils import timezone
from rest_framework.test import APIClient

from apps.accounts.models import BusinessKind, BusinessProfile, User, UserRole
from apps.ingestion.models import Source
from apps.memberships.models import MembershipAssignment, MembershipAssignmentStatus, MembershipPlan
from apps.places.models import FeaturedCatalogItem, Place, PlaceFeaturedCatalogItem
from apps.taxonomy.models import Category


@pytest.mark.django_db
def test_places_list_returns_only_active_places_and_supports_commune_and_verified_filters():
    client = APIClient()
    source = Source.objects.create(name="Seed Manual", slug="seed-manual")
    category = Category.objects.create(name="Veterinarias", slug="veterinarias")

    Place.objects.create(
        name="Vet Providencia",
        slug="vet-providencia",
        category=category,
        source=source,
        status="active",
        is_verified=True,
        commune="Providencia",
        region="Región Metropolitana",
        formatted_address="Providencia, Región Metropolitana, Chile",
        summary="Atención general",
    )
    Place.objects.create(
        name="Vet Santiago",
        slug="vet-santiago",
        category=category,
        source=source,
        status="active",
        is_verified=False,
        commune="Santiago",
        region="Región Metropolitana",
        formatted_address="Santiago, Región Metropolitana, Chile",
        summary="Atención general",
    )
    Place.objects.create(
        name="Vet Draft",
        slug="vet-draft",
        category=category,
        source=source,
        status="draft",
        commune="Providencia",
        region="Región Metropolitana",
        formatted_address="Providencia, Región Metropolitana, Chile",
        summary="No debería verse",
    )

    response = client.get(
        "/api/v1/places/",
        {
            "commune": "providencia",
            "verified_only": "true",
        },
    )

    assert response.status_code == 200
    assert response.data["count"] == 1
    assert response.data["results"][0]["slug"] == "vet-providencia"


@pytest.mark.django_db
def test_places_list_supports_region_filter_with_partial_region_names():
    client = APIClient()
    source = Source.objects.create(name="Seed Manual", slug="seed-manual")
    category = Category.objects.create(name="Veterinarias", slug="veterinarias")

    Place.objects.create(
        name="Vet Serena",
        slug="vet-serena",
        category=category,
        source=source,
        status="active",
        commune="La Serena",
        region="Región de Coquimbo",
        formatted_address="La Serena, Región de Coquimbo, Chile",
        summary="Atención general",
    )
    Place.objects.create(
        name="Vet Conce",
        slug="vet-conce",
        category=category,
        source=source,
        status="active",
        commune="Concepción",
        region="Región del Biobío",
        formatted_address="Concepción, Región del Biobío, Chile",
        summary="Atención general",
    )

    response = client.get(
        "/api/v1/places/",
        {
            "region": "Coquimbo",
        },
    )

    assert response.status_code == 200
    assert response.data["count"] == 1
    assert response.data["results"][0]["slug"] == "vet-serena"


@pytest.mark.django_db
def test_places_list_supports_radius_queries_and_distance_annotations():
    client = APIClient()
    source = Source.objects.create(name="Seed Manual", slug="seed-manual")
    category = Category.objects.create(name="Parques", slug="parques-pet-friendly")

    Place.objects.create(
        name="Parque Cerca",
        slug="parque-cerca",
        category=category,
        source=source,
        status="active",
        commune="Providencia",
        region="Región Metropolitana",
        formatted_address="Providencia, Región Metropolitana, Chile",
        summary="A poca distancia",
        location=Point(-70.6175, -33.4257, srid=4326),
    )
    Place.objects.create(
        name="Parque Lejos",
        slug="parque-lejos",
        category=category,
        source=source,
        status="active",
        commune="Maipú",
        region="Región Metropolitana",
        formatted_address="Maipú, Región Metropolitana, Chile",
        summary="Más lejano",
        location=Point(-70.7611, -33.5124, srid=4326),
    )

    response = client.get(
        "/api/v1/places/",
        {
            "lat": "-33.4257",
            "lng": "-70.6175",
            "radius_km": "5",
        },
    )

    assert response.status_code == 200
    assert response.data["count"] == 1
    assert response.data["results"][0]["slug"] == "parque-cerca"
    assert response.data["results"][0]["distance_km"] == 0.0


@pytest.mark.django_db
def test_place_detail_returns_public_metadata_and_source():
    client = APIClient()
    source = Source.objects.create(name="Seed Manual", slug="seed-manual")
    category = Category.objects.create(name="Guarderías", slug="guarderias")
    place = Place.objects.create(
        name="Guardería Centro",
        slug="guarderia-centro",
        category=category,
        source=source,
        status="active",
        commune="Santiago",
        region="Región Metropolitana",
        formatted_address="Santiago, Región Metropolitana, Chile",
        summary="Cuidado diario",
        description="Detalle operativo de la guardería.",
        metadata={"review_status": "ready"},
        google_rating="4.8",
        google_reviews_count=128,
    )

    response = client.get(f"/api/v1/places/{place.slug}/")

    assert response.status_code == 200
    assert response.data["slug"] == "guarderia-centro"
    assert response.data["source"] == "seed-manual"
    assert response.data["google_rating"] == 4.8
    assert response.data["google_reviews_count"] == 128
    assert response.data["metadata"]["review_status"] == "ready"
    assert response.data["verification_status"] == "unverified"
    assert response.data["is_premium_verified"] is False
    assert response.data["can_claim"] is True


@pytest.mark.django_db
def test_place_detail_returns_active_featured_items_sorted_with_final_labels(tmp_path):
    client = APIClient()
    with override_settings(MEDIA_ROOT=tmp_path):
        source = Source.objects.create(name="Seed Manual", slug="seed-manual")
        category = Category.objects.create(name="Veterinarias", slug="veterinarias")
        place = Place.objects.create(
            name="Vet Destacada",
            slug="vet-destacada",
            category=category,
            source=source,
            status="active",
            commune="Providencia",
            region="Región Metropolitana",
            formatted_address="Providencia, Región Metropolitana, Chile",
            summary="Servicios destacados",
        )
        promo_image = SimpleUploadedFile(
            "promo.gif",
            (
                b"GIF87a\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00"
                b"\xff\xff\xff!\xf9\x04\x01\x00\x00\x00\x00,\x00"
                b"\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;"
            ),
            content_type="image/gif",
        )
        first_item = FeaturedCatalogItem.objects.create(
            title="Baño premium",
            slug="bano-premium",
            description="Spa y baño completo.",
            item_type="service",
            category=category,
            price_label="Desde $18.990",
            cta_label="Reservar",
        )
        second_item = FeaturedCatalogItem.objects.create(
            title="Pack snack",
            slug="pack-snack",
            description="Snacks naturales para perros.",
            item_type="product",
            category=category,
            image=promo_image,
            price_label="Desde $7.990",
            cta_label="Comprar",
        )
        inactive_item = FeaturedCatalogItem.objects.create(
            title="Promo oculta",
            slug="promo-oculta",
            description="No debe salir en la API.",
            item_type="promo",
            category=category,
            is_active=False,
        )
        PlaceFeaturedCatalogItem.objects.create(
            place=place,
            featured_item=first_item,
            sort_order=2,
            is_active=True,
        )
        PlaceFeaturedCatalogItem.objects.create(
            place=place,
            featured_item=second_item,
            sort_order=1,
            custom_price_label="Oferta lanzamiento",
            custom_cta_url="https://elbigotes.cl/ofertas/pack-snack",
            is_active=True,
        )
        PlaceFeaturedCatalogItem.objects.create(
            place=place,
            featured_item=inactive_item,
            sort_order=0,
            is_active=True,
        )

        response = client.get(f"/api/v1/places/{place.slug}/")

    assert response.status_code == 200
    assert [item["title"] for item in response.data["featured_items"]] == [
        "Pack snack",
        "Baño premium",
    ]
    assert response.data["featured_items"][0]["price_label"] == "Oferta lanzamiento"
    assert response.data["featured_items"][0]["cta_label"] == "Comprar"
    assert (
        response.data["featured_items"][0]["cta_url"]
        == "https://elbigotes.cl/ofertas/pack-snack"
    )
    assert response.data["featured_items"][0]["image_url"].endswith(".gif")
    assert response.data["featured_items"][1]["price_label"] == "Desde $18.990"
    assert response.data["featured_items"][1]["cta_url"] is None
    assert response.data["featured_items"][1]["image_url"] is None


@pytest.mark.django_db
def test_places_list_returns_google_reputation_fields_from_model_or_metadata_fallback():
    client = APIClient()
    source = Source.objects.create(name="Google Places", slug="google-places")
    category = Category.objects.create(name="Veterinarias", slug="veterinarias")

    Place.objects.create(
        name="Vet Modelo",
        slug="vet-modelo",
        category=category,
        source=source,
        status="active",
        commune="Providencia",
        region="Región Metropolitana",
        formatted_address="Providencia, Región Metropolitana, Chile",
        summary="Con reputación persistida",
        google_rating="4.7",
        google_reviews_count=84,
    )
    Place.objects.create(
        name="Vet Metadata",
        slug="vet-metadata",
        category=category,
        source=source,
        status="active",
        commune="Santiago",
        region="Región Metropolitana",
        formatted_address="Santiago, Región Metropolitana, Chile",
        summary="Con reputación histórica",
        metadata={"google_rating": 4.4, "google_total_ratings": 21},
    )

    response = client.get("/api/v1/places/")

    assert response.status_code == 200
    payload = {item["slug"]: item for item in response.data["results"]}
    assert payload["vet-modelo"]["google_rating"] == 4.7
    assert payload["vet-modelo"]["google_reviews_count"] == 84
    assert payload["vet-metadata"]["google_rating"] == 4.4
    assert payload["vet-metadata"]["google_reviews_count"] == 21


@pytest.mark.django_db
def test_places_list_returns_claim_requested_and_verified_premium_statuses():
    client = APIClient()
    source = Source.objects.create(name="Google Places", slug="google-places")
    category = Category.objects.create(name="Veterinarias", slug="veterinarias")
    owner_user = User.objects.create_user(
        email="premium@example.com",
        password="Password123!",
        role=UserRole.BUSINESS_OWNER,
    )
    owner_profile = BusinessProfile.objects.create(
        user=owner_user,
        business_name="Premium Vet",
        business_kind=BusinessKind.VETERINARY,
        phone="+56911112222",
        commune="Providencia",
        region="Región Metropolitana",
    )
    premium_plan = MembershipPlan.objects.create(
        name="Business Premium",
        slug="business-premium-test",
        audience="business",
        billing_interval="monthly",
        price_amount=19990,
        metadata={"lifecycle": "business_paid"},
    )
    MembershipAssignment.objects.create(
        plan=premium_plan,
        owner=owner_profile,
        status=MembershipAssignmentStatus.ACTIVE,
        starts_at=timezone.now(),
        renews_at=timezone.now(),
    )
    Place.objects.create(
        name="Vet Premium",
        slug="vet-premium",
        category=category,
        source=source,
        status="active",
        owner_business_profile=owner_profile,
        verification_status="verified",
        summary="Con membresía premium",
        commune="Providencia",
        region="Región Metropolitana",
        formatted_address="Providencia, Región Metropolitana, Chile",
    )
    Place.objects.create(
        name="Vet Reclamada",
        slug="vet-reclamada",
        category=category,
        source=source,
        status="active",
        verification_status="claim_requested",
        summary="Con solicitud en revisión",
        commune="Santiago",
        region="Región Metropolitana",
        formatted_address="Santiago, Región Metropolitana, Chile",
    )

    response = client.get("/api/v1/places/")

    assert response.status_code == 200
    payload = {item["slug"]: item for item in response.data["results"]}
    assert payload["vet-premium"]["verification_status"] == "verified_premium"
    assert payload["vet-premium"]["is_premium_verified"] is True
    assert payload["vet-premium"]["is_verified"] is True
    assert payload["vet-premium"]["can_claim"] is False
    assert payload["vet-reclamada"]["verification_status"] == "claim_requested"
    assert payload["vet-reclamada"]["is_premium_verified"] is False
    assert payload["vet-reclamada"]["is_verified"] is False
    assert payload["vet-reclamada"]["can_claim"] is False
