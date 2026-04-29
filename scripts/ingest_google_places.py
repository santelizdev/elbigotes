"""
Ingesta de Google Places API → ImportedPlaceRecord
====================================================
Uso:
    python ingest_google_places.py --api-key TU_KEY --dataset veterinarias-rm
    python ingest_google_places.py --api-key TU_KEY --dataset refugios-nacional --dry-run

Requiere:
    pip install requests django-environ

Se puede correr desde la raíz del proyecto o desde `/app/scripts` dentro del
contenedor. El script detecta automáticamente `src/` para bootstrapear Django.
"""

import argparse
import hashlib
import json
import logging
import os
import sys
import time
import unicodedata
from collections.abc import Iterator
from dataclasses import dataclass, field
from pathlib import Path

import requests


# ---------------------------------------------------------------------------
# Bootstrap Django
# ---------------------------------------------------------------------------
def resolve_project_root() -> Path:
    script_dir = Path(__file__).resolve().parent
    for candidate in (script_dir, *script_dir.parents):
        src_root = candidate / "src"
        if (src_root / "manage.py").exists() and (src_root / "config").exists():
            return candidate
    raise RuntimeError("No pude encontrar la raíz del proyecto ni la carpeta src/.")


PROJECT_ROOT = resolve_project_root()
SRC_ROOT = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC_ROOT))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")

import django

django.setup()

from django.db import transaction

from apps.ingestion.models import (
    ImportedPlaceRecord,
    ImportRecordStatus,
    Source,
    SourceDataset,
    SourceKind,
)

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("ingest")


class IngestionBudgetExceeded(Exception):
    """Base class for ingestion guardrails."""


class RequestBudgetExceeded(IngestionBudgetExceeded):
    """Raised when the max request budget is exceeded."""


class RecordBudgetExceeded(IngestionBudgetExceeded):
    """Raised when the max record budget is exceeded."""

# ---------------------------------------------------------------------------
# Configuración de búsqueda
# ---------------------------------------------------------------------------

# Capitales regionales de Chile con coordenadas centrales
CHILE_REGIONS: list[dict] = [
    {"name": "Región de Arica y Parinacota",   "commune": "Arica",          "lat": -18.4783, "lng": -70.3126},
    {"name": "Región de Tarapacá",              "commune": "Iquique",        "lat": -20.2133, "lng": -70.1503},
    {"name": "Región de Antofagasta",           "commune": "Antofagasta",    "lat": -23.6509, "lng": -70.3975},
    {"name": "Región de Atacama",               "commune": "Copiapó",        "lat": -27.3668, "lng": -70.3321},
    {"name": "Región de Coquimbo",              "commune": "La Serena",      "lat": -29.9027, "lng": -71.2520},
    {"name": "Región de Valparaíso",            "commune": "Valparaíso",     "lat": -33.0472, "lng": -71.6127},
    {"name": "Región Metropolitana",            "commune": "Santiago",       "lat": -33.4489, "lng": -70.6693},
    {"name": "Región del Libertador O'Higgins", "commune": "Rancagua",       "lat": -34.1708, "lng": -70.7444},
    {"name": "Región del Maule",                "commune": "Talca",          "lat": -35.4264, "lng": -71.6554},
    {"name": "Región de Ñuble",                 "commune": "Chillán",        "lat": -36.6066, "lng": -72.1034},
    {"name": "Región del Biobío",               "commune": "Concepción",     "lat": -36.8201, "lng": -73.0444},
    {"name": "Región de La Araucanía",          "commune": "Temuco",         "lat": -38.7359, "lng": -72.5904},
    {"name": "Región de Los Ríos",              "commune": "Valdivia",       "lat": -39.8142, "lng": -73.2459},
    {"name": "Región de Los Lagos",             "commune": "Puerto Montt",   "lat": -41.4693, "lng": -72.9424},
    {"name": "Región de Aysén",                 "commune": "Coyhaique",      "lat": -45.5712, "lng": -72.0680},
    {"name": "Región de Magallanes",            "commune": "Punta Arenas",   "lat": -53.1638, "lng": -70.9171},
]

