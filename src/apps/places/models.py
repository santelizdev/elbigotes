from zoneinfo import ZoneInfo

from django.conf import settings
from django.contrib.gis.db import models as gis_models
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Q
from django.utils import timezone

from apps.core.models import TimeStampedModel
from apps.core.utils.slugs import generate_unique_slug
from apps.ingestion.models import Source
from apps.places.chile_locations import commune_belongs_to_region
from apps.places.choices import (
    ContactPointKind,
    DataIssueSeverity,
    DuplicateCandidateStatus,
    FeaturedCatalogItemType,
    PlaceStatus,
    PlaceVerificationStatus,
    PublicPetOperationCreatorType,
    PublicPetOperationStatus,
    PublicPetOperationType,
)
from apps.taxonomy.models import Category, Subcategory

PUBLIC_PET_OPERATIONS_TIMEZONE = ZoneInfo("America/Santiago")


def get_public_pet_operations_now():
    return timezone.localtime(timezone.now(), PUBLIC_PET_OPERATIONS_TIMEZONE)


class PublicPetOperationQuerySet(models.QuerySet):
    def with_related(self):
        return self

    def non_draft(self):
        return self.exclude(status=PublicPetOperationStatus.DRAFT)

    def publicly_visible(self, now=None):
        current_time = now or get_public_pet_operations_now()
        return self.filter(status=PublicPetOperationStatus.PUBLISHED).filter(
            Q(ends_at__gte=current_time)
            | Q(ends_at__isnull=True, starts_at__gte=current_time)
        )

    def expirable(self, now=None):
        current_time = now or get_public_pet_operations_now()
        return self.filter(status=PublicPetOperationStatus.PUBLISHED).filter(
            Q(ends_at__lt=current_time)
            | Q(ends_at__isnull=True, starts_at__lt=current_time)
        )


class Place(TimeStampedModel):
    # Horario crudo entregado por Google u otra fuente.
    # Se conserva para trazabilidad y debugging.
    opening_hours_raw = models.JSONField(
        default=dict,
        blank=True,
        help_text="Horario crudo de la fuente externa, sin normalizar.",
    )

    # Horario interno normalizado para consumo de producto/API.
    # Estructura esperada:
    # {
    #   "monday": [{"open": "09:00", "close": "18:00"}],
    #   "tuesday": [],
    #   ...
    # }
    opening_hours_normalized = models.JSONField(
        default=dict,
        blank=True,
        help_text="Horario estructurado normalizado para cálculos internos.",
    )

    # Zona horaria del lugar. Por ahora default Chile.
    timezone_name = models.CharField(
        max_length=64,
        default="America/Santiago",
        help_text="Zona horaria IANA usada para cálculos de apertura.",
    )

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
    verification_status = models.CharField(
        max_length=24,
        choices=PlaceVerificationStatus.choices,
        default=PlaceVerificationStatus.UNVERIFIED,
    )
    is_verified = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)
    is_emergency_service = models.BooleanField(default=False)
    is_open_24_7 = models.BooleanField(default=False)
    google_rating = models.DecimalField(
        max_digits=2,
        decimal_places=1,
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(5)],
    )
    google_reviews_count = models.PositiveIntegerField(default=0)
    google_maps_url = models.URLField(blank=True)
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
        cleaned_parts: list[str] = []
        seen_normalized: set[str] = set()

        for part in parts:
            normalized = " ".join(str(part or "").strip().lower().split())
            if not normalized or normalized in seen_normalized:
                continue
            seen_normalized.add(normalized)
            cleaned_parts.append(str(part).strip())

        return ", ".join(cleaned_parts)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_unique_slug(self, self.name)

        if self.verification_status == PlaceVerificationStatus.UNVERIFIED and self.is_verified:
            self.verification_status = PlaceVerificationStatus.VERIFIED
        elif self.verification_status == PlaceVerificationStatus.VERIFIED:
            self.is_verified = True
        else:
            self.is_verified = False

        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.name

    def is_open_now_at(self, dt=None) -> bool:
        """
        Determina si el lugar está abierto en el instante indicado.

        Reglas:
        - Si is_open_24_7 es True, retorna True.
        - Si no hay horario normalizado, retorna False.
        - Usa timezone_name del lugar; por defecto America/Santiago.
        - Soporta franjas que cruzan medianoche.
        """
        from apps.places.services.hours import is_place_open_now

        return is_place_open_now(self, dt=dt)


