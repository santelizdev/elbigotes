from django.db import models


class TimeStampedModel(models.Model):
    """
    Base abstracta para homogeneizar auditoría temporal.
    Tener estos campos consistentes simplifica admin, ordenamientos y futuras auditorías.
    """

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

