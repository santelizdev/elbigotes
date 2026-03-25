from django.db import models


class LostPetSpecies(models.TextChoices):
    DOG = "dog", "Dog"
    CAT = "cat", "Cat"
    OTHER = "other", "Other"


class LostPetSex(models.TextChoices):
    MALE = "male", "Male"
    FEMALE = "female", "Female"
    UNKNOWN = "unknown", "Unknown"


class LostPetReportStatus(models.TextChoices):
    LOST = "lost", "Lost"
    SIGHTED = "sighted", "Sighted"
    FOUND = "found", "Found"
    CLOSED = "closed", "Closed"


class LostPetModerationStatus(models.TextChoices):
    PENDING = "pending", "Pending review"
    APPROVED = "approved", "Approved"
    REJECTED = "rejected", "Rejected"
