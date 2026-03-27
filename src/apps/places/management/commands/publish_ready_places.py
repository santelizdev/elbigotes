from django.core.management.base import BaseCommand

from apps.places.services.publishing import get_publishable_places, publish_ready_places


class Command(BaseCommand):
    help = "Publica en bloque fichas draft que ya están listas para mostrarse en el catálogo."

    def add_arguments(self, parser):
        parser.add_argument(
            "--include-address-only",
            action="store_true",
            help="Incluye fichas con dirección completa aunque todavía no tengan coordenadas.",
        )
        parser.add_argument(
            "--dataset",
            help="Limita la publicación a fichas importadas desde un dataset específico.",
        )
        parser.add_argument(
            "--ignore-review-status",
            action="store_true",
            help="Publica aunque metadata.review_status no sea 'ready'. Úsalo solo para lotes validados.",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Solo informa cuántas fichas serían publicadas sin modificar datos.",
        )

    def handle(self, *args, **options):
        include_address_only = options["include_address_only"]
        dataset_slug = options["dataset"]
        ignore_review_status = options["ignore_review_status"]
        dry_run = options["dry_run"]

        queryset = get_publishable_places(
            include_address_only=include_address_only,
            dataset_slug=dataset_slug,
            ignore_review_status=ignore_review_status,
        )
        count = queryset.count()

        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    f"Dry run: {count} fichas draft cumplen criterio de publicación."
                )
            )
            return

        updated = publish_ready_places(
            include_address_only=include_address_only,
            dataset_slug=dataset_slug,
            ignore_review_status=ignore_review_status,
        )
        self.stdout.write(
            self.style.SUCCESS(f"Se publicaron {updated} fichas draft.")
        )
