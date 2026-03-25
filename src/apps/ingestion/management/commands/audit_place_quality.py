from django.core.management.base import BaseCommand

from apps.places.services.quality import audit_places


class Command(BaseCommand):
    help = "Ejecuta auditoría mínima de calidad de datos sobre lugares."

    def handle(self, *args, **options):
        count = audit_places()
        self.stdout.write(self.style.SUCCESS(f"Auditoría completada sobre {count} lugares."))

