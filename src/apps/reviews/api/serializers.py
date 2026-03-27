from rest_framework import serializers

from apps.places.choices import PlaceStatus
from apps.places.models import Place
from apps.reviews.models import PlaceReview, ReviewStatus


class PlaceReviewListSerializer(serializers.ModelSerializer):
    place_name = serializers.CharField(source="place.name", read_only=True)
    place_slug = serializers.CharField(source="place.slug", read_only=True)

    class Meta:
        model = PlaceReview
        fields = (
            "id",
            "place_name",
            "place_slug",
            "reviewer_name",
            "rating",
            "title",
            "body",
            "is_verified_visit",
            "published_at",
            "created_at",
        )


class PlaceReviewCreateSerializer(serializers.ModelSerializer):
    place_slug = serializers.SlugField(write_only=True)

    class Meta:
        model = PlaceReview
        fields = (
            "id",
            "place_slug",
            "reviewer_name",
            "reviewer_email",
            "rating",
            "title",
            "body",
            "is_verified_visit",
        )
        read_only_fields = ("id",)

    def validate_place_slug(self, value):
        try:
            place = Place.objects.get(slug=value)
        except Place.DoesNotExist as exc:
            raise serializers.ValidationError("La ficha indicada no existe.") from exc

        if place.status != PlaceStatus.ACTIVE:
            raise serializers.ValidationError("Solo puedes reseñar fichas publicadas.")

        self.context["place"] = place
        return value

    def validate(self, attrs):
        place = self.context["place"]
        existing_open_review = PlaceReview.objects.filter(
            place=place,
            reviewer_email__iexact=attrs["reviewer_email"],
            status=ReviewStatus.PENDING,
        ).exists()
        if existing_open_review:
            raise serializers.ValidationError(
                "Ya tienes una review pendiente de moderación para esta ficha."
            )
        return attrs

    def create(self, validated_data):
        validated_data.pop("place_slug", None)
        request = self.context.get("request")
        user = request.user if request and request.user.is_authenticated else None
        return PlaceReview.objects.create(
            place=self.context["place"],
            user=user,
            status=ReviewStatus.PENDING,
            **validated_data,
        )

    def to_representation(self, instance):
        return PlaceReviewListSerializer(instance, context=self.context).data
