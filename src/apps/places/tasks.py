from celery import shared_task

from apps.places.services.public_operations import expire_public_pet_operations


@shared_task
def expire_public_pet_operations_task() -> int:
    return expire_public_pet_operations()
