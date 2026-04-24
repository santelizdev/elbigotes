from urllib.parse import urlencode

from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.api.authentication import SignedTokenAuthentication
from apps.accounts.api.permissions import IsBusinessOwner, IsPetOwner
from apps.accounts.api.serializers import (
    BusinessBranchCreateSerializer,
    BusinessRegistrationSerializer,
    BusinessWorkspaceSerializer,
    BusinessWorkspaceUpdateSerializer,
    LoginSerializer,
    PetOwnerRegistrationSerializer,
    PetOwnerWorkspaceSerializer,
    RegistrationCatalogSerializer,
    SavedPlaceCreateSerializer,
    SavedPlaceSerializer,
    SavedPlaceStatusSerializer,
    build_registration_catalog,
)
from apps.accounts.email_verification import verify_email_token
from apps.accounts.models import SavedPlace
from apps.accounts.oauth import (
    GoogleOAuthConfigurationError,
    GoogleOAuthExchangeError,
    build_google_oauth_start_url,
    exchange_google_code_for_profile,
    get_or_create_user_from_google_profile,
)
from apps.accounts.tokens import create_access_token
from apps.memberships.services import (
    ensure_default_membership_for_owner,
    sync_memberships_for_owner,
)
from apps.places.models import Place


class BusinessRegistrationView(generics.CreateAPIView):
    serializer_class = BusinessRegistrationSerializer
    authentication_classes = []
    permission_classes = []


class PetOwnerRegistrationView(generics.CreateAPIView):
    serializer_class = PetOwnerRegistrationSerializer
    authentication_classes = []
    permission_classes = []


class RegistrationCatalogView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request, *args, **kwargs):
        serializer = RegistrationCatalogSerializer(build_registration_catalog())
        return Response(serializer.data)


class AccountLoginView(generics.CreateAPIView):
    serializer_class = LoginSerializer
    authentication_classes = []
    permission_classes = []


class GoogleOAuthStartView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request, *args, **kwargs):
        next_path = request.query_params.get("next") or "/ingresar"
        current_site_url = request.build_absolute_uri("/").rstrip("/")

        try:
            return HttpResponseRedirect(
                build_google_oauth_start_url(next_path=next_path, site_url=current_site_url)
            )
        except GoogleOAuthConfigurationError:
            params = urlencode({"error": "google_oauth_not_configured"})
            return HttpResponseRedirect(f"{settings.SITE_URL}/ingresar?{params}")


class GoogleOAuthCallbackView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request, *args, **kwargs):
        code = request.query_params.get("code", "")
        state = request.query_params.get("state", "")
        oauth_error = request.query_params.get("error")
        current_site_url = request.build_absolute_uri("/").rstrip("/")

        if oauth_error:
            params = urlencode({"error": oauth_error})
            return HttpResponseRedirect(f"{settings.SITE_URL}/ingresar?{params}")

        if not code or not state:
            params = urlencode({"error": "google_oauth_missing_code"})
            return HttpResponseRedirect(f"{settings.SITE_URL}/ingresar?{params}")

        try:
            state_payload, profile = exchange_google_code_for_profile(
                code=code,
                state_token=state,
                site_url=current_site_url,
            )
            user = get_or_create_user_from_google_profile(profile)
            token = create_access_token(user)
            params = urlencode(
                {
                    "token": token,
                    "role": user.role,
                    "auth_provider": "google",
                    "next": state_payload.get("next_path", "/ingresar"),
                }
            )
            return HttpResponseRedirect(f"{settings.SITE_URL}/ingresar?{params}")
        except (GoogleOAuthConfigurationError, GoogleOAuthExchangeError, ValueError):
            params = urlencode({"error": "google_oauth_failed"})
            return HttpResponseRedirect(f"{settings.SITE_URL}/ingresar?{params}")


class EmailVerificationView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request, *args, **kwargs):
        token = request.query_params.get("token", "")

        if not token:
            return HttpResponseRedirect(f"{settings.SITE_URL}/ingresar?verified=error")

        try:
            verify_email_token(token)
            return HttpResponseRedirect(f"{settings.SITE_URL}/ingresar?verified=success")
        except Exception:
            return HttpResponseRedirect(f"{settings.SITE_URL}/ingresar?verified=error")


class BusinessWorkspaceView(APIView):
    authentication_classes = [SignedTokenAuthentication]
    permission_classes = [permissions.IsAuthenticated, IsBusinessOwner]

    def get(self, request, *args, **kwargs):
        profile = request.user.business_profile
        ensure_default_membership_for_owner(profile)
        sync_memberships_for_owner(profile)
        serializer = BusinessWorkspaceSerializer({"user": request.user, "profile": profile})
        return Response(serializer.data)

    def patch(self, request, *args, **kwargs):
        profile = request.user.business_profile
        serializer = BusinessWorkspaceUpdateSerializer(instance=profile, data=request.data)
        serializer.is_valid(raise_exception=True)
        payload = serializer.save()
        return Response(BusinessWorkspaceSerializer(payload).data)


class PetOwnerWorkspaceView(APIView):
    authentication_classes = [SignedTokenAuthentication]
    permission_classes = [permissions.IsAuthenticated, IsPetOwner]

    def get(self, request, *args, **kwargs):
        profile = request.user.pet_owner_profile
        ensure_default_membership_for_owner(profile)
        sync_memberships_for_owner(profile)
        serializer = PetOwnerWorkspaceSerializer(
            {"user": request.user, "profile": profile},
            context={"request": request},
        )
        return Response(serializer.data)


class BusinessBranchCreateView(generics.CreateAPIView):
    serializer_class = BusinessBranchCreateSerializer
    authentication_classes = [SignedTokenAuthentication]
    permission_classes = [permissions.IsAuthenticated, IsBusinessOwner]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["profile"] = self.request.user.business_profile
        return context


class SavedPlaceCollectionView(APIView):
    authentication_classes = [SignedTokenAuthentication]
    permission_classes = [permissions.IsAuthenticated, IsPetOwner]

    def get(self, request, *args, **kwargs):
        saved_places = (
            SavedPlace.objects.select_related("place", "place__category")
            .filter(user=request.user, place__status="active")
            .order_by("-created_at")
        )
        serializer = SavedPlaceSerializer(saved_places, many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        serializer = SavedPlaceCreateSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        saved_place = serializer.save()
        response_serializer = SavedPlaceSerializer(saved_place)
        response_status = (
            status.HTTP_201_CREATED
            if serializer.context.get("created", False)
            else status.HTTP_200_OK
        )
        return Response(response_serializer.data, status=response_status)


class SavedPlaceDetailView(APIView):
    authentication_classes = [SignedTokenAuthentication]
    permission_classes = [permissions.IsAuthenticated, IsPetOwner]

    def get(self, request, place_slug, *args, **kwargs):
        place = get_object_or_404(Place.objects.filter(status="active"), slug=place_slug)
        saved_place = (
            SavedPlace.objects.select_related("place", "place__category")
            .filter(user=request.user, place=place)
            .first()
        )
        serializer = SavedPlaceStatusSerializer(
            {
                "is_saved": saved_place is not None,
                "item": saved_place,
            }
        )
        return Response(serializer.data)

    def delete(self, request, place_slug, *args, **kwargs):
        place = get_object_or_404(Place.objects.filter(status="active"), slug=place_slug)
        SavedPlace.objects.filter(user=request.user, place=place).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
