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
        "owner_label",
        "owner_content_type",
        "owner_object_id",
        "starts_at",
        "ends_at",
        "renews_at",
    )
    list_filter = ("status", "plan__audience", "plan__billing_interval")
    search_fields = ("plan__name", "owner_object_id", "notes")
    raw_id_fields = ("plan", "owner_content_type")
    list_select_related = ("plan", "owner_content_type")

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("plan", "owner_content_type")

    @admin.display(description="Owner")
    def owner_label(self, obj):
        return str(obj.owner) if obj.owner else "Sin owner"
