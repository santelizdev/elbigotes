from django.conf import settings
from django.contrib.gis.db import models as gis_models
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from apps.core.models import TimeStampedModel
from apps.core.utils.slugs import generate_unique_slug
from apps.ingestion.models import Source
from apps.places.choices import (
    ContactPointKind,
    DataIssueSeverity,
    DuplicateCandidateStatus,
    PlaceStatus,
)
from apps.taxonomy.models import Category, Subcategory


class Place(TimeStampedModel):
    """
    Ficha pública principal del mapa. Se mantiene intencionalmente compacta;
    los contactos y la procedencia viven en tablas separadas para escalar sin rigidez.
    """

    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True)
    summary = models.CharField(max_length=280, blank=True)
    description = models.TextField(blank=True)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="places")
    subcategory = models.ForeignKey(
        Subcategory,
        on_delete=models.PROTECT,
        related_name="places",
        null=True,
        blank=True,
    )
    status = models.CharField(max_length=20, choices=PlaceStatus.choices, default=PlaceStatus.DRAFT)
    location = gis_models.PointField(geography=True, srid=4326, null=True, blank=True)
    street_address = models.CharField(max_length=255, blank=True)
    commune = models.CharField(max_length=120, blank=True)
    region = models.CharField(max_length=120, blank=True)
    country = models.CharField(max_length=120, default="Chile")
    postal_code = models.CharField(max_length=20, blank=True)
    formatted_address = models.CharField(max_length=255, blank=True)
    website = models.URLField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    is_verified = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)
    is_emergency_service = models.BooleanField(default=False)
    is_open_24_7 = models.BooleanField(default=False)
    quality_score = models.PositiveSmallIntegerField(default=0)
    last_quality_check_at = models.DateTimeField(null=True, blank=True)
    source = models.ForeignKey(
        Source,
        on_delete=models.SET_NULL,
        related_name="places",
        null=True,
        blank=True,
    )
    owner_business_profile = models.ForeignKey(
        "accounts.BusinessProfile",
        on_delete=models.SET_NULL,
        related_name="owned_places",
        null=True,
        blank=True,
    )

    class Meta:
        ordering = ["-is_featured", "name"]
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["slug"]),
            models.Index(fields=["region", "commune"]),
        ]
        verbose_name = "Place"
        verbose_name_plural = "Places"

    def clean(self):
        has_address = any([self.street_address, self.formatted_address, self.commune, self.region])
        if not self.location and not has_address:
            raise ValidationError(
                {"location": "Debes informar coordenadas o una dirección suficiente para geocodificar."}
            )
        if self.subcategory and self.subcategory.category_id != self.category_id:
            raise ValidationError(
                {"subcategory": "La subcategoría debe pertenecer a la categoría seleccionada."}
            )

    @property
    def geocoding_query(self) -> str:
        parts = [
            self.street_address,
            self.formatted_address,
            self.commune,
            self.region,
            self.country,
        ]
        return ", ".join(part for part in parts if part)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_unique_slug(self, self.name)
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.name


class ContactPoint(TimeStampedModel):
    place = models.ForeignKey(Place, on_delete=models.CASCADE, related_name="contact_points")
    label = models.CharField(max_length=80)
    kind = models.CharField(max_length=20, choices=ContactPointKind.choices)
    value = models.CharField(max_length=255)
    notes = models.CharField(max_length=255, blank=True)
    is_primary = models.BooleanField(default=False)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["sort_order", "-is_primary", "kind"]
        verbose_name = "Contact point"
        verbose_name_plural = "Contact points"

    def __str__(self) -> str:
        return f"{self.place.name} - {self.kind}"


class PlaceQualityIssue(TimeStampedModel):
    place = models.ForeignKey(Place, on_delete=models.CASCADE, related_name="quality_issues")
    code = models.CharField(max_length=64)
    severity = models.CharField(max_length=20, choices=DataIssueSeverity.choices)
    message = models.CharField(max_length=255)
    details = models.JSONField(default=dict, blank=True)
    is_resolved = models.BooleanField(default=False)
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["place", "code", "message", "is_resolved"],
                name="places_quality_issue_unique_open",
            )
        ]
        verbose_name = "Place quality issue"
        verbose_name_plural = "Place quality issues"

    def mark_resolved(self):
        self.is_resolved = True
        self.resolved_at = timezone.now()
        self.save(update_fields=["is_resolved", "resolved_at", "updated_at"])

    def __str__(self) -> str:
        return f"{self.place.name} - {self.code}"


class DuplicatePlaceCandidate(TimeStampedModel):
    primary_place = models.ForeignKey(
        Place,
        on_delete=models.CASCADE,
        related_name="duplicate_candidates",
    )
    candidate_place = models.ForeignKey(
        Place,
        on_delete=models.CASCADE,
        related_name="duplicate_matches",
    )
    reason = models.CharField(max_length=255)
    similarity_score = models.DecimalField(max_digits=5, decimal_places=2)
    status = models.CharField(
        max_length=20,
        choices=DuplicateCandidateStatus.choices,
        default=DuplicateCandidateStatus.OPEN,
    )
    notes = models.TextField(blank=True)
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="reviewed_duplicate_candidates",
        null=True,
        blank=True,
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-similarity_score", "-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["primary_place", "candidate_place"],
                name="places_duplicate_candidate_unique_pair",
            )
        ]
        verbose_name = "Duplicate place candidate"
        verbose_name_plural = "Duplicate place candidates"

    def clean(self):
        if self.primary_place_id == self.candidate_place_id:
            raise ValidationError({"candidate_place": "Un lugar no puede ser duplicado de sí mismo."})

    def __str__(self) -> str:
        return f"{self.primary_place.name} ~ {self.candidate_place.name}"