RM_TOP_COMMUNES: list[dict] = [
    {"name": "Región Metropolitana", "commune": "Santiago", "lat": -33.4489, "lng": -70.6693},
    {"name": "Región Metropolitana", "commune": "Las Condes", "lat": -33.4080, "lng": -70.5673},
    {"name": "Región Metropolitana", "commune": "Providencia", "lat": -33.4310, "lng": -70.6180},
    {"name": "Región Metropolitana", "commune": "Ñuñoa", "lat": -33.4569, "lng": -70.5979},
    {"name": "Región Metropolitana", "commune": "Maipú", "lat": -33.5108, "lng": -70.7600},
    {"name": "Región Metropolitana", "commune": "Puente Alto", "lat": -33.6117, "lng": -70.5758},
    {"name": "Región Metropolitana", "commune": "La Florida", "lat": -33.5310, "lng": -70.5930},
    {"name": "Región Metropolitana", "commune": "San Bernardo", "lat": -33.5924, "lng": -70.6996},
    {"name": "Región Metropolitana", "commune": "Pudahuel", "lat": -33.4440, "lng": -70.7239},
    {"name": "Región Metropolitana", "commune": "Quilicura", "lat": -33.3569, "lng": -70.7298},
]

SEARCH_SEEDS: list[dict] = CHILE_REGIONS + [
    commune
    for commune in RM_TOP_COMMUNES
    if commune["commune"] != "Santiago"
]

# Mapeo de categoría interna → query terms para Google Places
CATEGORY_QUERIES: dict[str, list[str]] = {
    "veterinaria": [
        "veterinaria",
        "clínica veterinaria",
        "hospital veterinario",
    ],
    "refugio": [
        "refugio de animales",
        "rescate de mascotas",
        "adopción de perros",
        "fundación animales",
    ],
    "peluqueria-canina": [
        "peluqueria canina perros",
        "grooming perros",
        "peluqueria mascotas perros",
        "baño corte perros grooming",
        "dog grooming santiago",
    ],
    "guarderia": [
        "guardería de perros",
        "daycare mascotas",
        "hotel de mascotas",
    ],
    "emergencia-veterinaria": [
        "urgencia veterinaria",
        "emergencia veterinaria 24 horas",
        "hospital veterinario 24 horas",
    ],
    "parque": [
        "parque canino",
        "dog park",
        "parque pet friendly",
    ],
    "tiendas": [
        "pet shop",
        "tienda de mascotas",
        "tienda productos mascotas",
        "alimentos para mascotas",
        "accesorios para mascotas",
    ],
}

# Radio de búsqueda en metros por región
# RM más amplio por densidad; resto estándar
SEARCH_RADIUS_BY_COMMUNE: dict[str, int] = {
    "Santiago": 20_000,
    "Las Condes": 12_000,
    "Providencia": 10_000,
    "Ñuñoa": 10_000,
    "Maipú": 14_000,
    "Puente Alto": 14_000,
    "La Florida": 12_000,
    "San Bernardo": 14_000,
    "Pudahuel": 14_000,
    "Quilicura": 14_000,
    "Valparaíso": 12_000,
    "Concepción": 12_000,
}
DEFAULT_RADIUS = 8_000

# ---------------------------------------------------------------------------
# Google Places client
# ---------------------------------------------------------------------------

PLACES_BASE = "https://maps.googleapis.com/maps/api/place"
NEARBY_URL  = f"{PLACES_BASE}/nearbysearch/json"
DETAILS_URL = f"{PLACES_BASE}/details/json"

DETAIL_FIELDS = (
    "place_id,name,formatted_address,geometry,formatted_phone_number,"
    "website,opening_hours,rating,user_ratings_total,types,address_components"
)


def build_google_maps_url(place_id: str) -> str:
    if not place_id:
        return ""
    return f"https://www.google.com/maps/place/?q=place_id:{place_id}"

@dataclass
class PlacesClient:
    api_key: str
    max_requests: int | None = None
    requests_made: int = 0
    _session: requests.Session = field(default_factory=requests.Session)

    def nearby_search(self, lat: float, lng: float, keyword: str, radius: int) -> Iterator[dict]:
        """Itera todos los resultados paginados de nearby search."""
        params = {
            "location": f"{lat},{lng}",
            "radius": radius,
            "keyword": keyword,
            "language": "es",
            "key": self.api_key,
        }
        while True:
            resp = self._get(NEARBY_URL, params)
            status = resp.get("status")
            if status not in ("OK", "ZERO_RESULTS"):
                log.warning(
                    "Nearby search status: %s — keyword: %s — error: %s",
                    status,
                    keyword,
                    resp.get("error_message", "sin detalle"),
                )
                break
            for result in resp.get("results", []):
                yield result
            next_token = resp.get("next_page_token")
            if not next_token:
                break
            # Google exige ~2s antes de usar el page token
            time.sleep(2.2)
            params = {"pagetoken": next_token, "key": self.api_key}

    def place_details(self, place_id: str) -> dict:
        params = {
            "place_id": place_id,
            "fields": DETAIL_FIELDS,
            "language": "es",
            "key": self.api_key,
        }
        resp = self._get(DETAILS_URL, params)
        return resp.get("result", {})

    def _get(self, url: str, params: dict) -> dict:
        if self.max_requests is not None and self.requests_made >= self.max_requests:
            raise RequestBudgetExceeded(
                f"Se alcanzó el máximo de {self.max_requests} requests a Google Places."
            )
        self.requests_made += 1
        # Throttle: max ~10 req/seg para no saturar quota
        time.sleep(0.12)
        try:
            r = self._session.get(url, params=params, timeout=15)
            r.raise_for_status()
            return r.json()
        except requests.RequestException as exc:
            log.error("HTTP error: %s", exc)
            return {}


