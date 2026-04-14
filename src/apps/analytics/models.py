from django.conf import settings
from django.db import models

from apps.core.models import TimeStampedModel


class AnalyticsDeviceType(models.TextChoices):
    PHONE = "phone", "Phone"
    PC = "pc", "PC"
    TABLET = "tablet", "Tablet"
    UNKNOWN = "unknown", "Unknown"


class SearchEvent(TimeStampedModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="search_events",
        null=True,
        blank=True,
    )
    category_slug = models.CharField(max_length=120, blank=True)
    search_term = models.CharField(max_length=160, blank=True)
    region = models.CharField(max_length=120, blank=True)
    commune = models.CharField(max_length=120, blank=True)
    has_user_location = models.BooleanField(default=False)
    user_latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    user_longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    radius_km = models.PositiveIntegerField(null=True, blank=True)
    verified_only = models.BooleanField(default=False)
    result_count = models.PositiveIntegerField(default=0)
    is_registered = models.BooleanField(default=False)
    device_type = models.CharField(
        max_length=20,
        choices=AnalyticsDeviceType.choices,
        default=AnalyticsDeviceType.UNKNOWN,
    )
    path = models.CharField(max_length=255, blank=True)
    user_agent = models.TextField(blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["created_at"]),
            models.Index(fields=["category_slug"]),
            models.Index(fields=["device_type"]),
            models.Index(fields=["is_registered"]),
        ]
        verbose_name = "Search event"
        verbose_name_plural = "Search events"


class PlaceViewEvent(TimeStampedModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="place_view_events",
        null=True,
        blank=True,
    )
    place = models.ForeignKey(
        "places.Place",
        on_delete=models.CASCADE,
        related_name="view_events",
    )
    category_slug = models.CharField(max_length=120, blank=True)
    region = models.CharField(max_length=120, blank=True)
    commune = models.CharField(max_length=120, blank=True)
    verification_status = models.CharField(max_length=40, blank=True)
    is_registered = models.BooleanField(default=False)
    device_type = models.CharField(
        max_length=20,
        choices=AnalyticsDeviceType.choices,
        default=AnalyticsDeviceType.UNKNOWN,
    )
    path = models.CharField(max_length=255, blank=True)
    user_agent = models.TextField(blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["created_at"]),
            models.Index(fields=["place"]),
            models.Index(fields=["device_type"]),
            models.Index(fields=["is_registered"]),
        ]
        verbose_name = "Place view event"
        verbose_name_plural = "Place view events"
