from django.core.management.base import BaseCommand

from apps.places.services.duplicates import rebuild_duplicate_candidates


class Command(BaseCommand):
    help = "Reconstruye candidatos de duplicados básicos para moderación."

    def handle(self, *args, **options):
        total = rebuild_duplicate_candidates()
        self.stdout.write(self.style.SUCCESS(f"Se generaron o actualizaron {total} candidatos de duplicado."))

