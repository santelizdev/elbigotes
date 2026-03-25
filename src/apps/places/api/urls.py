from rest_framework.routers import DefaultRouter

from apps.places.api.views import PlaceViewSet

router = DefaultRouter()
router.register("", PlaceViewSet, basename="place")

urlpatterns = router.urls

