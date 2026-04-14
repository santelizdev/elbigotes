from rest_framework import serializers

from apps.claims.choices import ClaimRequestStatus
from apps.claims.models import ClaimRequest
from apps.places.choices import PlaceStatus, PlaceVerificationStatus
from apps.places.services.verification import (
    PLACE_EFFECTIVE_VERIFICATION_PREMIUM,
    get_place_effective_verification_status,
    mark_place_claim_requested,
)


class ClaimRequestSerializer(serializers.ModelSerializer):
    place_name = serializers.CharField(source="place.name", read_only=True)
    place_slug = serializers.CharField(source="place.slug", read_only=True)

    class Meta:
        model = ClaimRequest
        fields = (
            "id",
            "place_name",
            "place_slug",
            "status",
            "claimer_name",
            "organization_name",
            "email",
            "phone",
            "relationship_to_place",
            "message",
            "evidence_url",
            "created_at",
        )
        read_only_fields = ("id", "status", "place_name", "place_slug", "created_at")


class ClaimRequestCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClaimRequest
        fields = (
            "id",
            "claimer_name",
            "organization_name",
            "email",
            "phone",
            "relationship_to_place",
            "message",
            "evidence_url",
        )
        read_only_fields = ("id",)

    def validate(self, attrs):
        place = self.context["place"]
        verification_status = get_place_effective_verification_status(place)

        if place.status != PlaceStatus.ACTIVE:
            raise serializers.ValidationError(
                "Esta ficha todavía no está publicada para recibir reclamos."
            )

        if verification_status in {PlaceVerificationStatus.VERIFIED, PLACE_EFFECTIVE_VERIFICATION_PREMIUM}:
            raise serializers.ValidationError(
                "Esta ficha ya está verificada. Si necesitas soporte, contáctanos directamente."
            )

        if verification_status == PlaceVerificationStatus.CLAIM_REQUESTED:
            raise serializers.ValidationError(
                "Esta ficha ya tiene una solicitud de propiedad en revisión."
            )

        existing_open_claim = ClaimRequest.objects.filter(
            place=place,
            email__iexact=attrs["email"],
            status__in=[ClaimRequestStatus.PENDING, ClaimRequestStatus.UNDER_REVIEW],
        ).exists()
        if existing_open_claim:
            raise serializers.ValidationError(
                "Ya existe una solicitud abierta para esta ficha con este correo."
            )

        return attrs

    def create(self, validated_data):
        claim = ClaimRequest.objects.create(
            place=self.context["place"],
            status=ClaimRequestStatus.PENDING,
            **validated_data,
        )
        mark_place_claim_requested(claim.place)
        return claim

    def to_representation(self, instance):
        return ClaimRequestSerializer(instance, context=self.context).data
