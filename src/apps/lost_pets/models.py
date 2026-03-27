import uuid

from django.contrib.gis.db import models as gis_models
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from apps.core.models import TimeStampedModel
from apps.ingestion.models import Source
from apps.lost_pets.choices import (
    LostPetModerationStatus,
    LostPetReportStatus,
    LostPetSex,
    LostPetSpecies,
)


class LostPetReport(TimeStampedModel):
    """
    Reporte público separado del directorio de lugares porque su ciclo de vida es distinto
    y necesita reglas propias de publicación, cierre y verificación.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    pet_name = models.CharField(max_length=120)
    species = models.CharField(max_length=20, choices=LostPetSpecies.choices)
    breed = models.CharField(max_length=120, blank=True)
    sex = models.CharField(max_length=20, choices=LostPetSex.choices, default=LostPetSex.UNKNOWN)
    color_description = models.CharField(max_length=255)
    distinctive_marks = models.TextField(blank=True)
    status = models.CharField(
        max_length=20,
        choices=LostPetReportStatus.choices,
        default=LostPetReportStatus.LOST,
    )
    last_seen_at = models.DateTimeField()
    last_seen_location = gis_models.PointField(geography=True, srid=4326, null=True, blank=True)
    last_seen_address = models.CharField(max_length=255)
    last_seen_reference = models.CharField(max_length=255, blank=True)
    reporter_name = models.CharField(max_length=120)
    reporter_phone = models.CharField(max_length=40)
    reporter_email = models.EmailField(blank=True)
    additional_contact = models.CharField(max_length=255, blank=True)
    photo = models.FileField(upload_to="lost-pets/photos/%Y/%m/", blank=True)
    photo_url = models.URLField(blank=True)
    is_reward_offered = models.BooleanField(default=False)
    reward_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    pet_profile = models.ForeignKey(
        "accounts.PetProfile",
        on_delete=models.SET_NULL,
        related_name="lost_pet_reports",
        null=True,
        blank=True,
    )
    source = models.ForeignKey(
        Source,
        on_delete=models.SET_NULL,
        related_name="lost_pet_reports",
        null=True,
        blank=True,
    )
    moderation_status = models.CharField(
        max_length=20,
        choices=LostPetModerationStatus.choices,
        default=LostPetModerationStatus.PENDING,
    )
    moderation_notes = models.TextField(blank=True)
    moderated_at = models.DateTimeField(null=True, blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-last_seen_at", "-created_at"]
        verbose_name = "Lost pet report"
        verbose_name_plural = "Lost pet reports"

    def clean(self):
        if not self.is_reward_offered and self.reward_amount:
            raise ValidationError(
                {"reward_amount": "No se debe enviar monto si no hay recompensa ofrecida."}
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def mark_moderated(self, status: str, notes: str = ""):
        self.moderation_status = status
        self.moderation_notes = notes
        self.moderated_at = timezone.now()
        self.save(update_fields=["moderation_status", "moderation_notes", "moderated_at", "updated_at"])

    def __str__(self) -> str:
        return f"{self.pet_name} - {self.status}"
