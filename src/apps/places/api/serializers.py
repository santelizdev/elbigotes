from rest_framework import serializers

from apps.places.choices import PlaceVerificationStatus
from apps.places.models import ContactPoint, Place, PlaceFeaturedCatalogItem, PublicPetOperation
from apps.places.services.verification import (
    PLACE_EFFECTIVE_VERIFICATION_PREMIUM,
    get_place_effective_verification_status,
)


class ContactPointSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactPoint
        fields = ("label", "kind", "value", "notes", "is_primary")


class PlaceFeaturedCatalogItemSerializer(serializers.ModelSerializer):
    title = serializers.CharField(source="featured_item.title", read_only=True)
    description = serializers.CharField(source="featured_item.description", read_only=True)
    item_type = serializers.CharField(source="featured_item.item_type", read_only=True)
    price_label = serializers.SerializerMethodField()
    cta_label = serializers.CharField(source="featured_item.cta_label", read_only=True)
    cta_url = serializers.SerializerMethodField()
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = PlaceFeaturedCatalogItem
        fields = (
            "title",
            "description",
            "item_type",
            "price_label",
            "cta_label",
            "cta_url",
            "image_url",
        )

    def get_price_label(self, obj):
        return obj.effective_price_label or None

    def get_cta_url(self, obj):
        return obj.effective_cta_url or None

    def get_image_url(self, obj):
        if not obj.featured_item.image:
            return None

        request = self.context.get("request")
        url = obj.featured_item.image.url
        return request.build_absolute_uri(url) if request else url


class PlaceListSerializer(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(read_only=True, slug_field="slug")
    subcategory = serializers.SlugRelatedField(read_only=True, slug_field="slug")
    contact_points = ContactPointSerializer(many=True, read_only=True)
    latitude = serializers.SerializerMethodField()
    longitude = serializers.SerializerMethodField()
    distance_km = serializers.SerializerMethodField()
    google_rating = serializers.SerializerMethodField()
    google_reviews_count = serializers.SerializerMethodField()
    verification_status = serializers.SerializerMethodField()
    is_premium_verified = serializers.SerializerMethodField()
    can_claim = serializers.SerializerMethodField()
    is_open_now = serializers.SerializerMethodField()
    opening_hours = serializers.SerializerMethodField()

    class Meta:
        model = Place
        fields = (
            "name",
            "slug",
            "summary",
            "category",
            "subcategory",
            "formatted_address",
            "commune",
            "region",
            "country",
            "is_verified",
            "is_featured",
            "is_emergency_service",
            "is_open_24_7",
            "website",
            "latitude",
            "longitude",
            "distance_km",
            "google_rating",
            "google_reviews_count",
            "verification_status",
            "is_premium_verified",
            "can_claim",
            "contact_points",
            "is_open_now",
            "opening_hours",
        )

    def get_is_open_now(self, obj):
        return obj.is_open_now_at()

    def get_opening_hours(self, obj):
        return obj.opening_hours_normalized or {}

    def get_latitude(self, obj):
        return obj.location.y if obj.location else None

    def get_longitude(self, obj):
        return obj.location.x if obj.location else None

    def get_distance_km(self, obj):
        distance = getattr(obj, "distance_m", None)
        if distance is None:
            return None
        return round(distance.m / 1000, 2)

    def get_google_rating(self, obj):
        if obj.google_rating is not None:
            return float(obj.google_rating)

        fallback_rating = (obj.metadata or {}).get("google_rating")
        if fallback_rating is None:
            return None

        try:
            return float(fallback_rating)
        except (TypeError, ValueError):
            return None

    def get_google_reviews_count(self, obj):
        if obj.google_reviews_count:
            return obj.google_reviews_count
        return (obj.metadata or {}).get("google_total_ratings", 0)

    def _get_effective_verification_status(self, obj):
        cache = getattr(self, "_verification_status_cache", {})
        if obj.pk not in cache:
            cache[obj.pk] = get_place_effective_verification_status(obj)
            self._verification_status_cache = cache
        return cache[obj.pk]

    def get_verification_status(self, obj):
        return self._get_effective_verification_status(obj)

    def get_is_premium_verified(self, obj):
        return self._get_effective_verification_status(obj) == PLACE_EFFECTIVE_VERIFICATION_PREMIUM

    def get_can_claim(self, obj):
        return self._get_effective_verification_status(obj) == PlaceVerificationStatus.UNVERIFIED


class PlaceDetailSerializer(PlaceListSerializer):
    source = serializers.SlugRelatedField(read_only=True, slug_field="slug")
    featured_items = serializers.SerializerMethodField()

    class Meta(PlaceListSerializer.Meta):
        fields = PlaceListSerializer.Meta.fields + (
            "description",
            "metadata",
            "source",
            "featured_items",
            "created_at",
            "updated_at",
        )

    def get_featured_items(self, obj):
        assignments = getattr(obj, "prefetched_featured_catalog_assignments", None)
        if assignments is None:
            assignments = (
                obj.featured_catalog_assignments.select_related("featured_item")
                .filter(is_active=True, featured_item__is_active=True)
                .order_by("sort_order", "id")
            )

        return PlaceFeaturedCatalogItemSerializer(
            assignments,
            many=True,
            context=self.context,
        ).data


class PublicPetOperationSerializer(serializers.ModelSerializer):
    is_expired = serializers.ReadOnlyField()
    is_publicly_visible = serializers.ReadOnlyField()
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = PublicPetOperation
        fields = (
            "title",
            "slug",
            "operation_type",
            "creator_type",
            "creator_name",
            "address",
            "commune",
            "region",
            "latitude",
            "longitude",
            "starts_at",
            "ends_at",
            "requirements",
            "image_url",
            "status",
            "is_expired",
            "is_publicly_visible",
            "created_at",
            "updated_at",
        )

    def get_image_url(self, obj):
        if not obj.image:
            return None
        request = self.context.get("request")
        url = obj.image.url
        return request.build_absolute_uri(url) if request else url
