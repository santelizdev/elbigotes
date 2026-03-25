from rest_framework import serializers

from apps.places.models import ContactPoint, Place


class ContactPointSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactPoint
        fields = ("label", "kind", "value", "notes", "is_primary")


class PlaceListSerializer(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(read_only=True, slug_field="slug")
    subcategory = serializers.SlugRelatedField(read_only=True, slug_field="slug")
    contact_points = ContactPointSerializer(many=True, read_only=True)
    latitude = serializers.SerializerMethodField()
    longitude = serializers.SerializerMethodField()
    distance_km = serializers.SerializerMethodField()

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
            "contact_points",
        )

    def get_latitude(self, obj):
        return obj.location.y if obj.location else None

    def get_longitude(self, obj):
        return obj.location.x if obj.location else None

    def get_distance_km(self, obj):
        distance = getattr(obj, "distance_m", None)
        if distance is None:
            return None
        return round(distance.m / 1000, 2)


class PlaceDetailSerializer(PlaceListSerializer):
    source = serializers.SlugRelatedField(read_only=True, slug_field="slug")

    class Meta(PlaceListSerializer.Meta):
        fields = PlaceListSerializer.Meta.fields + (
            "description",
            "metadata",
            "source",
            "created_at",
            "updated_at",
        )

