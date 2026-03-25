from rest_framework import generics

from apps.taxonomy.api.serializers import PublicCategorySerializer
from apps.taxonomy.models import Category


class PublicCategoryListView(generics.ListAPIView):
    authentication_classes = []
    permission_classes = []
    pagination_class = None
    serializer_class = PublicCategorySerializer

    def get_queryset(self):
        return Category.objects.filter(is_active=True).order_by("sort_order", "name")
