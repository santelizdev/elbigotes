from django.urls import path

from apps.reviews.api.views import PlaceReviewListCreateView

urlpatterns = [
    path("", PlaceReviewListCreateView.as_view(), name="place-review-list-create"),
]
