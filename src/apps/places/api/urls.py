from rest_framework.routers import DefaultRouter

from apps.places.api.views import PlaceViewSet, PublicPetOperationViewSet

router = DefaultRouter()
router.register("public-operations", PublicPetOperationViewSet, basename="public-pet-operation")
router.register("", PlaceViewSet, basename="place")

urlpatterns = router.urls
