from django.core.management.base import BaseCommand

from apps.ingestion.services.normalization import resolve_category_pair
from apps.places.models import Place


class Command(BaseCommand):
    help = "Normaliza categorías y subcategorías leyendo metadata cruda o slugs actuales."

    def handle(self, *args, **options):
        normalized = 0
        skipped = 0

        for place in Place.objects.select_related("category", "subcategory"):
            raw_category = place.metadata.get("raw_category") or place.category.slug
            raw_subcategory = place.metadata.get("raw_subcategory") or (place.subcategory.slug if place.subcategory else "")

            try:
                category, subcategory = resolve_category_pair(raw_category, raw_subcategory)
            except ValueError:
                skipped += 1
                continue

            if place.category_id == category.id and place.subcategory_id == getattr(subcategory, "id", None):
                skipped += 1
                continue

            place.category = category
            place.subcategory = subcategory
            place.save(update_fields=["category", "subcategory", "updated_at"])
            normalized += 1

        self.stdout.write(
            self.style.SUCCESS(f"Normalización completada. {normalized} fichas actualizadas, {skipped} omitidas.")
        )

