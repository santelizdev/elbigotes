import argparse
from django.core.management.base import BaseCommand
from django.db import transaction

from apps.ingestion.models import ImportedPlaceRecord
from apps.places.services.location_normalization import detect_commune_for_imported_record

class Command(BaseCommand):
    help = "Normaliza y asigna comuna detectada a registros en staging (ImportedPlaceRecord)"

    def add_arguments(self, parser):
        parser.add_argument("--dataset", required=True, help="Slug del SourceDataset a procesar")
        parser.add_argument("--dry-run", action="store_true", help="Muestra qué cambiaría sin escribir en DB")
        parser.add_argument("--limit", type=int, default=None, help="Límite máximo de registros a procesar")

    def handle(self, *args, **options):
        dataset_slug = options["dataset"]
        dry_run = options["dry_run"]
        limit = options["limit"]

        qs = ImportedPlaceRecord.objects.filter(dataset__slug=dataset_slug).order_by("id")
        if limit:
            qs = qs[:limit]

        total = qs.count()
        if total == 0:
            self.stdout.write(self.style.WARNING(f"No hay registros en el dataset '{dataset_slug}'."))
            return

        self.stdout.write(f"Iniciando normalización territorial para {total} registros en staging{' [DRY RUN]' if dry_run else ''}")
        stats = {"updated": 0, "skipped": 0, "errors": 0}

        for record in qs.iterator():
            try:
                detection = detect_commune_for_imported_record(record)
                
                # Check if it's already there
                meta = record.raw_payload.get("meta", {})
                current_detected = meta.get("commune_detected")
                if current_detected == detection["commune"] and "commune_detected" in meta:
                    stats["skipped"] += 1
                    continue

                if dry_run:
                    self.stdout.write(f"WOULD UPDATE: {record.raw_name}")
                    self.stdout.write(f"  commune detected: {detection['commune']}")
                    self.stdout.write(f"  source: {detection['source']}")
                    stats["updated"] += 1
                    continue

                with transaction.atomic():
                    payload = record.raw_payload
                    meta = payload.get("meta", {})
                    meta["commune_detected"] = detection["commune"]
                    meta["commune_source"] = detection["source"]
                    meta["commune_confidence"] = detection["confidence"]
                    meta["needs_location_review"] = detection["needs_review"]
                    payload["meta"] = meta
                    
                    record.raw_payload = payload
                    record.save(update_fields=["raw_payload", "updated_at"])
                    
                stats["updated"] += 1

            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error procesando {record.raw_name}: {e}"))
                stats["errors"] += 1

        self.stdout.write("=" * 50)
        self.stdout.write("NORMALIZACIÓN EN STAGING FINALIZADA" + (" [DRY RUN]" if dry_run else ""))
        self.stdout.write(f"  Actualizados: {stats['updated']}")
        self.stdout.write(f"  Saltados:     {stats['skipped']}")
        self.stdout.write(f"  Errores:      {stats['errors']}")
