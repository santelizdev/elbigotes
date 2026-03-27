from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone

from apps.core.models import TimeStampedModel


class ReviewStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    PUBLISHED = "published", "Published"
    REJECTED = "rejected", "Rejected"


class PlaceReview(TimeStampedModel):
    place = models.ForeignKey(
        "places.Place",
        on_delete=models.CASCADE,
        related_name="reviews",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="place_reviews",
        null=True,
        blank=True,
    )
    reviewer_name = models.CharField(max_length=120)
    reviewer_email = models.EmailField()
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    title = models.CharField(max_length=160, blank=True)
    body = models.TextField()
    is_verified_visit = models.BooleanField(default=False)
    status = models.CharField(
        max_length=20,
        choices=ReviewStatus.choices,
        default=ReviewStatus.PENDING,
    )
    moderation_notes = models.TextField(blank=True)
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="reviewed_place_reviews",
        null=True,
        blank=True,
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    published_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-published_at", "-created_at"]
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["place", "status"]),
        ]
        verbose_name = "Place review"
        verbose_name_plural = "Place reviews"

    def mark_published(self, reviewed_by=None):
        self.status = ReviewStatus.PUBLISHED
        self.reviewed_by = reviewed_by
        now = timezone.now()
        self.reviewed_at = now
        self.published_at = now
        self.save(update_fields=["status", "reviewed_by", "reviewed_at", "published_at", "updated_at"])

    def mark_rejected(self, reviewed_by=None, notes: str = ""):
        self.status = ReviewStatus.REJECTED
        self.reviewed_by = reviewed_by
        self.reviewed_at = timezone.now()
        self.moderation_notes = notes
        self.save(update_fields=["status", "reviewed_by", "reviewed_at", "moderation_notes", "updated_at"])

    def __str__(self) -> str:
        return f"{self.place.name} - {self.rating}/5"
