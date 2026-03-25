from rest_framework import mixins, viewsets

from apps.places.api.serializers import PlaceDetailSerializer, PlaceListSerializer
from apps.places.filters import PlaceFilterSet
from apps.places.selectors import build_place_queryset


class PlaceViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    filterset_class = PlaceFilterSet
    lookup_field = "slug"
    ordering_fields = ("name", "created_at", "distance_m")

    def get_queryset(self):
        return build_place_queryset(self.request.query_params)

    def get_serializer_class(self):
        if self.action == "retrieve":
            return PlaceDetailSerializer
        return PlaceListSerializer

