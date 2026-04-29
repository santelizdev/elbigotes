import hashlib
import json
import logging
import os
import time

import requests
from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import Q

from apps.ingestion.models import ImportedPlaceRecord, ImportRecordStatus

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("enrich_details")

DETAILS_URL = "https://maps.googleapis.com/maps/api/place/details/json"
DETAIL_FIELDS = (
    "place_id,name,formatted_address,geometry,formatted_phone_number,"
    "website,opening_hours,rating,user_ratings_total,types,address_components"
)


class Command(BaseCommand):
    help = "Enriquece selectivamente ImportedPlaceRecord sin horarios consultando Google Place Details"

    def add_arguments(self, parser):
        parser.add_argument("--dataset", required=True, help="Slug del SourceDataset")
        parser.add_argument("--category", default=None, help="Filtrar por categoría específica")
        parser.add_argument("--limit", type=int, default=None, help="Límite máximo de registros a enriquecer")
        parser.add_argument("--max-requests", type=int, default=300, help="Límite máximo de llamadas a la API")
        parser.add_argument("--dry-run", action="store_true", help="Simula sin consumir API ni escribir en DB")
        parser.add_argument("--api-key", default=None, help="Google Maps API Key (usa GOOGLE_MAPS_API_KEY env var si no se pasa)")

    def handle(self, *args, **options):
        dataset_slug = options["dataset"]
        category_filter = options["category"]
        limit = options["limit"]
        max_requests = options["max_requests"]
        dry_run = options["dry_run"]
        api_key = options["api_key"] or os.environ.get("GOOGLE_MAPS_API_KEY")

        if not api_key and not dry_run:
            self.stderr.write(self.style.ERROR("Se requiere --api-key o GOOGLE_MAPS_API_KEY en el entorno."))
            return

        # Filtrar registros PENDING en el dataset especificado
        qs = ImportedPlaceRecord.objects.filter(
            dataset__slug=dataset_slug,
            status=ImportRecordStatus.PENDING
        )

        if category_filter:
            qs = qs.filter(raw_payload__meta__category_slug=category_filter)

        # Buscar todos y filtrar en memoria los que NO tienen opening_hours en payload y priorizar
        candidates = []
        for record in qs.iterator():
            google = record.raw_payload.get("google", {})
            if "opening_hours" in google:
                continue

            category_slug = record.raw_payload.get("meta", {}).get("category_slug", "")
            raw_name = record.raw_name.lower()
            
            # Lógica de priorización
            is_priority = False
            if category_slug == "emergencia-veterinaria":
                is_priority = True
            elif any(token in raw_name for token in ["24", "24/7", "24 horas", "urgencia", "emergencia"]):
                is_priority = True
            
            # Priorizamos si es tienda 24h
            if category_slug == "tiendas" and any(token in raw_name for token in ["24", "24/7", "24 horas"]):
                is_priority = True

            candidates.append((is_priority, record))

        # Ordenar: primero los prioritarios (True > False), y limitarlos si es necesario
        candidates.sort(key=lambda x: x[0], reverse=True)
        
        if limit:
            candidates = candidates[:limit]

        if not candidates:
            self.stdout.write(self.style.WARNING("No hay candidatos sin horarios para enriquecer."))
            return

        self.stdout.write(f"Iniciando enriquecimiento selectivo de {len(candidates)} candidatos.")
        
        stats = {"enriched": 0, "skipped": 0, "errors": 0}
        requests_made = 0

        session = requests.Session()

        for is_priority, record in candidates:
            if requests_made >= max_requests:
                self.stdout.write(self.style.WARNING(f"Límite de max_requests alcanzado ({max_requests})."))
                break

            place_id = record.external_id

            if dry_run:
                self.stdout.write(f"[DRY RUN] Enriquecería: {record.raw_name} [{place_id}]")
                stats["enriched"] += 1
                continue

            requests_made += 1
            time.sleep(0.15) # Throttle

            params = {
                "place_id": place_id,
                "fields": DETAIL_FIELDS,
                "language": "es",
                "key": api_key,
            }

            try:
                resp = session.get(DETAILS_URL, params=params, timeout=10)
                resp.raise_for_status()
                data = resp.json()
                
                status = data.get("status")
                if status != "OK":
                    self.stdout.write(self.style.WARNING(f"Error API {status} para {place_id}"))
                    stats["errors"] += 1
                    continue

                details = data.get("result", {})
                
                # Actualizamos payload
                payload = record.raw_payload
                google_data = payload.setdefault("google", {})
                
                # Merge details
                for key in ["opening_hours", "formatted_phone_number", "website", "rating", "user_ratings_total", "types", "address_components", "geometry"]:
                    if key in details:
                        google_data[key] = details[key]

                # Recalcular checksum
                blob = json.dumps(payload, sort_keys=True, ensure_ascii=False)
                new_checksum = hashlib.sha256(blob.encode()).hexdigest()[:64]

                with transaction.atomic():
                    record.raw_payload = payload
                    record.checksum = new_checksum
                    record.notes = f"Enriquecido con Details. Horarios: {'SÍ' if 'opening_hours' in details else 'NO'}"
                    record.save(update_fields=["raw_payload", "checksum", "notes", "updated_at"])

                stats["enriched"] += 1
                
                if stats["enriched"] % 10 == 0:
                    self.stdout.write(f"  Progreso: {stats['enriched']} enriquecidos...")

            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Excepción enriqueciendo {place_id}: {e}"))
                stats["errors"] += 1

        self.stdout.write("=" * 50)
        self.stdout.write("ENRIQUECIMIENTO FINALIZADO" + (" [DRY RUN]" if dry_run else ""))
        self.stdout.write(f"  Enriquecidos: {stats['enriched']}")
        self.stdout.write(f"  Errores:      {stats['errors']}")
        self.stdout.write(f"  API Calls:    {requests_made}")
        self.stdout.write(f"  Costo est.:   ~$%{(requests_made * 0.017):.2f} USD")
