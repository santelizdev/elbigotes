"""
Management command: promote_places
===================================
Promueve ImportedPlaceRecord (staging) → Place (producción)

Uso:
    # Ver qué se promovería sin escribir nada
    python manage.py promote_places --dataset test-local-v1 --dry-run

    # Promover todo el dataset
    python manage.py promote_places --dataset test-local-v1

    # Promover solo una categoría
    python manage.py promote_places --dataset test-local-v1 --category veterinaria

    # Forzar re-promoción de registros ya importados
    python manage.py promote_places --dataset test-local-v1 --force

Ubicación:
    Copiar a: src/apps/ingestion/management/commands/promote_places.py
    (crear carpetas management/commands/ con __init__.py si no existen)
"""

import ast
import re
from pathlib import Path

from django.utils.text import slugify
from django.contrib.gis.geos import Point
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from apps.ingestion.models import ImportRecordStatus, ImportedPlaceRecord
from apps.places.choices import PlaceStatus
from apps.places.models import ContactPoint, Place
from apps.taxonomy.models import Category, Subcategory


# ---------------------------------------------------------------------------
# Mapeo: category_slug del raw_payload → slug real en tu DB
# Ajusta esto si agregas más categorías al script de ingesta
# ---------------------------------------------------------------------------
CATEGORY_MAP: dict[str, str] = {
    "veterinaria":       "veterinarias",
    "refugio":           "refugios-albergues",
    "peluqueria-canina": "peluquerias",
    "guarderia":         "guarderias",
    "emergencia-veterinaria": "emergencias-veterinarias",
    "parque": "parques-pet-friendly",
}

# Mapeo opcional a subcategoría por defecto según categoría
SUBCATEGORY_MAP: dict[str, str] = {
    "veterinaria":       "consulta",
    "refugio":           "refugios",
    "peluqueria-canina": None,
    "guarderia":         "guarderia-diurna",
    "emergencia-veterinaria": "urgencias",
    "parque": None,
}

CATEGORY_KEYWORDS: dict[str, tuple[str, ...]] = {
    "veterinaria": (
        "veterinaria",
        "veterinario",
        "clinica veterinaria",
        "clínica veterinaria",
        "hospital veterinario",
        "pet care",
    ),
    "refugio": (
        "refugio",
        "rescate",
        "adopcion",
        "adopción",
        "fundacion",
        "fundación",
        "proteccion animal",
        "protección animal",
        "santuario",
        "albergue",
        "ong",
        "corporacion",
        "corporación",
    ),
    "peluqueria-canina": (
        "peluqueria",
        "peluquería",
        "grooming",
        "baño y corte",
        "bano y corte",
        "estetica canina",
        "estética canina",
        "spa canino",
        "pet grooming",
    ),
    "guarderia": (
        "guarderia",
        "guardería",
        "hotel de mascotas",
        "hotel canino",
        "daycare",
        "pension canina",
        "pensión canina",
        "hospedaje canino",
        "hotel felino",
    ),
    "emergencia-veterinaria": (
        "urgencia veterinaria",
        "emergencia veterinaria",
        "24 horas",
        "24hrs",
        "24hr",
        "24 7",
        "24/7",
        "hospital veterinario",
        "clinica veterinaria 24",
        "clínica veterinaria 24",
    ),
    "parque": (
        "parque",
        "plaza",
        "canil",
        "dog park",
        "pet friendly",
        "zona canina",
    ),
}

NEGATIVE_KEYWORDS: dict[str, tuple[str, ...]] = {
    "refugio": (
        "veterinaria",
        "veterinario",
        "hotel de mascotas",
        "guarderia",
        "guardería",
        "peluqueria",
        "peluquería",
        "grooming",
    ),
    "guarderia": (
        "refugio",
        "rescate",
        "adopcion",
        "adopción",
        "fundacion",
        "fundación",
        "veterinaria",
        "veterinario",
        "clinica",
        "clínica",
        "peluqueria",
        "peluquería",
        "grooming",
    ),
    "peluqueria-canina": (
        "refugio",
        "rescate",
        "adopcion",
        "adopción",
        "veterinaria",
        "veterinario",
        "clinica",
        "clínica",
        "hospital veterinario",
        "hotel de mascotas",
        "guarderia",
        "guardería",
    ),
    "emergencia-veterinaria": (
        "refugio",
        "rescate",
        "adopcion",
        "adopción",
        "guarderia",
        "guardería",
        "peluqueria",
        "peluquería",
        "grooming",
        "parque",
        "plaza",
    ),
    "parque": (
        "veterinaria",
        "veterinario",
        "clinica",
        "clínica",
        "hospital",
        "refugio",
        "rescate",
        "guarderia",
        "guardería",
        "peluqueria",
        "peluquería",
        "grooming",
        "hotel de mascotas",
    ),
}

