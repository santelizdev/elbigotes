from rest_framework import serializers

from apps.taxonomy.models import Category


class PublicCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = (
            "name",
            "slug",
            "description",
            "icon_name",
            "sort_order",
        )
