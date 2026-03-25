from django.conf import settings
from django.db import models
from django.utils import timezone

from apps.core.models import TimeStampedModel
from apps.core.utils.slugs import generate_unique_slug


class SourceKind(models.TextChoices):
    MANUAL = "manual", "Manual"
    PARTNER = "partner", "Partner"
    SCRAPER = "scraper", "Scraper"
    API = "api", "API"


class SyncRunStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    RUNNING = "running", "Running"
    SUCCEEDED = "succeeded", "Succeeded"
    FAILED = "failed", "Failed"


class ImportRecordStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    IMPORTED = "imported", "Imported"
    SKIPPED = "skipped", "Skipped"
    FAILED = "failed", "Failed"


class GeocodingStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    SUCCEEDED = "succeeded", "Succeeded"
    FAILED = "failed", "Failed"


class Source(TimeStampedModel):
    name = models.CharField(max_length=150, unique=True)
    slug = models.SlugField(max_length=220, unique=True)
    kind = models.CharField(max_length=24, choices=SourceKind.choices, default=SourceKind.MANUAL)
    domain = models.CharField(max_length=255, blank=True)
    reliability_score = models.DecimalField(max_digits=3, decimal_places=2, default=0.50)
    metadata = models.JSONField(default=dict, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Source"
        verbose_name_plural = "Sources"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_unique_slug(self, self.name)
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.name


class SourceDataset(TimeStampedModel):
    source = models.ForeignKey(Source, on_delete=models.CASCADE, related_name="datasets")
    name = models.CharField(max_length=150)
    slug = models.SlugField(max_length=220, unique=True)
    description = models.TextField(blank=True)
    default_country = models.CharField(max_length=120, default="Chile")
    default_region = models.CharField(max_length=120, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["source__name", "name"]
        constraints = [
            models.UniqueConstraint(fields=["source", "name"], name="ingestion_dataset_unique_name")
        ]
        verbose_name = "Source dataset"
        verbose_name_plural = "Source datasets"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_unique_slug(self, f"{self.source_id}-{self.name}")
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.source.name} / {self.name}"


class SourceSyncRun(TimeStampedModel):
    source = models.ForeignKey(Source, on_delete=models.CASCADE, related_name="sync_runs")
    status = models.CharField(max_length=24, choices=SyncRunStatus.choices, default=SyncRunStatus.PENDING)
    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    items_seen = models.PositiveIntegerField(default=0)
    items_created = models.PositiveIntegerField(default=0)
    items_updated = models.PositiveIntegerField(default=0)
    error_message = models.TextField(blank=True)
    stats = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Source sync run"
        verbose_name_plural = "Source sync runs"

    def __str__(self) -> str:
        return f"{self.source.name} - {self.status}"


class ImportedPlaceRecord(TimeStampedModel):
    dataset = models.ForeignKey(SourceDataset, on_delete=models.CASCADE, related_name="import_records")
    source = models.ForeignKey(Source, on_delete=models.CASCADE, related_name="import_records")
    imported_place = models.ForeignKey(
        "places.Place",
        on_delete=models.SET_NULL,
        related_name="import_records",
        null=True,
        blank=True,
    )
    external_id = models.CharField(max_length=120)
    status = models.CharField(
        max_length=20,
        choices=ImportRecordStatus.choices,
        default=ImportRecordStatus.PENDING,
    )
    checksum = models.CharField(max_length=64, blank=True)
    raw_name = models.CharField(max_length=200)
    raw_address = models.CharField(max_length=255, blank=True)
    raw_payload = models.JSONField(default=dict, blank=True)
    notes = models.TextField(blank=True)
    imported_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["dataset", "external_id"],
                name="ingestion_import_record_unique_external_id",
            )
        ]
        verbose_name = "Imported place record"
        verbose_name_plural = "Imported place records"

    def mark_imported(self, place):
        self.imported_place = place
        self.status = ImportRecordStatus.IMPORTED
        self.imported_at = timezone.now()
        self.save(update_fields=["imported_place", "status", "imported_at", "updated_at"])

    def __str__(self) -> str:
        return f"{self.dataset.slug} / {self.external_id}"


class GeocodingLog(TimeStampedModel):
    place = models.ForeignKey("places.Place", on_delete=models.CASCADE, related_name="geocoding_logs")
    provider = models.CharField(max_length=40)
    query = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=GeocodingStatus.choices)
    matched_address = models.CharField(max_length=255, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    raw_response = models.JSONField(default=dict, blank=True)
    error_message = models.TextField(blank=True)
    triggered_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="geocoding_logs",
        null=True,
        blank=True,
    )

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Geocoding log"
        verbose_name_plural = "Geocoding logs"

    def __str__(self) -> str:
        return f"{self.place.name} - {self.status}"
