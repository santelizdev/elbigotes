from django.core.management.base import BaseCommand

from apps.ingestion.services.geocoding import geocode_place_instance
from apps.places.models import Place


class Command(BaseCommand):
    help = "Geocodifica fichas sin coordenadas usando la dirección disponible."

    def add_arguments(self, parser):
        parser.add_argument("--limit", type=int, default=50)

    def handle(self, *args, **options):
        queryset = Place.objects.filter(location__isnull=True).exclude(
            formatted_address=""
        ) | Place.objects.filter(location__isnull=True).exclude(street_address="")
        limit = options["limit"]
        processed = 0

        for place in queryset.distinct()[:limit]:
            geocode_place_instance(place)
            processed += 1

        self.stdout.write(self.style.SUCCESS(f"Geocodificación ejecutada para {processed} lugares."))
