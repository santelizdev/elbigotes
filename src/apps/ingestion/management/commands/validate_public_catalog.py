from django.core.management.base import BaseCommand, CommandError
from django.db.models import Q

from apps.ingestion.models import ImportedPlaceRecord, ImportRecordStatus, SourceDataset
from apps.places.models import Place
from apps.taxonomy.models import Category

REQUIRED_PUBLIC_CATEGORY_SLUGS = (
    "veterinarias",
    "refugios-albergues",
    "parques-pet-friendly",
    "emergencias-veterinarias",
    "guarderias",
)


class Command(BaseCommand):
    help = "Valida taxonomía, datasets y preparación del catálogo público antes de publicar."

    def add_arguments(self, parser):
        parser.add_argument(
            "--fail-on-warning",
            action="store_true",
            help="Retorna error si se detectan advertencias operativas.",
        )

    def handle(self, *args, **options):
        warnings: list[str] = []

        category_slugs = set(Category.objects.filter(is_active=True).values_list("slug", flat=True))
        missing_categories = sorted(set(REQUIRED_PUBLIC_CATEGORY_SLUGS) - category_slugs)
        if missing_categories:
            warnings.append(
                "Faltan categorías públicas requeridas: " + ", ".join(missing_categories)
            )

        active_places = Place.objects.filter(status="active")
        draft_places = Place.objects.filter(status="draft")
        archived_places = Place.objects.filter(status="archived")
        imported_records = ImportedPlaceRecord.objects.count()
        failed_records = ImportedPlaceRecord.objects.filter(
            status=ImportRecordStatus.FAILED
        ).count()
        pending_records = ImportedPlaceRecord.objects.filter(
            status=ImportRecordStatus.PENDING
        ).count()
        records_without_place = ImportedPlaceRecord.objects.filter(
            imported_place__isnull=True
        ).count()
        active_datasets_without_records = SourceDataset.objects.filter(
            is_active=True,
            import_records__isnull=True,
        ).count()
        active_places_without_address = active_places.filter(
            Q(formatted_address="") & Q(street_address="")
        ).count()
        active_places_without_source = active_places.filter(source__isnull=True).count()

        for category_slug in REQUIRED_PUBLIC_CATEGORY_SLUGS:
            category_count = active_places.filter(category__slug=category_slug).count()
            if category_count == 0:
                warnings.append(
                    f"No hay lugares activos visibles para la categoría '{category_slug}'."
                )

        if active_places_without_address:
            warnings.append(
                "Hay "
                f"{active_places_without_address} "
                "lugares activos sin dirección pública visible."
            )
        if active_places_without_source:
            warnings.append(
                f"Hay {active_places_without_source} lugares activos sin fuente asignada."
            )
        if failed_records:
            warnings.append(f"Hay {failed_records} registros importados en estado failed.")
        if pending_records:
            warnings.append(f"Hay {pending_records} registros importados en estado pending.")
        if records_without_place:
            warnings.append(
                f"Hay {records_without_place} registros importados sin vínculo a Place."
            )
        if active_datasets_without_records:
            warnings.append(
                f"Hay {active_datasets_without_records} datasets activos sin registros importados."
            )

        self.stdout.write(self.style.MIGRATE_HEADING("Resumen catálogo público"))
        self.stdout.write(f"Categorias activas: {Category.objects.filter(is_active=True).count()}")
        self.stdout.write(f"Lugares activos: {active_places.count()}")
        self.stdout.write(f"Lugares draft: {draft_places.count()}")
        self.stdout.write(f"Lugares archivados: {archived_places.count()}")
        self.stdout.write(f"ImportedPlaceRecord: {imported_records}")
        self.stdout.write(
            f"SourceDataset activos: {SourceDataset.objects.filter(is_active=True).count()}"
        )

        if warnings:
            self.stdout.write("")
            self.stdout.write(self.style.WARNING("Advertencias detectadas:"))
            for warning in warnings:
                self.stdout.write(f"- {warning}")
            if options["fail_on_warning"]:
                raise CommandError("La validación del catálogo público detectó advertencias.")
            return

        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS("Catálogo público listo para revisión final."))
