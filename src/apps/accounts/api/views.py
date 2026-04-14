from rest_framework import generics, permissions
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
    build_registration_catalog,
)
from apps.memberships.services import ensure_default_membership_for_owner, sync_memberships_for_owner


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
