"""
Management command: geocode_places
====================================
Geocodifica Places que no tienen coordenadas usando Google Geocoding API.
Registra cada intento en GeocodingLog para trazabilidad completa.

Uso:
    # Ver qué se geocodificaría sin gastar nada
    python manage.py geocode_places --api-key $GOOGLE_MAPS_API_KEY --dry-run

    # Geocodificar todos los places sin coordenadas
    python manage.py geocode_places --api-key $GOOGLE_MAPS_API_KEY

    # Solo places manuales (sin google_place_id)
    python manage.py geocode_places --api-key $GOOGLE_MAPS_API_KEY --only-manual

    # Reintentar los que fallaron antes
    python manage.py geocode_places --api-key $GOOGLE_MAPS_API_KEY --retry-failed

Ubicación:
    src/apps/ingestion/management/commands/geocode_places.py
"""

import time

import requests
from django.contrib.gis.geos import Point
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from apps.ingestion.models import GeocodingLog, GeocodingStatus
from apps.places.models import Place


GEOCODING_URL = "https://maps.googleapis.com/maps/api/geocode/json"

# Direcciones que sabemos que son demasiado genéricas — skip automático
SKIP_PATTERNS = [
    "punto confirmado",
    "región metropolitana, chile",
    "santiago centro, región",
]


def is_too_generic(address: str) -> bool:
    normalized = address.lower().strip()
    return any(pattern in normalized for pattern in SKIP_PATTERNS) or len(normalized) < 20


def geocode_address(api_key: str, query: str, session: requests.Session) -> dict:
    """Llama a Google Geocoding API y retorna el resultado crudo."""
    time.sleep(0.12)  # throttle suave
    try:
        resp = session.get(
            GEOCODING_URL,
            params={
                "address": query,
                "region": "cl",
                "language": "es",
                "key": api_key,
            },
            timeout=15,
        )
        resp.raise_for_status()
        return resp.json()
    except requests.RequestException as exc:
        return {"status": "REQUEST_ERROR", "error": str(exc)}


def extract_best_result(data: dict) -> tuple[float, float, str] | None:
    """
    Extrae (lat, lng, matched_address) del primer resultado de Geocoding API.
    Retorna None si no hay resultados válidos.
    """
    results = data.get("results", [])
    if not results:
        return None
    best = results[0]
    location = best.get("geometry", {}).get("location", {})
    lat = location.get("lat")
    lng = location.get("lng")
    matched = best.get("formatted_address", "")
    if lat is None or lng is None:
        return None
    return lat, lng, matched