# ---------------------------------------------------------------------------
# Normalización de payload → campos del modelo
# ---------------------------------------------------------------------------

def extract_address_component(components: list[dict], kind: str) -> str:
    for comp in components:
        if kind in comp.get("types", []):
            return comp.get("long_name", "")
    return ""


def normalize_record(
    details: dict,
    commune: str,
    region: str,
    category_slug: str,
    *,
    search_keyword: str,
    search_radius_m: int,
) -> dict:
    """Convierte el JSON de Google Places en un dict listo para ImportedPlaceRecord."""
    address_comps = details.get("address_components", [])
    geometry = details.get("geometry", {}).get("location", {})

    commune_google = (
        extract_address_component(address_comps, "locality")
        or extract_address_component(address_comps, "administrative_area_level_3")
        or commune
    )
    region_google = (
        extract_address_component(address_comps, "administrative_area_level_1")
        or region
    )

    return {
        "raw_name": details.get("name", "")[:200],
        "raw_address": details.get("formatted_address", "")[:255],
        "raw_payload": {
            "google": details,
            "meta": {
                "category_slug": category_slug,
                "commune_target": commune,
                "region_target": region,
                "search_keyword": search_keyword,
                "search_radius_m": search_radius_m,
                "google_maps_url": build_google_maps_url(details.get("place_id", "")),
            },
        },
        # Campos extra que usaremos al promover a Place
        "_lat": geometry.get("lat"),
        "_lng": geometry.get("lng"),
        "_commune": commune_google,
        "_region": region_google,
        "_phone": details.get("formatted_phone_number", ""),
        "_website": details.get("website", ""),
        "_rating": details.get("rating"),
        "_total_ratings": details.get("user_ratings_total", 0),
    }


