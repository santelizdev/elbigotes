import argparse

from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import Q

from apps.places.models import Place
from apps.places.services.location_normalization import detect_commune_for_place


class Command(BaseCommand):
    help = "Recalcula y normaliza la comuna de los Places basándose en su dirección física."

    def add_arguments(self, parser):
        parser.add_argument("--dry-run", action="store_true", help="Muestra qué cambiaría sin escribir en la DB")
        parser.add_argument("--limit", type=int, default=None, help="Límite máximo de registros a procesar")
        parser.add_argument("--dataset", default=None, help="Filtrar por metadata__imported_from")
        parser.add_argument("--category", default=None, help="Filtrar por category__slug")
        parser.add_argument("--only-region", default=None, help="Filtrar por region actual del Place")
        parser.add_argument("--force", action="store_true", help="Obliga la actualización aunque confidencia sea baja")
        parser.add_argument("--unsafe", action="store_true", help="Desactiva el safe-mode. En safe-mode, solo se permiten actualizaciones en RM donde old_commune sea Santiago y new_commune sea más específica.")

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        limit = options["limit"]
        dataset = options["dataset"]
        category = options["category"]
        only_region = options["only_region"]
        force = options["force"]

        qs = Place.objects.all().order_by("id")

        if dataset:
            qs = qs.filter(metadata__imported_from=dataset)
        if category:
            qs = qs.filter(category__slug=category)
        if only_region:
            qs = qs.filter(region=only_region)
            
        if limit:
            qs = qs[:limit]

        total = qs.count()
        if total == 0:
            self.stdout.write(self.style.WARNING("No hay Places que coincidan con los filtros."))
            return

        self.stdout.write(f"Iniciando normalización territorial para {total} lugares{' [DRY RUN]' if dry_run else ''}")
        
        stats = {"updated": 0, "skipped_same": 0, "skipped_low_confidence": 0, "errors": 0}

        for place in qs.iterator():
            try:
                detection = detect_commune_for_place(place)
                new_commune = detection["commune"]
                new_region = detection["region"]
                source = detection["source"]
                confidence = detection["confidence"]
                needs_review = detection["needs_review"]

                if not new_commune:
                    stats["skipped_low_confidence"] += 1
                    continue

                if place.commune == new_commune and place.region == new_region:
                    stats["skipped_same"] += 1
                    continue
                    
                if confidence == "low" and not force:
                    stats["skipped_low_confidence"] += 1
                    continue

                if not force and not options["unsafe"]:
                    # Safe Mode por defecto para Región Metropolitana
                    is_rm = place.region in ("Región Metropolitana", "Santiago Metropolitan Region") or new_region == "Región Metropolitana"
                    if is_rm:
                        is_old_santiago = (place.commune.lower() == "santiago")
                        is_new_santiago = (new_commune.lower() == "santiago")
                        
                        if is_new_santiago:
                            # Evitar cambios hacia Santiago (pérdida de especificidad)
                            stats["skipped_low_confidence"] += 1
                            continue
                            
                        if not is_old_santiago:
                            # Evitar cambios cuando old_commune ya es válida (no es Santiago)
                            stats["skipped_low_confidence"] += 1
                            continue

                if dry_run:
                    self.stdout.write(f"WOULD UPDATE: {place.name}")
                    self.stdout.write(f"  old commune: {place.commune}")
                    self.stdout.write(f"  new commune: {new_commune}")
                    self.stdout.write(f"  source: {source}")
                    self.stdout.write(f"  confidence: {confidence}")
                    stats["updated"] += 1
                    continue

                with transaction.atomic():
                    meta = place.metadata or {}
                    meta["commune_target"] = place.commune # guardamos el original como history
                    meta["commune_detected"] = new_commune
                    meta["commune_source"] = source
                    meta["commune_confidence"] = confidence
                    meta["needs_location_review"] = needs_review
                    
                    place.metadata = meta
                    place.commune = new_commune
                    place.region = new_region
                    place.save(update_fields=["commune", "region", "metadata", "updated_at"])
                    
                self.stdout.write(self.style.SUCCESS(f"UPDATED: {place.name} -> {new_commune}"))
                stats["updated"] += 1

            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error procesando {place.name}: {e}"))
                stats["errors"] += 1

        self.stdout.write("=" * 50)
        self.stdout.write("NORMALIZACIÓN FINALIZADA" + (" [DRY RUN]" if dry_run else ""))
        self.stdout.write(f"  Actualizados: {stats['updated']}")
        self.stdout.write(f"  Sin cambios:  {stats['skipped_same']}")
        self.stdout.write(f"  Saltados/Low: {stats['skipped_low_confidence']}")
        self.stdout.write(f"  Errores:      {stats['errors']}")
