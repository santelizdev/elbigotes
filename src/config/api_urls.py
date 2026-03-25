from django.urls import include, path

urlpatterns = [
    path("", include("apps.core.api.urls")),
    path("accounts/", include("apps.accounts.api.urls")),
    path("places/", include("apps.places.api.urls")),
    path("lost-pets/", include("apps.lost_pets.api.urls")),
]
