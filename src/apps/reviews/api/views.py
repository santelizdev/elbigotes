from rest_framework import generics

from apps.reviews.api.serializers import PlaceReviewCreateSerializer, PlaceReviewListSerializer
from apps.reviews.models import PlaceReview, ReviewStatus


class PlaceReviewListCreateView(generics.ListCreateAPIView):
    authentication_classes = []
    permission_classes = []
    ordering = ("-published_at", "-created_at")

    def get_queryset(self):
        queryset = PlaceReview.objects.select_related("place").order_by("-published_at", "-created_at")
        if self.request.method == "GET":
            queryset = queryset.filter(status=ReviewStatus.PUBLISHED)

        place_slug = self.request.query_params.get("place")
        if place_slug:
            queryset = queryset.filter(place__slug=place_slug)

        return queryset

    def get_serializer_class(self):
        if self.request.method == "POST":
            return PlaceReviewCreateSerializer
        return PlaceReviewListSerializer
