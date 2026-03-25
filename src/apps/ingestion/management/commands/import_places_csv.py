from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from apps.ingestion.services.importers import import_places_from_csv


class Command(BaseCommand):
    help = "Importa lugares desde CSV manteniendo trazabilidad por fuente y dataset."

    def add_arguments(self, parser):
        parser.add_argument("csv_path")
        parser.add_argument("--source", required=True, dest="source_slug")
        parser.add_argument("--dataset-slug", dest="dataset_slug")
        parser.add_argument("--dataset-name", dest="dataset_name")
        parser.add_argument("--update-existing", action="store_true")
        parser.add_argument("--dry-run", action="store_true")

    def handle(self, *args, **options):
        summary = None
        try:
            with transaction.atomic():
                summary = import_places_from_csv(
                    options["csv_path"],
                    source_slug=options["source_slug"],
                    dataset_slug=options.get("dataset_slug"),
                    dataset_name=options.get("dataset_name"),
                    update_existing=options["update_existing"],
                )
                if options["dry_run"]:
                    transaction.set_rollback(True)
                    self.stdout.write(
                        self.style.WARNING(
                            "Dry run completado: "
                            f"{summary.created} creados, "
                            f"{summary.updated} actualizados, "
                            f"{summary.skipped} omitidos, "
                            f"{summary.failed} fallidos."
                        )
                    )
                    return
        except RuntimeError as exc:
            if str(exc) != "dry-run":
                raise
        except Exception as exc:  # noqa: BLE001
            raise CommandError(str(exc)) from exc

        self.stdout.write(
            self.style.SUCCESS(
                "Importación finalizada: "
                f"{summary.created} creados, "
                f"{summary.updated} actualizados, "
                f"{summary.skipped} omitidos, "
                f"{summary.failed} fallidos, "
                f"{summary.geocoding_needed} pendientes de geocodificación."
            )
        )
