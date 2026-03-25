from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db import models

from apps.core.models import TimeStampedModel
from apps.core.utils.slugs import generate_unique_slug


class MembershipAudience(models.TextChoices):
    BUSINESS = "business", "Business"
    PET_OWNER = "pet_owner", "Pet owner"


class MembershipBillingInterval(models.TextChoices):
    MONTHLY = "monthly", "Monthly"
    YEARLY = "yearly", "Yearly"
    ONE_TIME = "one_time", "One time"
    CUSTOM = "custom", "Custom"


class MembershipAssignmentStatus(models.TextChoices):
    TRIAL = "trial", "Trial"
    ACTIVE = "active", "Active"
    PAST_DUE = "past_due", "Past due"
    CANCELLED = "cancelled", "Cancelled"
    EXPIRED = "expired", "Expired"


class MembershipPlan(TimeStampedModel):
    name = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(max_length=220, unique=True)
    audience = models.CharField(max_length=20, choices=MembershipAudience.choices)
    description = models.TextField(blank=True)
    billing_interval = models.CharField(
        max_length=20,
        choices=MembershipBillingInterval.choices,
        default=MembershipBillingInterval.MONTHLY,
    )
    price_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    currency = models.CharField(max_length=8, default="CLP")
    grace_days = models.PositiveIntegerField(default=0)
    max_places = models.PositiveIntegerField(default=1)
    max_pets = models.PositiveIntegerField(default=1)
    is_public = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["audience", "price_amount", "name"]
        verbose_name = "Membership plan"
        verbose_name_plural = "Membership plans"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_unique_slug(self, self.name)
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.name


class MembershipAssignmentQuerySet(models.QuerySet):
    def for_owner(self, owner):
        content_type = ContentType.objects.get_for_model(owner, for_concrete_model=False)
        return self.filter(
            owner_content_type=content_type,
            owner_object_id=owner.pk,
        ).select_related("plan")


class MembershipAssignment(TimeStampedModel):
    plan = models.ForeignKey(
        MembershipPlan,
        on_delete=models.PROTECT,
        related_name="assignments",
    )
    owner_content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        related_name="membership_assignments",
    )
    owner_object_id = models.PositiveBigIntegerField()
    owner = GenericForeignKey("owner_content_type", "owner_object_id")
    status = models.CharField(
        max_length=20,
        choices=MembershipAssignmentStatus.choices,
        default=MembershipAssignmentStatus.TRIAL,
    )
    starts_at = models.DateTimeField()
    ends_at = models.DateTimeField(null=True, blank=True)
    renews_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    objects = MembershipAssignmentQuerySet.as_manager()

    class Meta:
        ordering = ["-starts_at", "-created_at"]
        indexes = [
            models.Index(fields=["owner_content_type", "owner_object_id"]),
            models.Index(fields=["status"]),
        ]
        verbose_name = "Membership assignment"
        verbose_name_plural = "Membership assignments"

    def clean(self):
        if self.owner is None:
            raise ValidationError(
                {"owner_object_id": "Debes asociar una membresía a un perfil válido."}
            )

        owner_model = self.owner.__class__.__name__
        if owner_model == "BusinessProfile":
            expected_audience = MembershipAudience.BUSINESS
        elif owner_model == "PetOwnerProfile":
            expected_audience = MembershipAudience.PET_OWNER
        else:
            raise ValidationError({"owner_object_id": "Este tipo de perfil no soporta membresías."})

        if self.plan.audience != expected_audience:
            raise ValidationError(
                {"plan": "El plan seleccionado no coincide con el tipo de perfil asociado."}
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.plan.name} -> {self.owner}"
