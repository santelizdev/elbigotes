from django.db.models import Q
from django_filters import rest_framework as filters

from apps.places.models import Place


class PlaceFilterSet(filters.FilterSet):
    category = filters.CharFilter(field_name="category__slug", lookup_expr="iexact")
    subcategory = filters.CharFilter(field_name="subcategory__slug", lookup_expr="iexact")
    commune = filters.CharFilter(field_name="commune", lookup_expr="icontains")
    region = filters.CharFilter(field_name="region", lookup_expr="icontains")
    search = filters.CharFilter(method="filter_search")
    is_open_24_7 = filters.BooleanFilter()
    is_emergency_service = filters.BooleanFilter()
    verified_only = filters.BooleanFilter(method="filter_verified_only")

    class Meta:
        model = Place
        fields = [
            "category",
            "subcategory",
            "commune",
            "region",
            "is_open_24_7",
            "is_emergency_service",
        ]

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(name__icontains=value)
            | Q(summary__icontains=value)
            | Q(description__icontains=value)
            | Q(formatted_address__icontains=value)
        )

    def filter_verified_only(self, queryset, name, value):
        if value:
            return queryset.filter(is_verified=True)
        return queryset