class FeaturedCatalogItem(TimeStampedModel):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True)
    description = models.TextField(blank=True)
    item_type = models.CharField(
        max_length=20,
        choices=FeaturedCatalogItemType.choices,
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="featured_catalog_items",
    )
    image = models.ImageField(upload_to="places/featured-catalog/%Y/%m/", blank=True)
    price_label = models.CharField(max_length=120, blank=True)
    cta_label = models.CharField(max_length=120, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["title"]
        verbose_name = "Featured catalog item"
        verbose_name_plural = "Featured catalog items"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_unique_slug(self, self.title)
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.title


class PlaceFeaturedCatalogItem(TimeStampedModel):
    place = models.ForeignKey(
        Place,
        on_delete=models.CASCADE,
        related_name="featured_catalog_assignments",
    )
    featured_item = models.ForeignKey(
        FeaturedCatalogItem,
        on_delete=models.CASCADE,
        related_name="place_assignments",
    )
    custom_price_label = models.CharField(max_length=120, blank=True)
    custom_cta_url = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["sort_order", "id"]
        constraints = [
            models.UniqueConstraint(
                fields=["place", "featured_item"],
                name="places_featured_catalog_assignment_unique_pair",
            )
        ]
        verbose_name = "Place featured catalog item"
        verbose_name_plural = "Place featured catalog items"

    def clean(self):
        if (
            self.place_id
            and self.featured_item_id
            and self.place.category_id != self.featured_item.category_id
        ):
            raise ValidationError(
                {
                    "featured_item": (
                        "La categoría del item destacado debe coincidir con la categoría del place."
                    )
                }
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    @property
    def effective_price_label(self) -> str:
        return self.custom_price_label or self.featured_item.price_label

    @property
    def effective_cta_url(self) -> str:
        return self.custom_cta_url

    def __str__(self) -> str:
        return f"{self.place.name} - {self.featured_item.title}"


class PublicPetOperation(TimeStampedModel):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True)
    operation_type = models.CharField(
        max_length=20,
        choices=PublicPetOperationType.choices,
    )
    address = models.CharField(max_length=255)
    commune = models.CharField(max_length=120)
    region = models.CharField(max_length=120)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    starts_at = models.DateTimeField()
    ends_at = models.DateTimeField(null=True, blank=True)
    requirements = models.TextField(blank=True)
    image = models.ImageField(upload_to="places/public-operations/%Y/%m/", blank=True)
    creator_type = models.CharField(
        max_length=20,
        choices=PublicPetOperationCreatorType.choices,
    )
    creator_name = models.CharField(max_length=160)
    status = models.CharField(
        max_length=20,
        choices=PublicPetOperationStatus.choices,
        default=PublicPetOperationStatus.DRAFT,
    )

    objects = PublicPetOperationQuerySet.as_manager()

    class Meta:
        ordering = ["starts_at", "title"]
        indexes = [
            models.Index(fields=["slug"], name="places_publ_slug_098f67_idx"),
            models.Index(fields=["status", "starts_at"], name="places_publ_status__ec73ee_idx"),
            models.Index(
                fields=["operation_type", "commune"],
                name="places_publ_operati_651f44_idx",
            ),
        ]
        verbose_name = "Public pet operation"
        verbose_name_plural = "Public pet operations"

    def clean(self):
        if (self.latitude is None) ^ (self.longitude is None):
            raise ValidationError(
                "Debes informar latitude y longitude juntas o dejar ambas vacías."
            )

        if self.ends_at and self.ends_at < self.starts_at:
            raise ValidationError(
                {"ends_at": "La fecha de término no puede ser anterior a starts_at."}
            )

        if self.region and self.commune and not commune_belongs_to_region(self.region, self.commune):
            raise ValidationError(
                {"commune": "La comuna seleccionada no pertenece a la región indicada."}
            )

        if self.status == PublicPetOperationStatus.PUBLISHED and (
            self.latitude is None or self.longitude is None
        ):
            raise ValidationError(
                {"latitude": "Debes confirmar una dirección con coordenadas antes de publicar el operativo."}
            )

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_unique_slug(self, self.title)
        self.full_clean()
        super().save(*args, **kwargs)

    @property
    def is_expired(self) -> bool:
        reference_date = self.ends_at or self.starts_at
        return timezone.localtime(reference_date, PUBLIC_PET_OPERATIONS_TIMEZONE) < get_public_pet_operations_now()

    @property
    def is_publicly_visible(self) -> bool:
        if self.status != PublicPetOperationStatus.PUBLISHED:
            return False
        return not self.is_expired

    def __str__(self) -> str:
        return self.title


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
