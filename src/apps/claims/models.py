import uuid

from django.conf import settings
from django.db import models

from apps.claims.choices import ClaimRequestStatus
from apps.core.models import TimeStampedModel


class ClaimRequest(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    place = models.ForeignKey("places.Place", on_delete=models.CASCADE, related_name="claim_requests")
    status = models.CharField(
        max_length=24,
        choices=ClaimRequestStatus.choices,
        default=ClaimRequestStatus.PENDING,
    )
    claimer_name = models.CharField(max_length=120)
    organization_name = models.CharField(max_length=180, blank=True)
    email = models.EmailField()
    phone = models.CharField(max_length=40, blank=True)
    relationship_to_place = models.CharField(max_length=120)
    message = models.TextField(blank=True)
    evidence_url = models.URLField(blank=True)
    review_notes = models.TextField(blank=True)
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="reviewed_claim_requests",
        null=True,
        blank=True,
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Claim request"
        verbose_name_plural = "Claim requests"

    def __str__(self) -> str:
        return f"{self.place.name} - {self.status}"

