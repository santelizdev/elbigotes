from rest_framework import generics

from apps.lost_pets.api.serializers import (
    LostPetReportCreateSerializer,
    LostPetReportListSerializer,
)
from apps.lost_pets.choices import LostPetModerationStatus
from apps.lost_pets.models import LostPetReport


class LostPetReportListCreateView(generics.ListCreateAPIView):
    ordering = ("-last_seen_at",)

    def get_queryset(self):
        queryset = LostPetReport.objects.all().order_by("-last_seen_at", "-created_at")
        if self.request.method == "GET":
            return queryset.filter(moderation_status=LostPetModerationStatus.APPROVED)
        return queryset

    def get_serializer_class(self):
        if self.request.method == "POST":
            return LostPetReportCreateSerializer
        return LostPetReportListSerializer
