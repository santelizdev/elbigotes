from datetime import timedelta

from django.utils import timezone
from rest_framework import serializers

from apps.lost_pets.choices import LostPetModerationStatus
from apps.lost_pets.models import LostPetReport
from apps.lost_pets.services import create_lost_pet_report


class LostPetReportListSerializer(serializers.ModelSerializer):
    latitude = serializers.SerializerMethodField()
    longitude = serializers.SerializerMethodField()
    photo_url = serializers.SerializerMethodField()

    class Meta:
        model = LostPetReport
        fields = (
            "id",
            "pet_name",
            "species",
            "breed",
            "sex",
            "color_description",
            "distinctive_marks",
            "status",
            "last_seen_at",
            "last_seen_address",
            "last_seen_reference",
            "latitude",
            "longitude",
            "photo_url",
            "is_reward_offered",
            "reward_amount",
            "moderation_status",
            "created_at",
        )

    def get_latitude(self, obj):
        return obj.last_seen_location.y if obj.last_seen_location else None

    def get_longitude(self, obj):
        return obj.last_seen_location.x if obj.last_seen_location else None

    def get_photo_url(self, obj):
        if obj.photo:
            request = self.context.get("request")
            url = obj.photo.url
            return request.build_absolute_uri(url) if request else url
        return obj.photo_url or None


class LostPetReportCreateSerializer(serializers.ModelSerializer):
    last_seen_latitude = serializers.FloatField(write_only=True, required=False, allow_null=True)
    last_seen_longitude = serializers.FloatField(write_only=True, required=False, allow_null=True)
    photo = serializers.ImageField(write_only=True, required=False, allow_null=True)

    class Meta:
        model = LostPetReport
        fields = (
            "id",
            "pet_name",
            "species",
            "breed",
            "sex",
            "color_description",
            "distinctive_marks",
            "status",
            "last_seen_at",
            "last_seen_latitude",
            "last_seen_longitude",
            "last_seen_address",
            "last_seen_reference",
            "reporter_name",
            "reporter_phone",
            "reporter_email",
            "additional_contact",
            "photo",
            "photo_url",
            "is_reward_offered",
            "reward_amount",
            "metadata",
            "moderation_status",
        )
        read_only_fields = ("id", "moderation_status")

    def validate(self, attrs):
        latitude = attrs.get("last_seen_latitude")
        longitude = attrs.get("last_seen_longitude")

        if (latitude is None) ^ (longitude is None):
            raise serializers.ValidationError(
                "Debes informar latitude y longitude juntas o dejar ambas vacías."
            )

        recent_duplicate = (
            LostPetReport.objects.filter(
                pet_name__iexact=attrs.get("pet_name", ""),
                reporter_phone__iexact=attrs.get("reporter_phone", ""),
                last_seen_address__iexact=attrs.get("last_seen_address", ""),
                status=attrs.get("status", "lost"),
                created_at__gte=timezone.now() - timedelta(hours=24),
            )
            .order_by("-created_at")
            .first()
        )
        if recent_duplicate:
            raise serializers.ValidationError(
                "Ya existe un reporte muy parecido publicado recientemente para esta mascota."
            )

        recent_volume = LostPetReport.objects.filter(
            reporter_phone__iexact=attrs.get("reporter_phone", ""),
            created_at__gte=timezone.now() - timedelta(hours=24),
        ).count()
        if recent_volume >= 3:
            raise serializers.ValidationError(
                "Se alcanzó el límite de publicaciones recientes para este teléfono."
            )

        return attrs

    def validate_photo(self, value):
        if not value:
            return value

        allowed_types = {"image/jpeg", "image/png", "image/webp"}
        if getattr(value, "content_type", "") not in allowed_types:
            raise serializers.ValidationError("La foto debe ser JPG, PNG o WebP.")

        max_size = 5 * 1024 * 1024
        if value.size > max_size:
            raise serializers.ValidationError("La foto no puede superar 5 MB.")

        return value

    def create(self, validated_data):
        validated_data["moderation_status"] = LostPetModerationStatus.PENDING
        return create_lost_pet_report(validated_data)

    def to_representation(self, instance):
        return LostPetReportListSerializer(instance, context=self.context).data