GOOGLE_TYPE_HINTS: dict[str, tuple[str, ...]] = {
    "veterinaria": ("veterinary_care",),
    "parque": ("park",),
}


def _normalize_text(value: str) -> str:
    return slugify(value or "").replace("-", " ")


def _load_known_communes() -> dict[str, str]:
    constants_path = (
        Path(__file__).resolve().parents[5]
        / "frontend"
        / "src"
        / "lib"
        / "constants"
        / "chile-locations.ts"
    )
    if not constants_path.exists():
        return {}

    text = constants_path.read_text(encoding="utf-8")
    aliases: dict[str, str] = {}

    for match in re.finditer(r"communes:\s*\[(.*?)\]", text, re.S):
        communes = ast.literal_eval(f"[{match.group(1)}]")
        for commune in communes:
            aliases.setdefault(_normalize_text(commune), commune)

    return aliases


REGION_ALIASES: dict[str, str] = {
    "arica y parinacota": "Región de Arica y Parinacota",
    "region de arica y parinacota": "Región de Arica y Parinacota",
    "tarapaca": "Región de Tarapacá",
    "region de tarapaca": "Región de Tarapacá",
    "antofagasta": "Región de Antofagasta",
    "region de antofagasta": "Región de Antofagasta",
    "atacama": "Región de Atacama",
    "region de atacama": "Región de Atacama",
    "coquimbo": "Región de Coquimbo",
    "region de coquimbo": "Región de Coquimbo",
    "valparaiso": "Región de Valparaíso",
    "region de valparaiso": "Región de Valparaíso",
    "region metropolitana": "Región Metropolitana",
    "region metropolitana de santiago": "Región Metropolitana",
    "metropolitana de santiago": "Región Metropolitana",
    "metropolitana": "Región Metropolitana",
    "o higgins": "Región del Libertador O'Higgins",
    "ohiggins": "Región del Libertador O'Higgins",
    "libertador o higgins": "Región del Libertador O'Higgins",
    "region del libertador o higgins": "Región del Libertador O'Higgins",
    "region del libertador bernardo o higgins": "Región del Libertador O'Higgins",
    "maule": "Región del Maule",
    "region del maule": "Región del Maule",
    "nuble": "Región de Ñuble",
    "region de nuble": "Región de Ñuble",
    "biobio": "Región del Biobío",
    "region del biobio": "Región del Biobío",
    "la araucania": "Región de La Araucanía",
    "region de la araucania": "Región de La Araucanía",
    "los rios": "Región de Los Ríos",
    "region de los rios": "Región de Los Ríos",
    "los lagos": "Región de Los Lagos",
    "region de los lagos": "Región de Los Lagos",
    "aysen": "Región de Aysén",
    "region de aysen": "Región de Aysén",
    "magallanes": "Región de Magallanes y la Antártica Chilena",
    "magallanes y la antartica chilena": "Región de Magallanes y la Antártica Chilena",
    "region de magallanes": "Región de Magallanes y la Antártica Chilena",
    "region de magallanes y la antartica chilena": "Región de Magallanes y la Antártica Chilena",
}

KNOWN_COMMUNES = _load_known_communes()
INVALID_COMMUNE_TOKENS = (
    "avenida",
    "av ",
    "avda",
    "calle",
    "camino",
    "pasaje",
    "ruta",
    "parque",
    "plaza",
    "condominio",
    "edificio",
    "torre",
    "kilometro",
    "km",
    "sector",
)


def normalize_region_name(value: str) -> str:
    raw = (value or "").strip()
    if not raw:
        return ""
    return REGION_ALIASES.get(_normalize_text(raw), raw)


def normalize_commune_name(value: str) -> str:
    raw = (value or "").strip()
    normalized = _normalize_text(raw)
    if not raw or not normalized or normalized == "chile":
        return ""
    if any(char.isdigit() for char in raw):
        return ""
    if re.fullmatch(r"-?\d+(?:\.\d+)?", raw):
        return ""
    if any(token in normalized for token in INVALID_COMMUNE_TOKENS):
        return ""
    return KNOWN_COMMUNES.get(normalized, "")


