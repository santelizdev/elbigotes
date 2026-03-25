from django.contrib import admin

from apps.memberships.models import MembershipAssignment, MembershipPlan


@admin.register(MembershipPlan)
class MembershipPlanAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "audience",
        "billing_interval",
        "price_amount",
        "currency",
        "is_active",
        "is_public",
    )
    list_filter = ("audience", "billing_interval", "is_active", "is_public")
    search_fields = ("name", "slug")
    ordering = ("audience", "price_amount", "name")


@admin.register(MembershipAssignment)
class MembershipAssignmentAdmin(admin.ModelAdmin):
    list_display = (
        "plan",
        "status",
        "owner_content_type",
        "owner_object_id",
        "starts_at",
        "ends_at",
        "renews_at",
    )
    list_filter = ("status", "plan__audience", "plan__billing_interval")
    search_fields = ("plan__name", "notes")
    autocomplete_fields = ("plan",)
