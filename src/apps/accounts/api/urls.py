from django.urls import path

from apps.accounts.api.views import (
    AccountLoginView,
    BusinessBranchCreateView,
    BusinessRegistrationView,
    BusinessWorkspaceView,
    PetOwnerRegistrationView,
    RegistrationCatalogView,
)

urlpatterns = [
    path("catalog/", RegistrationCatalogView.as_view(), name="accounts-registration-catalog"),
    path("login/", AccountLoginView.as_view(), name="accounts-login"),
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
    path(
        "me/business/branches/",
        BusinessBranchCreateView.as_view(),
        name="accounts-me-business-branches",
    ),
]
