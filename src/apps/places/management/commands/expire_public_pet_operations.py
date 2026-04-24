from django.core.management.base import BaseCommand

from apps.places.services.public_operations import expire_public_pet_operations


class Command(BaseCommand):
    help = "Marca como expirados los operativos públicos ya vencidos sin borrarlos de la base."

    def handle(self, *args, **options):
        expired_count = expire_public_pet_operations()
        self.stdout.write(
            self.style.SUCCESS(f"Se expiraron {expired_count} operativos públicos.")
        )
