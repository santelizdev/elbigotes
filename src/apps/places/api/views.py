from rest_framework import mixins, viewsets

from apps.places.api.serializers import (
    PlaceDetailSerializer,
    PlaceListSerializer,
    PublicPetOperationSerializer,
)
from apps.places.filters import PlaceFilterSet, PublicPetOperationFilterSet
from apps.places.selectors import build_place_queryset, build_public_pet_operation_queryset


class PlaceViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    filterset_class = PlaceFilterSet
    lookup_field = "slug"
    ordering_fields = ("name", "created_at", "distance_m")

    def get_queryset(self):
        return build_place_queryset(
            self.request.query_params,
            include_featured_items=self.action == "retrieve",
        )

    def get_serializer_class(self):
        if self.action == "retrieve":
            return PlaceDetailSerializer
        return PlaceListSerializer


class PublicPetOperationViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = PublicPetOperationSerializer
    filterset_class = PublicPetOperationFilterSet
    lookup_field = "slug"
    ordering_fields = ("starts_at", "created_at", "title")

    def get_queryset(self):
        include_expired = self.request.query_params.get("include_expired", "").lower() in {
            "1",
            "true",
            "yes",
        }
        return build_public_pet_operation_queryset(include_expired=include_expired)
