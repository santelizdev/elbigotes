from django.contrib import admin

from apps.analytics.models import PlaceViewEvent, SearchEvent


@admin.register(SearchEvent)
class SearchEventAdmin(admin.ModelAdmin):
    list_display = (
        "created_at",
        "category_slug",
        "region",
        "commune",
        "result_count",
        "device_type",
        "is_registered",
    )
    list_filter = ("category_slug", "device_type", "is_registered", "verified_only", "created_at")
    search_fields = ("search_term", "region", "commune", "path")
    autocomplete_fields = ("user",)
    readonly_fields = ("created_at", "updated_at")


@admin.register(PlaceViewEvent)
class PlaceViewEventAdmin(admin.ModelAdmin):
    list_display = (
        "created_at",
        "place",
        "category_slug",
        "verification_status",
        "device_type",
        "is_registered",
    )
    list_filter = ("category_slug", "verification_status", "device_type", "is_registered", "created_at")
    search_fields = ("place__name", "region", "commune", "path")
    autocomplete_fields = ("place", "user")
    readonly_fields = ("created_at", "updated_at")
