from django.urls import path

from apps.analytics.api.views import (
    AnalyticsOverviewView,
    PlaceViewEventCreateView,
    SearchEventCreateView,
)

urlpatterns = [
    path("events/searches/", SearchEventCreateView.as_view(), name="analytics-events-searches"),
    path("events/place-views/", PlaceViewEventCreateView.as_view(), name="analytics-events-place-views"),
    path("overview/", AnalyticsOverviewView.as_view(), name="analytics-overview"),
]