class Command(BaseCommand):
    help = "Geocodifica Places sin coordenadas usando Google Geocoding API"

    def add_arguments(self, parser):
        parser.add_argument(
            "--api-key",
            required=True,
            help="Google Maps API key con Geocoding API habilitada",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Muestra qué se geocodificaría sin llamar a la API",
        )
        parser.add_argument(
            "--only-manual",
            action="store_true",
            help="Solo geocodificar places sin google_place_id (cargados manualmente)",
        )
        parser.add_argument(
            "--retry-failed",
            action="store_true",
            help="Reintentar places que fallaron en un intento anterior",
        )
        parser.add_argument(
            "--limit",
            type=int,
            default=None,
            help="Limitar cantidad a procesar",
        )

    def handle(self, *args, **options):
        api_key = options["api_key"]
        dry_run = options["dry_run"]
        only_manual = options["only_manual"]
        retry_failed = options["retry_failed"]
        limit = options["limit"]

        # --- Queryset base: places sin coordenadas ---
        qs = Place.objects.filter(location__isnull=True)

        if only_manual:
            qs = qs.filter(metadata__google_place_id__isnull=True)

        if not retry_failed:
            # Excluir los que ya tienen un GeocodingLog exitoso
            already_succeeded = GeocodingLog.objects.filter(
                status=GeocodingStatus.SUCCEEDED
            ).values_list("place_id", flat=True)
            qs = qs.exclude(pk__in=already_succeeded)

        qs = qs.order_by("pk")
        if limit:
            qs = qs[:limit]

        total = qs.count()
        if total == 0:
            self.stdout.write(self.style.WARNING("No hay places sin coordenadas para geocodificar."))
            return

        self.stdout.write(
            f"{'[DRY RUN] ' if dry_run else ''}Geocodificando {total} places"
            + (" (solo manuales)" if only_manual else "")
        )
        self.stdout.write(f"Costo estimado: ~${total * 0.005:.2f} USD\n")

        session = requests.Session()
        stats = {"succeeded": 0, "failed": 0, "skipped": 0, "api_calls": 0}

        for place in qs.iterator():
            query = place.geocoding_query  # property ya definida en el modelo

            # Skip automático para direcciones genéricas
            if is_too_generic(query):
                self.stdout.write(
                    self.style.WARNING(f"  SKIP [{place.pk}] '{place.name}' — dirección genérica: '{query[:60]}'")
                )
                stats["skipped"] += 1
                continue

            if dry_run:
                self.stdout.write(
                    f"  WOULD GEOCODE [{place.pk}] '{place.name}'\n"
                    f"    query: '{query[:80]}'"
                )
                stats["succeeded"] += 1
                continue

            # --- Llamada real a la API ---
            stats["api_calls"] += 1
            data = geocode_address(api_key, query, session)
            status = data.get("status", "UNKNOWN")

            if status == "OK":
                result = extract_best_result(data)
                if result:
                    lat, lng, matched_address = result
                    try:
                        with transaction.atomic():
                            # Actualizar coordenadas del Place
                            place.location = Point(lng, lat, srid=4326)
                            place.save(update_fields=["location", "updated_at"])

                            # Registrar en GeocodingLog
                            GeocodingLog.objects.create(
                                place=place,
                                provider="google_geocoding_api",
                                query=query,
                                status=GeocodingStatus.SUCCEEDED,
                                matched_address=matched_address[:255],
                                latitude=lat,
                                longitude=lng,
                                raw_response=data,
                            )

                        self.stdout.write(
                            self.style.SUCCESS(
                                f"  OK [{place.pk}] '{place.name}' → {lat:.4f}, {lng:.4f}"
                            )
                        )
                        stats["succeeded"] += 1

                    except Exception as exc:
                        self.stdout.write(
                            self.style.ERROR(f"  ERROR DB [{place.pk}] '{place.name}': {exc}")
                        )
                        stats["failed"] += 1
                else:
                    self._log_failure(place, query, data, "Sin resultados en respuesta OK")
                    stats["failed"] += 1
            else:
                error_msg = f"API status: {status}"
                self._log_failure(place, query, data, error_msg)
                self.stdout.write(
                    self.style.ERROR(f"  FAIL [{place.pk}] '{place.name}': {error_msg}")
                )
                stats["failed"] += 1

        # --- Resumen ---
        self.stdout.write("\n" + "=" * 60)
        self.stdout.write(
            self.style.SUCCESS(f"{'[DRY RUN] ' if dry_run else ''}GEOCODING COMPLETO")
        )
        self.stdout.write(f"  Geocodificados: {stats['succeeded']}")
        self.stdout.write(f"  Saltados:       {stats['skipped']}")
        self.stdout.write(f"  Fallidos:       {stats['failed']}")
        self.stdout.write(f"  API calls:      {stats['api_calls']}")
        self.stdout.write(f"  Costo real:     ~${stats['api_calls'] * 0.005:.3f} USD")

        if stats["skipped"] > 0:
            self.stdout.write(
                self.style.WARNING(
                    f"\n  {stats['skipped']} place(s) saltados por dirección genérica.\n"
                    f"  Corrígelos manualmente en /admin/places/place/ agregando coordenadas."
                )
            )

    def _log_failure(self, place: Place, query: str, raw_response: dict, error_msg: str):
        """Registra un intento fallido en GeocodingLog."""
        try:
            GeocodingLog.objects.create(
                place=place,
                provider="google_geocoding_api",
                query=query,
                status=GeocodingStatus.FAILED,
                matched_address="",
                latitude=None,
                longitude=None,
                raw_response=raw_response,
                error_message=error_msg[:500],
            )
        except Exception:
            pass  # No romper el flujo principal si el log falla
