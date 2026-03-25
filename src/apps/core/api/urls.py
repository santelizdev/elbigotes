from django.urls import path

from apps.core.api.views import HealthCheckView

urlpatterns = [
    path("health/", HealthCheckView.as_view(), name="healthcheck"),
]

