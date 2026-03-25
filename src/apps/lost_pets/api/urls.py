from django.urls import path

from apps.lost_pets.api.views import LostPetReportListCreateView

urlpatterns = [
    path("reports/", LostPetReportListCreateView.as_view(), name="lost-pet-report-list-create"),
]