def checksum(payload: dict) -> str:
    blob = json.dumps(payload, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(blob.encode()).hexdigest()[:64]


# ---------------------------------------------------------------------------
# Ingesta principal
# ---------------------------------------------------------------------------

def get_or_create_source_and_dataset(dataset_slug: str) -> tuple[Source, SourceDataset]:
    source, _ = Source.objects.get_or_create(
        slug="google-places",
        defaults={
            "name": "Google Places API",
            "kind": SourceKind.API,
            "domain": "maps.googleapis.com",
            "reliability_score": 0.85,
            "is_active": True,
        },
    )
    dataset, created = SourceDataset.objects.get_or_create(
        slug=dataset_slug,
        defaults={
            "source": source,
            "name": dataset_slug.replace("-", " ").title(),
            "default_country": "Chile",
            "is_active": True,
        },
    )
    if created:
        log.info("Dataset creado: %s", dataset_slug)
    return source, dataset


@transaction.atomic
def upsert_record(
    source: Source,
    dataset: SourceDataset,
    place_id: str,
    normalized: dict,
    dry_run: bool,
) -> tuple[str, bool]:
    """
    Inserta o actualiza un ImportedPlaceRecord.
    Retorna (action, changed) donde action ∈ {'created', 'updated', 'skipped'}.
    """
    payload = normalized["raw_payload"]
    new_checksum = checksum(payload)

    existing = ImportedPlaceRecord.objects.filter(
        dataset=dataset,
        external_id=place_id,
    ).first()

    if existing:
        if existing.checksum == new_checksum:
            return "skipped", False
        if not dry_run:
            existing.raw_name = normalized["raw_name"]
            existing.raw_address = normalized["raw_address"]
            existing.raw_payload = payload
            existing.checksum = new_checksum
            existing.notes = f"Actualizado en re-run. Rating: {normalized['_rating']}"
            existing.status = ImportRecordStatus.PENDING
            existing.save(update_fields=[
                "raw_name", "raw_address", "raw_payload",
                "checksum", "notes", "status", "updated_at",
            ])
        return "updated", True

    if not dry_run:
        ImportedPlaceRecord.objects.create(
            dataset=dataset,
            source=source,
            external_id=place_id,
            status=ImportRecordStatus.PENDING,
            checksum=new_checksum,
            raw_name=normalized["raw_name"],
            raw_address=normalized["raw_address"],
            raw_payload=payload,
            notes=f"Rating Google: {normalized['_rating']} ({normalized['_total_ratings']} reseñas)",
        )
    return "created", True


def run_ingestion(
    api_key: str,
    dataset_slug: str,
    categories: list[str],
    regions: list[dict],
    dry_run: bool,
    fetch_details: bool,
    max_records: int | None = None,
    max_requests: int | None = None,
) -> None:
    client = PlacesClient(api_key=api_key, max_requests=max_requests)
    source, dataset = get_or_create_source_and_dataset(dataset_slug)

    stats = {"created": 0, "updated": 0, "skipped": 0, "errors": 0, "with_hours": 0, "without_hours": 0}
    seen_place_ids: set[str] = set()
    processed_records = 0
    stopped_early = False
    stop_reason = ""

    total_combinations = len(regions) * sum(len(q) for q in [CATEGORY_QUERIES[c] for c in categories if c in CATEGORY_QUERIES])
    log.info(
        "Iniciando ingesta: %d regiones × %d queries = ~%d búsquedas%s | Fetch Details: %s",
        len(regions),
        sum(len(CATEGORY_QUERIES[c]) for c in categories if c in CATEGORY_QUERIES),
        total_combinations,
        " [DRY RUN]" if dry_run else "",
        "SÍ (Alto costo)" if fetch_details else "NO (Discovery barato)",
    )

    for region_data in regions:
        commune = region_data["commune"]
        region  = region_data["name"]
        lat     = region_data["lat"]
        lng     = region_data["lng"]
        radius  = SEARCH_RADIUS_BY_COMMUNE.get(commune, DEFAULT_RADIUS)

        for category_slug in categories:
            queries = CATEGORY_QUERIES.get(category_slug, [])
            for keyword in queries:
                log.info("  ↳ %s / %s — '%s'", commune, category_slug, keyword)
                try:
                    for result in client.nearby_search(lat, lng, keyword, radius):
                        place_id = result.get("place_id")
                        if not place_id or place_id in seen_place_ids:
                            continue
                        if max_records is not None and processed_records >= max_records:
                            raise RecordBudgetExceeded(
                                f"Se alcanzó el máximo de {max_records} registros procesados."
                            )
                        seen_place_ids.add(place_id)
                        processed_records += 1

                        # Fetch details si se pidió (más info, más costo)
                        if fetch_details:
                            details = client.place_details(place_id)
                        else:
                            # Usar datos del nearby search directamente
                            details = {
                                "place_id": place_id,
                                "name": result.get("name", ""),
                                "formatted_address": result.get("vicinity", ""),
                                "geometry": result.get("geometry", {}),
                                "rating": result.get("rating"),
                                "user_ratings_total": result.get("user_ratings_total", 0),
                                "types": result.get("types", []),
                                "address_components": [],
                            }

                        if details.get("opening_hours"):
                            stats["with_hours"] += 1
                        else:
                            stats["without_hours"] += 1

                        normalized = normalize_record(
                            details,
                            commune,
                            region,
                            category_slug,
                            search_keyword=keyword,
                            search_radius_m=radius,
                        )
                        action, _ = upsert_record(source, dataset, place_id, normalized, dry_run)
                        stats[action] += 1

                        if stats["created"] % 50 == 0 and stats["created"] > 0:
                            log.info(
                                "  Progreso: +%d creados | %d actualizados | %d saltados | %d API calls",
                                stats["created"], stats["updated"], stats["skipped"], client.requests_made,
                            )

                except IngestionBudgetExceeded as exc:
                    log.warning("%s", exc)
                    stopped_early = True
                    stop_reason = str(exc)
                    break
                except Exception as exc:
                    log.error("Error en %s/%s: %s", commune, keyword, exc)
                    stats["errors"] += 1
                    continue
            if stopped_early:
                break
        if stopped_early:
            break

    log.info("=" * 60)
    log.info("INGESTA COMPLETA%s", " [DRY RUN — nada fue guardado]" if dry_run else "")
    log.info("  Creados:     %d", stats["created"])
    log.info("  Actualizados:%d", stats["updated"])
    log.info("  Saltados:    %d", stats["skipped"])
    log.info("  Errores:     %d", stats["errors"])
    log.info("  Con horarios: %d", stats["with_hours"])
    log.info("  Sin horarios: %d", stats["without_hours"])
    log.info("  Procesados:  %d", processed_records)
    log.info("  API calls:   %d", client.requests_made)
    if stopped_early:
        log.info("  Corte seguro: %s", stop_reason)
    log.info(
        "  Costo estimado: ~$%.2f USD",
        client.requests_made * 0.032,  # Nearby Search pricing
    )


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

AVAILABLE_CATEGORIES = list(CATEGORY_QUERIES.keys())


def normalize_token(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value or "")
    ascii_only = normalized.encode("ascii", "ignore").decode("ascii")
    collapsed = ascii_only.replace("-", " ").replace("_", " ")
    return " ".join(collapsed.strip().lower().split())


AVAILABLE_REGIONS = [normalize_token(r["commune"]) for r in SEARCH_SEEDS]


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Ingesta Google Places → ImportedPlaceRecord",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  # Todas las categorías, todas las regiones (producción)
  python ingest_google_places.py --api-key AIza... --dataset lanzamiento-v1

  # Solo veterinarias en Santiago (test barato)
  python ingest_google_places.py --api-key AIza... --dataset test-stgo \\
      --categories veterinaria --only-communes santiago

  # Ver qué haría sin gastar API calls
  python ingest_google_places.py --api-key AIza... --dataset test \\
      --categories veterinaria refugio --dry-run

  # Con detalles completos (más datos, más costo ~2x)
  python ingest_google_places.py --api-key AIza... --dataset full-v1 --fetch-details
        """,
    )
    parser.add_argument("--api-key",        required=True, help="Google Maps API key")
    parser.add_argument("--dataset",        required=True, help="Slug del SourceDataset a crear/usar")
    parser.add_argument(
        "--categories",
        nargs="+",
        default=AVAILABLE_CATEGORIES,
        choices=AVAILABLE_CATEGORIES,
        help=f"Categorías a ingestar. Por defecto: todas. Opciones: {AVAILABLE_CATEGORIES}",
    )
    parser.add_argument(
        "--only-communes",
        nargs="+",
        default=None,
        metavar="COMMUNE",
        help="Filtrar por comunas específicas (ej: santiago valparaiso). Por defecto: todas.",
    )
    parser.add_argument(
        "--rm-top-communes",
        action="store_true",
        help="Usa un barrido por las 10 comunas prioritarias de Región Metropolitana.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simula la ingesta sin escribir en la base de datos",
    )
    parser.add_argument(
        "--fetch-details",
        action="store_true",
        help="Hace una llamada extra a Place Details por cada lugar (más datos, ~2x más costo)",
    )
    parser.add_argument(
        "--max-records",
        type=int,
        default=None,
        help="Corta la ingesta al procesar esta cantidad máxima de lugares únicos.",
    )
    parser.add_argument(
        "--max-requests",
        type=int,
        default=None,
        help="Corta la ingesta al alcanzar esta cantidad máxima de requests a Google.",
    )

    args = parser.parse_args()

    # Filtrar regiones si se especificaron comunas
    regions = SEARCH_SEEDS
    if args.rm_top_communes:
        regions = RM_TOP_COMMUNES
        log.info(
            "Usando preset RM top comunas: %s",
            [region["commune"] for region in regions],
        )
    elif args.only_communes:
        filter_set = {normalize_token(c) for c in args.only_communes}
        regions = [r for r in SEARCH_SEEDS if normalize_token(r["commune"]) in filter_set]
        if not regions:
            log.error(
                "Ninguna de las comunas especificadas coincide. Disponibles: %s",
                AVAILABLE_REGIONS,
            )
            sys.exit(1)
        log.info("Filtrando a %d región(es): %s", len(regions), [r["commune"] for r in regions])

    run_ingestion(
        api_key=args.api_key,
        dataset_slug=args.dataset,
        categories=args.categories,
        regions=regions,
        dry_run=args.dry_run,
        fetch_details=args.fetch_details,
        max_records=args.max_records,
        max_requests=args.max_requests,
    )


if __name__ == "__main__":
    main()
