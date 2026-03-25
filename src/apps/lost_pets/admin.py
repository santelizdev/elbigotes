from django.contrib import admin
from django.contrib.gis.admin import GISModelAdmin

from apps.lost_pets.choices import LostPetModerationStatus
from apps.lost_pets.models import LostPetReport


@admin.register(LostPetReport)
class LostPetReportAdmin(GISModelAdmin):
    list_display = (
        "pet_name",
        "species",
        "status",
        "moderation_status",
        "last_seen_at",
        "reporter_name",
        "created_at",
    )
    list_filter = ("species", "status", "sex", "moderation_status")
    search_fields = ("pet_name", "breed", "color_description", "reporter_name", "reporter_phone")
    autocomplete_fields = ("source",)
    readonly_fields = ("created_at", "updated_at", "moderated_at")
    actions = ("approve_reports", "reject_reports")

    @admin.action(description="Aprobar reportes seleccionados")
    def approve_reports(self, request, queryset):
        for report in queryset:
            report.mark_moderated(LostPetModerationStatus.APPROVED)

    @admin.action(description="Rechazar reportes seleccionados")
    def reject_reports(self, request, queryset):
        for report in queryset:
            report.mark_moderated(LostPetModerationStatus.REJECTED)
