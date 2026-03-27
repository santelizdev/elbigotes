from django.contrib import admin

from apps.claims.choices import ClaimRequestStatus
from apps.claims.models import ClaimRequest


@admin.register(ClaimRequest)
class ClaimRequestAdmin(admin.ModelAdmin):
    list_display = ("place", "claimer_name", "status", "email", "created_at", "reviewed_at")
    list_filter = ("status", "created_at")
    search_fields = ("place__name", "claimer_name", "organization_name", "email")
    autocomplete_fields = ("place", "reviewed_by")
    readonly_fields = ("created_at", "updated_at")
    actions = ("mark_under_review", "mark_approved", "mark_rejected")

    @admin.action(description="Marcar como en revisión")
    def mark_under_review(self, request, queryset):
        queryset.update(status=ClaimRequestStatus.UNDER_REVIEW)

    @admin.action(description="Aprobar reclamos seleccionados")
    def mark_approved(self, request, queryset):
        queryset.update(status=ClaimRequestStatus.APPROVED)

    @admin.action(description="Rechazar reclamos seleccionados")
    def mark_rejected(self, request, queryset):
        queryset.update(status=ClaimRequestStatus.REJECTED)
