from django.utils import timezone

from apps.places.choices import PublicPetOperationStatus
from apps.places.models import PublicPetOperation, get_public_pet_operations_now


def expire_public_pet_operations(*, now=None) -> int:
    current_time = now or get_public_pet_operations_now()
    return PublicPetOperation.objects.expirable(now=current_time).update(
        status=PublicPetOperationStatus.EXPIRED,
        updated_at=timezone.now(),
    )
