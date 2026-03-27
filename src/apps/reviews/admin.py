from django.contrib import admin

from apps.reviews.models import PlaceReview, ReviewStatus


@admin.register(PlaceReview)
class PlaceReviewAdmin(admin.ModelAdmin):
    list_display = (
        "place",
        "reviewer_name",
        "rating",
        "status",
        "is_verified_visit",
        "published_at",
        "created_at",
    )
    list_filter = ("status", "rating", "is_verified_visit", "created_at")
    search_fields = ("place__name", "reviewer_name", "reviewer_email", "title", "body")
    autocomplete_fields = ("place", "user", "reviewed_by")
    readonly_fields = ("created_at", "updated_at", "reviewed_at", "published_at")
    actions = ("publish_reviews", "reject_reviews")

    @admin.action(description="Publicar reviews seleccionadas")
    def publish_reviews(self, request, queryset):
        for review in queryset:
            review.mark_published(reviewed_by=request.user)

    @admin.action(description="Rechazar reviews seleccionadas")
    def reject_reviews(self, request, queryset):
        for review in queryset:
            review.mark_rejected(reviewed_by=request.user)