def parse_location_from_address(address: str) -> tuple[str, str]:
    """
    Intenta inferir comuna y región desde formatted_address/vicinity sin requerir Place Details.
    Ejemplos:
      - "Av. Providencia 1234, Providencia, Región Metropolitana, Chile"
      - "Colón 2870, Talcahuano"
    """
    tokens = [token.strip() for token in (address or "").split(",") if token.strip()]
    if not tokens:
        return "", ""

    commune = ""
    region = ""

    for token in reversed(tokens):
        normalized = _normalize_text(token)
        if not normalized or normalized == "chile":
            continue

        canonical_region = REGION_ALIASES.get(normalized)
        if canonical_region and not region:
            region = canonical_region
            continue

        canonical_commune = normalize_commune_name(token)
        if canonical_commune and not commune:
            commune = canonical_commune
            break

    return commune, region


def is_record_relevant(record: ImportedPlaceRecord) -> tuple[bool, str]:
    google = record.raw_payload.get("google", {})
    meta = record.raw_payload.get("meta", {})
    category_slug = meta.get("category_slug", "")
    name_haystack = _normalize_text(record.raw_name)
    address_haystack = _normalize_text(record.raw_address)
    haystack = " ".join(
        filter(
            None,
            [
                name_haystack,
                address_haystack,
            ],
        )
    )
    google_types = tuple(google.get("types", []))

    required_types = GOOGLE_TYPE_HINTS.get(category_slug, ())
    if required_types and any(google_type in required_types for google_type in google_types):
        return True, ""

    keywords = CATEGORY_KEYWORDS.get(category_slug, ())
    has_keyword_match = keywords and any(_normalize_text(keyword) in haystack for keyword in keywords)

    if category_slug == "veterinaria":
        if has_keyword_match:
            return True, ""
        return False, f"Resultado poco confiable para categoría '{category_slug}'"

    if category_slug == "refugio":
        if has_keyword_match:
            negative_keywords = NEGATIVE_KEYWORDS.get(category_slug, ())
            if any(_normalize_text(keyword) in haystack for keyword in negative_keywords):
                return False, f"Coincidencia ambigua para categoría '{category_slug}'"
            return True, ""
        return False, f"Resultado poco confiable para categoría '{category_slug}'"

    if category_slug == "emergencia-veterinaria":
        has_veterinary_signal = any(
            token in name_haystack
            for token in (
                "veterinaria",
                "veterinario",
                "hospital veterinario",
                "clinica veterinaria",
                "clínica veterinaria",
            )
        ) or "veterinary_care" in google_types
        has_emergency_signal = any(
            token in name_haystack
            for token in (
                "urgencia",
                "emergencia",
                "24 horas",
                "24hrs",
                "24hr",
                "24 7",
                "24/7",
            )
        )
        if not (has_veterinary_signal and has_emergency_signal):
            return False, f"Resultado poco confiable para categoría '{category_slug}'"
        negative_keywords = NEGATIVE_KEYWORDS.get(category_slug, ())
        if any(_normalize_text(keyword) in haystack for keyword in negative_keywords):
            return False, f"Coincidencia ambigua para categoría '{category_slug}'"
        return True, ""

    if category_slug == "parque":
        has_park_signal = any(
            _normalize_text(keyword) in name_haystack
            for keyword in CATEGORY_KEYWORDS.get(category_slug, ())
        ) or "park" in google_types
        if not has_park_signal:
            return False, f"Resultado poco confiable para categoría '{category_slug}'"
        negative_keywords = NEGATIVE_KEYWORDS.get(category_slug, ())
        if any(_normalize_text(keyword) in haystack for keyword in negative_keywords):
            return False, f"Coincidencia ambigua para categoría '{category_slug}'"
        return True, ""

    if category_slug in {"peluqueria-canina", "guarderia", "emergencia-veterinaria", "parque"}:
        if not has_keyword_match:
            return False, f"Resultado poco confiable para categoría '{category_slug}'"
        negative_keywords = NEGATIVE_KEYWORDS.get(category_slug, ())
        if any(_normalize_text(keyword) in haystack for keyword in negative_keywords):
            return False, f"Coincidencia ambigua para categoría '{category_slug}'"
        return True, ""

    return False, f"Resultado poco confiable para categoría '{category_slug}'"


def load_taxonomy() -> tuple[dict[str, Category], dict[str, Subcategory]]:
    """Carga toda la taxonomía en memoria para evitar N+1 queries."""
    categories = {c.slug: c for c in Category.objects.filter(is_active=True)}
    subcategories = {s.slug: s for s in Subcategory.objects.filter(is_active=True)}
    return categories, subcategories


def extract_address_component(components: list[dict], kind: str) -> str:
    for comp in components:
        if kind in comp.get("types", []):
            return comp.get("long_name", "")
    return ""


