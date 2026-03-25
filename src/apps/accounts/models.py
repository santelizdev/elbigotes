from datetime import timedelta

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

from apps.accounts.managers import UserManager
from apps.core.models import TimeStampedModel
from apps.lost_pets.choices import LostPetSex, LostPetSpecies


class UserRole(models.TextChoices):
    PLATFORM_ADMIN = "platform_admin", "Platform admin"
    MODERATOR = "moderator", "Moderator"
    ANALYST = "analyst", "Analyst"
    BUSINESS_OWNER = "business_owner", "Business owner"
    PET_OWNER = "pet_owner", "Pet owner"


class BusinessKind(models.TextChoices):
    VETERINARY = "veterinary", "Veterinaria"
    DAYCARE = "daycare", "Guarderia"
    EMERGENCY = "emergency", "Emergencia 24/7"
    SHELTER = "shelter", "Refugio"
    PARK = "park", "Parque"


class MembershipStatus(models.TextChoices):
    GRACE = "grace", "Grace period"
    ACTIVE = "active", "Active membership"
    PAST_DUE = "past_due", "Past due"
    FREE_FOREVER = "free_forever", "Free forever"


FREE_BUSINESS_KINDS = {BusinessKind.SHELTER, BusinessKind.PARK}
GRACE_PERIOD_DAYS = 30


class User(AbstractUser, TimeStampedModel):
    """
    Usuario propio desde el inicio para evitar migraciones dolorosas cuando aparezcan roles o SSO.
    """

    email = models.EmailField(unique=True)
    email_verified = models.BooleanField(default=False)
    role = models.CharField(max_length=32, choices=UserRole.choices, default=UserRole.MODERATOR)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta:
        ordering = ["email"]
        verbose_name = "User"
        verbose_name_plural = "Users"

    def save(self, *args, **kwargs):
        self.username = self.email
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.email

    @property
    def is_internal_user(self) -> bool:
        return self.role in {
            UserRole.PLATFORM_ADMIN,
            UserRole.MODERATOR,
            UserRole.ANALYST,
        }

    @property
    def is_business_owner(self) -> bool:
        return self.role == UserRole.BUSINESS_OWNER

    @property
    def is_pet_owner(self) -> bool:
        return self.role == UserRole.PET_OWNER


class BusinessProfile(TimeStampedModel):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="business_profile",
    )
    place = models.OneToOneField(
        "places.Place",
        on_delete=models.SET_NULL,
        related_name="business_profile",
        null=True,
        blank=True,
    )
    business_name = models.CharField(max_length=160)
    business_kind = models.CharField(max_length=20, choices=BusinessKind.choices)
    phone = models.CharField(max_length=40)
    commune = models.CharField(max_length=120)
    region = models.CharField(max_length=120, default="Región Metropolitana")
    website = models.URLField(blank=True)
    membership_status = models.CharField(
        max_length=20,
        choices=MembershipStatus.choices,
        default=MembershipStatus.GRACE,
    )
    grace_expires_at = models.DateTimeField(null=True, blank=True)
    marketing_opt_in = models.BooleanField(default=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["business_name"]
        verbose_name = "Business profile"
        verbose_name_plural = "Business profiles"

    @property
    def is_billable(self) -> bool:
        return self.business_kind not in FREE_BUSINESS_KINDS

    def apply_membership_policy(self):
        if self.business_kind in FREE_BUSINESS_KINDS:
            self.membership_status = MembershipStatus.FREE_FOREVER
            self.grace_expires_at = None
            return

        if self.membership_status == MembershipStatus.FREE_FOREVER:
            self.membership_status = MembershipStatus.GRACE

        if self.grace_expires_at is None:
            self.grace_expires_at = timezone.now() + timedelta(days=GRACE_PERIOD_DAYS)

    def save(self, *args, **kwargs):
        self.apply_membership_policy()
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.business_name


class PetOwnerProfile(TimeStampedModel):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="pet_owner_profile",
    )
    phone = models.CharField(max_length=40)
    address_line = models.CharField(max_length=255, blank=True)
    commune = models.CharField(max_length=120, blank=True)
    region = models.CharField(max_length=120, default="Región Metropolitana")
    marketing_opt_in = models.BooleanField(default=True)

    class Meta:
        ordering = ["user__email"]
        verbose_name = "Pet owner profile"
        verbose_name_plural = "Pet owner profiles"

    def __str__(self) -> str:
        return self.user.email


class PetProfile(TimeStampedModel):
    owner = models.ForeignKey(
        PetOwnerProfile,
        on_delete=models.CASCADE,
        related_name="pets",
    )
    name = models.CharField(max_length=120)
    species = models.CharField(max_length=20, choices=LostPetSpecies.choices)
    breed = models.CharField(max_length=120, blank=True)
    sex = models.CharField(max_length=20, choices=LostPetSex.choices, default=LostPetSex.UNKNOWN)
    birth_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Pet profile"
        verbose_name_plural = "Pet profiles"

    def __str__(self) -> str:
        return self.name
