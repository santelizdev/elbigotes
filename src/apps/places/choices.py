from django.db import models


class PlaceStatus(models.TextChoices):
    DRAFT = "draft", "Draft"
    ACTIVE = "active", "Active"
    ARCHIVED = "archived", "Archived"


class PlaceVerificationStatus(models.TextChoices):
    UNVERIFIED = "unverified", "Unverified"
    CLAIM_REQUESTED = "claim_requested", "Claim requested"
    VERIFIED = "verified", "Verified"


class ContactPointKind(models.TextChoices):
    PHONE = "phone", "Phone"
    WHATSAPP = "whatsapp", "WhatsApp"
    EMAIL = "email", "Email"
    WEBSITE = "website", "Website"
    INSTAGRAM = "instagram", "Instagram"
    FACEBOOK = "facebook", "Facebook"


class DataIssueSeverity(models.TextChoices):
    INFO = "info", "Info"
    WARNING = "warning", "Warning"
    CRITICAL = "critical", "Critical"


class DuplicateCandidateStatus(models.TextChoices):
    OPEN = "open", "Open"
    CONFIRMED = "confirmed", "Confirmed"
    DISMISSED = "dismissed", "Dismissed"


class FeaturedCatalogItemType(models.TextChoices):
    PRODUCT = "product", "Product"
    SERVICE = "service", "Service"
    PROMO = "promo", "Promo"


class PublicPetOperationType(models.TextChoices):
    VACCINATION = "vaccination", "Vaccination"
    STERILIZATION = "sterilization", "Sterilization"
    MICROCHIP = "microchip", "Microchip"
    ADOPTION = "adoption", "Adoption"
    OTHER = "other", "Other"


class PublicPetOperationStatus(models.TextChoices):
    DRAFT = "draft", "Draft"
    PUBLISHED = "published", "Published"
    EXPIRED = "expired", "Expired"


class PublicPetOperationCreatorType(models.TextChoices):
    PUBLIC = "public", "Public"
    PRIVATE = "private", "Private"