def build_place_from_record(
    record: ImportedPlaceRecord,
    categories: dict[str, Category],
    subcategories: dict[str, Subcategory],
) -> tuple[Place, list[dict]] | None:
    """
    Construye un Place y sus ContactPoints a partir de un ImportedPlaceRecord.
    Retorna (place, contact_points_data) o None si no se puede promover.
    """
    google = record.raw_payload.get("google", {})
    meta   = record.raw_payload.get("meta", {})

    is_relevant, relevance_error = is_record_relevant(record)
    if not is_relevant:
        return None, relevance_error

    # --- Categoría ---
    category_slug_raw = meta.get("category_slug", "")
    category_slug_db  = CATEGORY_MAP.get(category_slug_raw)
    if not category_slug_db or category_slug_db not in categories:
        return None, f"Categoría no mapeada: '{category_slug_raw}'"

    category = categories[category_slug_db]

    # --- Subcategoría (opcional) ---
    subcategory = None
    sub_slug = SUBCATEGORY_MAP.get(category_slug_raw)
    if sub_slug and sub_slug in subcategories:
        subcategory = subcategories[sub_slug]

    # --- Coordenadas ---
    location_data = google.get("geometry", {}).get("location", {})
    lat = location_data.get("lat")
    lng = location_data.get("lng")
    if lat is None or lng is None:
        return None, "Resultado sin coordenadas utiles para mapa"
    point = Point(lng, lat, srid=4326)

    # --- Dirección ---
    address_comps = google.get("address_components", [])
    formatted     = google.get("formatted_address", record.raw_address)
    parsed_commune, parsed_region = parse_location_from_address(formatted)
    commune       = (
        extract_address_component(address_comps, "locality")
        or extract_address_component(address_comps, "administrative_area_level_3")
        or parsed_commune
        or meta.get("commune_target", "")
    )
    region = normalize_region_name(
        extract_address_component(address_comps, "administrative_area_level_1")
        or parsed_region
        or meta.get("region_target", "")
    )

    # --- Place ---
    place = Place(
        name             = record.raw_name[:200],
        summary          = "",
        category         = category,
        subcategory      = subcategory,
        status           = PlaceStatus.DRAFT,
        location         = point,
        formatted_address= formatted[:255],
        street_address   = formatted[:255],
        commune          = commune[:120],
        region           = region[:120],
        country          = "Chile",
        website          = google.get("website", "")[:200] if google.get("website") else "",
        is_verified      = False,
        is_featured      = False,
        is_emergency_service = category_slug_raw == "emergencia-veterinaria",
        is_open_24_7     = category_slug_raw == "emergencia-veterinaria",
        source           = record.source,
        metadata         = {
            "google_place_id":    record.external_id,
            "google_rating":      google.get("rating"),
            "google_total_ratings": google.get("user_ratings_total", 0),
            "google_types":       google.get("types", []),
            "imported_from":      record.dataset.slug,
            "import_category_slug": category_slug_raw,
            "import_search_keyword": meta.get("search_keyword", ""),
            "review_status": "pending",
        },
    )

    # --- ContactPoints ---
    contact_points = []
    phone = google.get("formatted_phone_number", "")
    if phone:
        contact_points.append({
            "label":      "Teléfono",
            "kind":       "phone",
            "value":      phone[:255],
            "is_primary": True,
            "sort_order": 0,
        })
    website = google.get("website", "")
    if website:
        contact_points.append({
            "label":      "Sitio web",
            "kind":       "website",
            "value":      website[:255],
            "is_primary": not bool(phone),
            "sort_order": 1,
        })

    return place, contact_points


def update_existing_place(existing: Place, candidate: Place) -> Place:
    """
    Copia los campos importables de `candidate` sobre `existing` sin perder identidad
    editorial ni referencias públicas como slug/status.
    """
    editable_fields = (
        "name",
        "summary",
        "description",
        "category",
        "subcategory",
        "location",
        "street_address",
        "commune",
        "region",
        "country",
        "postal_code",
        "formatted_address",
        "website",
        "metadata",
        "is_verified",
        "is_featured",
        "is_emergency_service",
        "is_open_24_7",
        "source",
        "owner_business_profile",
    )

    for field_name in editable_fields:
        setattr(existing, field_name, getattr(candidate, field_name))

    return existing


