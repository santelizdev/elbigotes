from django.conf import settings
from django.contrib import admin
from django.contrib.gis.admin import GISModelAdmin
from django.utils.html import format_html

from apps.ingestion.tasks import audit_places_consistency, geocode_place
from apps.places.choices import PlaceVerificationStatus
from apps.places.forms import PublicPetOperationAdminForm, build_public_pet_operation_admin_config
from apps.places.models import (
    ContactPoint,
    DuplicatePlaceCandidate,
    FeaturedCatalogItem,
    Place,
    PlaceFeaturedCatalogItem,
    PlaceQualityIssue,
    PublicPetOperation,
)


class ContactPointInline(admin.TabularInline):
    model = ContactPoint
    extra = 0
    fields = ("label", "kind", "value", "is_primary", "sort_order")


class PlaceFeaturedCatalogItemInline(admin.TabularInline):
    model = PlaceFeaturedCatalogItem
    extra = 0
    fields = ("featured_item", "custom_price_label", "custom_cta_url", "is_active", "sort_order")
    autocomplete_fields = ("featured_item",)


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
    search_fields = (
        "name",
        "slug",
        "summary",
        "street_address",
        "formatted_address",
        "commune",
        "region",
    )
    autocomplete_fields = ("category", "subcategory", "source", "owner_business_profile")
    prepopulated_fields = {"slug": ("name",)}
    inlines = [ContactPointInline, PlaceFeaturedCatalogItemInline]
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


@admin.register(FeaturedCatalogItem)
class FeaturedCatalogItemAdmin(admin.ModelAdmin):
    list_display = ("title", "item_type", "category", "price_label", "cta_label", "is_active")
    list_filter = ("item_type", "category", "is_active")
    search_fields = ("title", "description")
    autocomplete_fields = ("category",)
    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = ("created_at", "updated_at")


@admin.register(PlaceFeaturedCatalogItem)
class PlaceFeaturedCatalogItemAdmin(admin.ModelAdmin):
    list_display = ("place", "featured_item", "is_active", "sort_order", "updated_at")
    list_filter = ("is_active",)
    search_fields = (
        "place__name",
        "place__formatted_address",
        "place__commune",
        "featured_item__title",
        "featured_item__description",
    )
    autocomplete_fields = ("place", "featured_item")
    readonly_fields = ("created_at", "updated_at")


@admin.register(PublicPetOperation)
class PublicPetOperationAdmin(admin.ModelAdmin):
    form = PublicPetOperationAdminForm
    list_display = ("title", "operation_type", "commune", "starts_at", "status")
    list_filter = ("operation_type", "status", "commune", "starts_at")
    search_fields = ("title", "address", "commune", "requirements", "creator_name")
    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = (
        "location_preview",
        "created_at",
        "updated_at",
        "is_expired",
        "is_publicly_visible",
    )
    fields = (
        "title",
        "slug",
        "operation_type",
        "creator_type",
        "creator_name",
        "status",
        "region",
        "commune",
        "address",
        "latitude",
        "longitude",
        "location_preview",
        "starts_at",
        "ends_at",
        "requirements",
        "image",
        "is_expired",
        "is_publicly_visible",
        "created_at",
        "updated_at",
    )

    class Media:
        css = {
            "all": (
                "places/admin/public_pet_operation_admin.css",
            )
        }
        js = (
            "places/admin/public_pet_operation_admin.js",
        )

    @admin.display(description="Mapa de confirmación")
    def location_preview(self, obj):
        config = build_public_pet_operation_admin_config(
            google_maps_api_key=settings.GOOGLE_MAPS_API_KEY,
            latitude=getattr(obj, "latitude", None),
            longitude=getattr(obj, "longitude", None),
        )
        return format_html(
            '<div class="public-pet-operation-admin" data-public-pet-operation-config="{}">'
            '<p class="help">Escribe la dirección, selecciona una sugerencia de Google y confirma visualmente el punto sugerido antes de publicar.</p>'
            '<div class="public-pet-operation-admin__status" data-role="status"></div>'
            '<div class="public-pet-operation-admin__map" data-role="map"></div>'
            '<script type="application/json" id="public-pet-operation-admin-config">{}</script>'
            "</div>",
            config,
            config,
        )


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
