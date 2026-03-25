from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from apps.ingestion.services.importers import import_pet_places_from_csv


class Command(BaseCommand):
    help = "Importa lugares para el mapa público desde un CSV local."

    def add_arguments(self, parser):
        parser.add_argument("csv_path")
        parser.add_argument("--dataset-name", dest="dataset_name")
        parser.add_argument("--default-source", dest="default_source", default="manual_seed")
        parser.add_argument("--update-existing", action="store_true")
        parser.add_argument("--dry-run", action="store_true")

    def handle(self, *args, **options):
        try:
            with transaction.atomic():
                summary = import_pet_places_from_csv(
                    options["csv_path"],
                    dataset_name=options.get("dataset_name"),
                    default_source=options["default_source"],
                    update_existing=options["update_existing"],
                )
                if options["dry_run"]:
                    transaction.set_rollback(True)
        except Exception as exc:  # noqa: BLE001
            raise CommandError(str(exc)) from exc

        status_style = self.style.WARNING if options["dry_run"] else self.style.SUCCESS
        prefix = "Validación finalizada" if options["dry_run"] else "Importación finalizada"
        self.stdout.write(
            status_style(
                f"{prefix}: "
                f"procesados={summary.processed}, "
                f"creados={summary.created}, "
                f"actualizados={summary.updated}, "
                f"ignorados={summary.ignored}, "
                f"errores={summary.failed}, "
                f"pendientes_revision={summary.geocoding_needed}."
            )
        )

        for message in summary.error_messages:
            self.stdout.write(self.style.ERROR(message))
