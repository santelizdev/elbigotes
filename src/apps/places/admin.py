from django.contrib import admin
from django.contrib.gis.admin import GISModelAdmin

from apps.ingestion.tasks import audit_places_consistency, geocode_place
from apps.places.choices import PlaceVerificationStatus
from apps.places.models import ContactPoint, DuplicatePlaceCandidate, Place, PlaceQualityIssue


class ContactPointInline(admin.TabularInline):
    model = ContactPoint
    extra = 0
    fields = ("label", "kind", "value", "is_primary", "sort_order")


@admin.register(Place)
class PlaceAdmin(GISModelAdmin):
    list_display = (
        "name",
        "owner_business_profile",
        "category",
        "subcategory",
        "commune",
        "region",
        "status",
        "verification_status",
        "is_verified",
        "is_open_24_7",
    )
    list_filter = (
        "status",
        "category",
        "subcategory",
        "verification_status",
        "is_verified",
        "is_open_24_7",
        "is_emergency_service",
        "region",
    )
    search_fields = ("name", "slug", "summary", "formatted_address", "commune", "region")
    autocomplete_fields = ("category", "subcategory", "source", "owner_business_profile")
    prepopulated_fields = {"slug": ("name",)}
    inlines = [ContactPointInline]
    readonly_fields = ("created_at", "updated_at")
    actions = (
        "mark_as_active",
        "mark_as_archived",
        "mark_as_verified",
        "mark_as_claim_requested",
        "mark_as_unverified",
        "queue_geocoding",
        "queue_quality_audit",
    )

    @admin.action(description="Marcar seleccionados como activos")
    def mark_as_active(self, request, queryset):
        queryset.update(status="active")

    @admin.action(description="Archivar seleccionados")
    def mark_as_archived(self, request, queryset):
        queryset.update(status="archived")

    @admin.action(description="Marcar seleccionados como verificados")
    def mark_as_verified(self, request, queryset):
        queryset.update(
            verification_status=PlaceVerificationStatus.VERIFIED,
            is_verified=True,
        )

    @admin.action(description="Marcar seleccionados con reclamo en revisión")
    def mark_as_claim_requested(self, request, queryset):
        queryset.update(
            verification_status=PlaceVerificationStatus.CLAIM_REQUESTED,
            is_verified=False,
        )

    @admin.action(description="Marcar seleccionados como no verificados")
    def mark_as_unverified(self, request, queryset):
        queryset.update(
            verification_status=PlaceVerificationStatus.UNVERIFIED,
            is_verified=False,
        )

    @admin.action(description="Encolar geocodificación")
    def queue_geocoding(self, request, queryset):
        for place in queryset:
            geocode_place.delay(place.id)

    @admin.action(description="Encolar revisión de calidad")
    def queue_quality_audit(self, request, queryset):
        for place in queryset:
            audit_places_consistency.delay(place.id)


@admin.register(ContactPoint)
class ContactPointAdmin(admin.ModelAdmin):
    list_display = ("place", "kind", "value", "is_primary", "sort_order")
    list_filter = ("kind", "is_primary")
    search_fields = ("place__name", "value", "label")
    autocomplete_fields = ("place",)


@admin.register(PlaceQualityIssue)
class PlaceQualityIssueAdmin(admin.ModelAdmin):
    list_display = ("place", "code", "severity", "is_resolved", "created_at")
    list_filter = ("severity", "is_resolved", "code")
    search_fields = ("place__name", "message", "code")
    autocomplete_fields = ("place",)
    readonly_fields = ("created_at", "updated_at", "resolved_at")


@admin.register(DuplicatePlaceCandidate)
class DuplicatePlaceCandidateAdmin(admin.ModelAdmin):
    list_display = ("primary_place", "candidate_place", "similarity_score", "status", "reviewed_at")
    list_filter = ("status",)
    search_fields = ("primary_place__name", "candidate_place__name", "reason")
    autocomplete_fields = ("primary_place", "candidate_place", "reviewed_by")
    readonly_fields = ("created_at", "updated_at")