class Command(BaseCommand):
    help = "Promueve ImportedPlaceRecord pendientes → Place"

    def add_arguments(self, parser):
        parser.add_argument(
            "--dataset",
            required=True,
            help="Slug del SourceDataset a procesar",
        )
        parser.add_argument(
            "--category",
            default=None,
            choices=list(CATEGORY_MAP.keys()),
            help="Filtrar por categoría específica",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Muestra qué se promovería sin escribir en la DB",
        )
        parser.add_argument(
            "--force",
            action="store_true",
            help="Re-promueve registros que ya fueron importados anteriormente",
        )
        parser.add_argument(
            "--limit",
            type=int,
            default=None,
            help="Limitar cantidad de registros a procesar (útil para pruebas)",
        )

    def handle(self, *args, **options):
        dataset_slug = options["dataset"]
        category_filter = options["category"]
        dry_run = options["dry_run"]
        force = options["force"]
        limit = options["limit"]

        # --- Cargar taxonomía ---
        categories, subcategories = load_taxonomy()
        self.stdout.write(
            f"Taxonomía cargada: {len(categories)} categorías, {len(subcategories)} subcategorías"
        )

        # --- Queryset base ---
        statuses = [ImportRecordStatus.PENDING]
        if force:
            statuses.append(ImportRecordStatus.IMPORTED)

        qs = (
            ImportedPlaceRecord.objects
            .filter(dataset__slug=dataset_slug, status__in=statuses)
            .select_related("dataset", "source")
            .order_by("created_at")
        )

        if category_filter:
            qs = qs.filter(
                raw_payload__meta__category_slug=category_filter
            )

        if limit:
            qs = qs[:limit]

        total = qs.count()
        if total == 0:
            self.stdout.write(self.style.WARNING(
                f"No hay registros PENDING en dataset '{dataset_slug}'. "
                f"Usa --force para re-procesar importados."
            ))
            return

        self.stdout.write(
            f"{'[DRY RUN] ' if dry_run else ''}Procesando {total} registros "
            f"del dataset '{dataset_slug}'"
            + (f" (categoría: {category_filter})" if category_filter else "")
        )

        # --- Procesar ---
        stats = {"created": 0, "skipped": 0, "errors": 0, "duplicates": 0}

        for record in qs.iterator():
            place, contact_points_or_error = build_place_from_record(
                record, categories, subcategories
            )

            if place is None:
                self.stdout.write(
                    self.style.WARNING(f"  SKIP [{record.external_id}]: {contact_points_or_error}")
                )
                stats["skipped"] += 1
                continue

            contact_points_data = contact_points_or_error

            # Detectar duplicado por google_place_id en metadata
            existing = Place.objects.filter(
                metadata__google_place_id=record.external_id
            ).first()

            if existing and not force:
                stats["duplicates"] += 1
                continue

            if dry_run:
                self.stdout.write(
                    f"  WOULD CREATE: '{place.name}' "
                    f"[{place.category.slug}] "
                    f"{'📍' if place.location else '⚠️  sin coords'} "
                    f"{place.commune}, {place.region}"
                )
                stats["created"] += 1
                continue

            try:
                with transaction.atomic():
                    if existing and force:
                        # Rehidrata la ficha existente sin romper su slug/status.
                        place = update_existing_place(existing, place)
                        place.save()
                        ContactPoint.objects.filter(place=place).delete()
                    else:
                        place.save()

                    # Crear ContactPoints
                    for cp_data in contact_points_data:
                        ContactPoint.objects.create(place=place, **cp_data)

                    # Marcar record como importado
                    record.mark_imported(place)

                stats["created"] += 1

            except Exception as exc:
                self.stdout.write(
                    self.style.ERROR(f"  ERROR [{record.external_id}] {record.raw_name}: {exc}")
                )
                stats["errors"] += 1

            # Progreso cada 50
            processed = stats["created"] + stats["errors"] + stats["skipped"]
            if processed % 50 == 0:
                self.stdout.write(f"  ... {processed}/{total} procesados")

        # --- Resumen ---
        self.stdout.write("\n" + "=" * 60)
        self.stdout.write(
            self.style.SUCCESS(
                f"{'[DRY RUN] ' if dry_run else ''}PROMOCIÓN COMPLETA"
            )
        )
        self.stdout.write(f"  {'Promovidos' if not dry_run else 'A promover'}: {stats['created']}")
        self.stdout.write(f"  Duplicados saltados:  {stats['duplicates']}")
        self.stdout.write(f"  Saltados (sin mapa):  {stats['skipped']}")
        self.stdout.write(f"  Errores:              {stats['errors']}")
        if not dry_run and stats["created"] > 0:
            self.stdout.write(
                self.style.WARNING(
                    f"\n  ⚠️  Los Places creados están en status DRAFT.\n"
                    f"  Revisalos en /admin/places/place/ y cambia a PUBLISHED cuando estén listos."
                )
            )
