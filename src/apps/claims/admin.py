from django.contrib import admin

from apps.claims.choices import ClaimRequestStatus
from apps.claims.models import ClaimRequest
from apps.places.services.verification import (
    mark_place_claim_requested,
    mark_place_verified,
    reset_place_verification_if_unclaimed,
)


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
        for claim in queryset:
            claim.status = ClaimRequestStatus.UNDER_REVIEW
            claim.save(update_fields=["status", "updated_at"])
            mark_place_claim_requested(claim.place)

    @admin.action(description="Aprobar reclamos seleccionados")
    def mark_approved(self, request, queryset):
        for claim in queryset:
            claim.status = ClaimRequestStatus.APPROVED
            claim.save(update_fields=["status", "updated_at"])
            mark_place_verified(claim.place)

    @admin.action(description="Rechazar reclamos seleccionados")
    def mark_rejected(self, request, queryset):
        for claim in queryset:
            claim.status = ClaimRequestStatus.REJECTED
            claim.save(update_fields=["status", "updated_at"])
            reset_place_verification_if_unclaimed(claim.place)
