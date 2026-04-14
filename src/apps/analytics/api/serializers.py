from rest_framework import serializers

from apps.analytics.services import build_kpi_overview, record_place_view_event, record_search_event
from apps.places.models import Place
from apps.places.services.verification import get_place_effective_verification_status


class SearchEventCreateSerializer(serializers.Serializer):
    category_slug = serializers.CharField(max_length=120, required=False, allow_blank=True)
    search_term = serializers.CharField(max_length=160, required=False, allow_blank=True)
    region = serializers.CharField(max_length=120, required=False, allow_blank=True)
    commune = serializers.CharField(max_length=120, required=False, allow_blank=True)
    has_user_location = serializers.BooleanField(required=False, default=False)
    user_latitude = serializers.DecimalField(
        max_digits=9, decimal_places=6, required=False, allow_null=True
    )
    user_longitude = serializers.DecimalField(
        max_digits=9, decimal_places=6, required=False, allow_null=True
    )
    radius_km = serializers.IntegerField(required=False, allow_null=True, min_value=0)
    verified_only = serializers.BooleanField(required=False, default=False)
    result_count = serializers.IntegerField(required=False, min_value=0, default=0)
    path = serializers.CharField(max_length=255, required=False, allow_blank=True)

    def create(self, validated_data):
        request = self.context["request"]
        return record_search_event(
            user=request.user,
            user_agent=request.META.get("HTTP_USER_AGENT", ""),
            payload=validated_data,
        )


class PlaceViewEventCreateSerializer(serializers.Serializer):
    place_slug = serializers.SlugField()
    path = serializers.CharField(max_length=255, required=False, allow_blank=True)

    def validate_place_slug(self, value):
        try:
            return Place.objects.select_related("category", "owner_business_profile").get(slug=value, status="active")
        except Place.DoesNotExist as exc:
            raise serializers.ValidationError("La ficha indicada no existe o no está activa.") from exc

    def create(self, validated_data):
        request = self.context["request"]
        place = validated_data["place_slug"]
        return record_place_view_event(
            user=request.user,
            user_agent=request.META.get("HTTP_USER_AGENT", ""),
            place=place,
            payload={
                "path": validated_data.get("path", ""),
                "verification_status": get_place_effective_verification_status(place),
            },
        )


class AnalyticsOverviewQuerySerializer(serializers.Serializer):
    days = serializers.IntegerField(required=False, min_value=1, max_value=90, default=7)

    def create(self, validated_data):
        return build_kpi_overview(days=validated_data["days"])
