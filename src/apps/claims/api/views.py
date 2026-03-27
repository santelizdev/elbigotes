from django.shortcuts import get_object_or_404
from rest_framework import generics

from apps.claims.api.serializers import ClaimRequestCreateSerializer
from apps.places.models import Place


class PlaceClaimRequestCreateView(generics.CreateAPIView):
    serializer_class = ClaimRequestCreateSerializer
    authentication_classes = []
    permission_classes = []

    def get_place(self):
        return get_object_or_404(Place, slug=self.kwargs["slug"])

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["place"] = self.get_place()
        return context
