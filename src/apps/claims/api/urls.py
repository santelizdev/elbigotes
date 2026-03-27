from django.urls import path

from apps.claims.api.views import PlaceClaimRequestCreateView

urlpatterns = [
    path(
        "places/<slug:slug>/requests/",
        PlaceClaimRequestCreateView.as_view(),
        name="place-claim-request-create",
    ),
]
