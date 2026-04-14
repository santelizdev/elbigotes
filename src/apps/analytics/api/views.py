from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.api.authentication import SignedTokenAuthentication
from apps.analytics.api.permissions import IsInternalUser
from apps.analytics.api.serializers import (
    AnalyticsOverviewQuerySerializer,
    PlaceViewEventCreateSerializer,
    SearchEventCreateSerializer,
)


class SearchEventCreateView(generics.CreateAPIView):
    serializer_class = SearchEventCreateSerializer
    authentication_classes = [SignedTokenAuthentication]
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class PlaceViewEventCreateView(generics.CreateAPIView):
    serializer_class = PlaceViewEventCreateSerializer
    authentication_classes = [SignedTokenAuthentication]
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class AnalyticsOverviewView(APIView):
    authentication_classes = [SignedTokenAuthentication]
    permission_classes = [permissions.IsAuthenticated, IsInternalUser]

    def get(self, request, *args, **kwargs):
        serializer = AnalyticsOverviewQuerySerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.save())
