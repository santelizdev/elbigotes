from django.contrib import admin

from apps.claims.models import ClaimRequest


@admin.register(ClaimRequest)
class ClaimRequestAdmin(admin.ModelAdmin):
    list_display = ("place", "claimer_name", "status", "email", "created_at", "reviewed_at")
    list_filter = ("status", "created_at")
    search_fields = ("place__name", "claimer_name", "organization_name", "email")
    autocomplete_fields = ("place", "reviewed_by")
    readonly_fields = ("created_at", "updated_at")

