from django.urls import path

from apps.accounts.api.views import (
    AccountLoginView,
    BusinessBranchCreateView,
    BusinessRegistrationView,
    BusinessWorkspaceView,
    EmailVerificationView,
    GoogleOAuthCallbackView,
    GoogleOAuthStartView,
    PetOwnerRegistrationView,
    PetOwnerWorkspaceView,
    RegistrationCatalogView,
    SavedPlaceCollectionView,
    SavedPlaceDetailView,
)

urlpatterns = [
    path("catalog/", RegistrationCatalogView.as_view(), name="accounts-registration-catalog"),
    path("login/", AccountLoginView.as_view(), name="accounts-login"),
    path("oauth/google/start/", GoogleOAuthStartView.as_view(), name="accounts-oauth-google-start"),
    path(
        "oauth/google/callback/",
        GoogleOAuthCallbackView.as_view(),
        name="accounts-oauth-google-callback",
    ),
    path("verify-email/", EmailVerificationView.as_view(), name="accounts-verify-email"),
    path(
        "register/business/",
        BusinessRegistrationView.as_view(),
        name="accounts-register-business",
    ),
    path(
        "register/pet-owner/",
        PetOwnerRegistrationView.as_view(),
        name="accounts-register-pet-owner",
    ),
    path("me/business/", BusinessWorkspaceView.as_view(), name="accounts-me-business"),
    path("me/pet-owner/", PetOwnerWorkspaceView.as_view(), name="accounts-me-pet-owner"),
    path("me/saved-places/", SavedPlaceCollectionView.as_view(), name="accounts-me-saved-places"),
    path(
        "me/saved-places/<slug:place_slug>/",
        SavedPlaceDetailView.as_view(),
        name="accounts-me-saved-place-detail",
    ),
    path(
        "me/business/branches/",
        BusinessBranchCreateView.as_view(),
        name="accounts-me-business-branches",
    ),
]
