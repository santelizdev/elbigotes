import csv
import hashlib
from dataclasses import dataclass, field
from pathlib import Path

from django.contrib.gis.geos import Point
from django.db import transaction
from django.utils import timezone
from django.utils.text import slugify

from apps.ingestion.models import ImportedPlaceRecord, ImportRecordStatus, Source, SourceDataset
from apps.ingestion.services.normalization import (
    resolve_category_pair,
    resolve_pet_map_category,
)
from apps.places.choices import ContactPointKind, PlaceStatus
from apps.places.models import ContactPoint, Place
from apps.places.services.quality import audit_single_place

PET_PLACE_REQUIRED_COLUMNS = {
    "country",
    "region",
    "commune",
    "category",
    "name",
    "address",
    "latitude",
    "longitude",
    "phone",
    "email",
    "website",
    "source",
    "notes",
}
PET_PLACE_DEFAULT_COUNTRY = "Chile"
PET_PLACE_DEFAULT_REGION = "Región Metropolitana"


@dataclass
class ImportSummary:
    processed: int = 0
    created: int = 0
    updated: int = 0
    failed: int = 0
    skipped: int = 0
    geocoding_needed: int = 0
    error_messages: list[str] = field(default_factory=list)

    @property
    def ignored(self) -> int:
        return self.skipped


def _clean_string(value) -> str:
    return str(value or "").strip()


def _build_formatted_address(*parts: str) -> str:
    return ", ".join(part for part in (_clean_string(part) for part in parts) if part)


def _row_checksum(row: dict) -> str:
    serialized = "|".join(f"{key}={value}" for key, value in sorted(row.items()))
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


def _parse_bool(raw_value: str) -> bool:
    return str(raw_value).strip().lower() in {"1", "true", "yes", "si", "sí"}


def _build_dataset(source: Source, dataset_slug: str | None, dataset_name: str | None):
    resolved_name = dataset_name or dataset_slug or f"import-{timezone.now():%Y%m%d}"
    resolved_slug = dataset_slug or slugify(resolved_name)
    dataset, _ = SourceDataset.objects.get_or_create(
        source=source,
        slug=resolved_slug,
        defaults={"name": resolved_name},
    )
    return dataset


def _humanize_source_name(raw_source: str) -> str:
    normalized = raw_source.replace("_", " ").replace("-", " ").strip()
    return normalized.title() or "Manual Seed"


def _resolve_source(raw_source: str | None) -> Source:
    source_value = _clean_string(raw_source) or "manual_seed"
    source_slug = slugify(source_value.replace("_", "-")) or "manual-seed"
    source, _ = Source.objects.get_or_create(
        slug=source_slug,
        defaults={
            "name": _humanize_source_name(source_value),
            "kind": "manual",
            "reliability_score": 0.70,
        },
    )
    return source


def _build_pet_places_dataset(
    source: Source,
    csv_path: str,
    dataset_name: str | None,
) -> SourceDataset:
    base_name = (
        dataset_name
        or Path(csv_path).stem.replace("-", " ").replace("_", " ").strip()
        or "Pet places"
    )
    resolved_name = base_name.title()
    resolved_slug = slugify(f"{source.slug}-{Path(csv_path).stem}") or f"{source.slug}-pet-places"
    dataset, _ = SourceDataset.objects.get_or_create(
        source=source,
        slug=resolved_slug,
        defaults={
            "name": resolved_name,
            "default_country": PET_PLACE_DEFAULT_COUNTRY,
            "default_region": PET_PLACE_DEFAULT_REGION,
        },
    )
    return dataset


def _require_columns(fieldnames: list[str] | None, required_columns: set[str]) -> None:
    normalized = {_clean_string(name).lstrip("\ufeff") for name in fieldnames or []}
    missing = sorted(required_columns - normalized)
    if missing:
        raise ValueError(f"Faltan columnas requeridas en el CSV: {', '.join(missing)}.")


def _is_empty_row(row: dict) -> bool:
    return not any(_clean_string(value) for value in row.values())


def _parse_coordinates(row: dict) -> tuple[float | None, float | None]:
    raw_latitude = _clean_string(row.get("latitude"))
    raw_longitude = _clean_string(row.get("longitude"))

    if not raw_latitude and not raw_longitude:
        return None, None

    if not raw_latitude or not raw_longitude:
        raise ValueError("Debes informar latitude y longitude juntos o dejar ambos vacíos.")

    try:
        return float(raw_latitude), float(raw_longitude)
    except ValueError as exc:
        raise ValueError("Latitude y longitude deben ser numéricos.") from exc


def _build_pet_place_external_id(name: str, commune: str, category_slug: str) -> str:
    signature = f"{name.lower()}|{commune.lower()}|{category_slug}"
    digest = hashlib.sha1(signature.encode("utf-8")).hexdigest()[:16]
    return f"{slugify(name)[:40] or 'place'}-{digest}"


def _find_duplicate_place(name: str, commune: str, category_id: int) -> Place | None:
    return (
        Place.objects.filter(
            name__iexact=name,
            commune__iexact=commune,
            category_id=category_id,
        )
        .order_by("id")
        .first()
    )


def _sync_contact_points(place: Place, *, phone: str, email: str, website: str) -> None:
    if phone:
        ContactPoint.objects.update_or_create(
            place=place,
            kind=ContactPointKind.PHONE,
            value=phone,
            defaults={"label": "Principal", "is_primary": True},
        )
    if email:
        ContactPoint.objects.update_or_create(
            place=place,
            kind=ContactPointKind.EMAIL,
            value=email,
            defaults={"label": "Email", "is_primary": not bool(phone)},
        )
    if website:
        ContactPoint.objects.update_or_create(
            place=place,
            kind=ContactPointKind.WEBSITE,
            value=website,
            defaults={"label": "Sitio web", "is_primary": False},
        )


def _save_failed_record(
    *,
    dataset: SourceDataset | None,
    source: Source | None,
    external_id: str,
    row: dict,
    message: str,
) -> None:
    if not dataset or not source:
        return

    ImportedPlaceRecord.objects.update_or_create(
        dataset=dataset,
        external_id=external_id,
        defaults={
            "source": source,
            "raw_name": _clean_string(row.get("name")),
            "raw_address": _clean_string(row.get("address")),
            "raw_payload": row,
            "checksum": _row_checksum(row),
            "status": ImportRecordStatus.FAILED,
            "notes": message,
        },
    )


@transaction.atomic
def import_places_from_csv(
    csv_path: str,
    *,
    source_slug: str,
    dataset_slug: str | None = None,
    dataset_name: str | None = None,
    update_existing: bool = False,
) -> ImportSummary:
    """
    Importa filas desde CSV preservando trazabilidad por registro.
    La importación no intenta resolver toda la calidad del dato en el mismo paso; solo deja el
    sistema en un estado moderable y listo para geocodificación/auditoría posterior.
    """

    source = Source.objects.get(slug=source_slug)
    dataset = _build_dataset(source, dataset_slug, dataset_name)
    summary = ImportSummary()

    with Path(csv_path).open(newline="", encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)

        for row in reader:
            external_id = (row.get("external_id") or "").strip()
            name = (row.get("name") or "").strip()
            checksum = _row_checksum(row)

            if not external_id or not name:
                summary.failed += 1
                continue

            record, _ = ImportedPlaceRecord.objects.get_or_create(
                dataset=dataset,
                external_id=external_id,
                defaults={
                    "source": source,
                    "raw_name": name,
                    "raw_address": (
                        (row.get("formatted_address") or row.get("street_address") or "").strip()
                    ),
                    "raw_payload": row,
                    "checksum": checksum,
                },
            )

            if (
                record.checksum == checksum
                and record.status == ImportRecordStatus.IMPORTED
                and not update_existing
            ):
                summary.skipped += 1
                continue

            if record.imported_place_id and not update_existing:
                summary.skipped += 1
                continue

            try:
                category, subcategory = resolve_category_pair(
                    row.get("category", ""),
                    row.get("subcategory", ""),
                )
            except ValueError as exc:
                record.status = ImportRecordStatus.FAILED
                record.notes = str(exc)
                record.raw_payload = row
                record.save(update_fields=["status", "notes", "raw_payload", "updated_at"])
                summary.failed += 1
                continue

            place = record.imported_place
            if not place:
                place = Place(source=source)

            latitude = (row.get("latitude") or "").strip()
            longitude = (row.get("longitude") or "").strip()

            place.name = name
            place.summary = (row.get("summary") or "").strip()
            place.description = (row.get("description") or "").strip()
            place.category = category
            place.subcategory = subcategory
            requested_status = row.get("status", PlaceStatus.DRAFT) or PlaceStatus.DRAFT
            valid_statuses = {choice for choice, _ in PlaceStatus.choices}
            place.status = (
                requested_status if requested_status in valid_statuses else PlaceStatus.DRAFT
            )
            place.commune = (row.get("commune") or "").strip()
            place.region = (row.get("region") or dataset.default_region or "").strip()
            place.country = (row.get("country") or dataset.default_country or "Chile").strip()
            place.street_address = (row.get("street_address") or "").strip()
            raw_formatted_address = (row.get("formatted_address") or "").strip()
            place.formatted_address = raw_formatted_address or _build_formatted_address(
                place.street_address,
                place.commune,
                place.region,
                place.country,
            )
            place.website = (row.get("website") or "").strip()
            place.is_verified = _parse_bool(row.get("is_verified", ""))
            place.is_emergency_service = _parse_bool(row.get("is_emergency_service", ""))
            place.is_open_24_7 = _parse_bool(row.get("is_open_24_7", ""))
            place.metadata = {
                "source_url": (row.get("source_url") or "").strip(),
                "opening_hours": (row.get("opening_hours") or "").strip(),
                "import_notes": (row.get("notes") or "").strip(),
            }

            if latitude and longitude:
                place.location = Point(float(longitude), float(latitude), srid=4326)
            else:
                place.location = place.location or None
                if not place.location:
                    summary.geocoding_needed += 1

            place.save()

            if record.imported_place_id:
                summary.updated += 1
            else:
                summary.created += 1

            phone = (row.get("phone") or "").strip()
            email = (row.get("email") or "").strip()
            website = (row.get("website") or "").strip()

            if phone:
                ContactPoint.objects.update_or_create(
                    place=place,
                    kind=ContactPointKind.PHONE,
                    value=phone,
                    defaults={"label": "Principal", "is_primary": True},
                )
            if email:
                ContactPoint.objects.update_or_create(
                    place=place,
                    kind=ContactPointKind.EMAIL,
                    value=email,
                    defaults={"label": "Email", "is_primary": not bool(phone)},
                )
            if website:
                ContactPoint.objects.update_or_create(
                    place=place,
                    kind=ContactPointKind.WEBSITE,
                    value=website,
                    defaults={"label": "Website", "is_primary": False},
                )

            record.source = source
            record.raw_name = name
            record.raw_address = place.formatted_address or place.street_address
            record.raw_payload = row
            record.checksum = checksum
            record.notes = ""
            record.save(
                update_fields=[
                    "source",
                    "raw_name",
                    "raw_address",
                    "raw_payload",
                    "checksum",
                    "notes",
                    "updated_at",
                ]
            )
            record.mark_imported(place)

            audit_single_place(place)

    return summary


@transaction.atomic
def import_pet_places_from_csv(
    csv_path: str,
    *,
    dataset_name: str | None = None,
    default_source: str = "manual_seed",
    update_existing: bool = False,
) -> ImportSummary:
    """
    Importa el CSV operativo del mapa público usando el modelo Place actual.
    El flujo intenta ser estricto con el formato y conservador con los duplicados.
    """

    summary = ImportSummary()
    dataset_cache: dict[str, SourceDataset] = {}

    with Path(csv_path).open(newline="", encoding="utf-8-sig") as csv_file:
        reader = csv.DictReader(csv_file)
        _require_columns(reader.fieldnames, PET_PLACE_REQUIRED_COLUMNS)

        for index, raw_row in enumerate(reader, start=2):
            row = {key.lstrip("\ufeff"): _clean_string(value) for key, value in raw_row.items()}
            if _is_empty_row(row):
                continue

            summary.processed += 1
            source = None
            dataset = None
            external_id = f"line-{index}"

            try:
                name = row["name"]
                commune = row["commune"]
                raw_category = row["category"]
                address = row["address"]
                phone = row["phone"]
                email = row["email"]
                website = row["website"]
                notes = row["notes"]
                source = _resolve_source(row.get("source") or default_source)
                dataset = dataset_cache.get(source.slug)
                if dataset is None:
                    dataset = _build_pet_places_dataset(source, csv_path, dataset_name)
                    dataset_cache[source.slug] = dataset

                if not name:
                    raise ValueError("El campo name es obligatorio.")
                if not commune:
                    raise ValueError("El campo commune es obligatorio.")

                category = resolve_pet_map_category(raw_category)
                external_id = _build_pet_place_external_id(name, commune, category.slug)
                latitude, longitude = _parse_coordinates(row)

                has_coordinates = latitude is not None and longitude is not None
                if not any([address, has_coordinates, phone, website]):
                    raise ValueError(
                        "Cada fila debe informar address, latitude+longitude, phone o website."
                    )

                checksum = _row_checksum(row)
                record, _ = ImportedPlaceRecord.objects.get_or_create(
                    dataset=dataset,
                    external_id=external_id,
                    defaults={
                        "source": source,
                        "raw_name": name,
                        "raw_address": address,
                        "raw_payload": row,
                        "checksum": checksum,
                    },
                )

                if record.checksum == checksum and record.status == ImportRecordStatus.IMPORTED:
                    summary.skipped += 1
                    continue

                place = record.imported_place or _find_duplicate_place(name, commune, category.id)
                created = place is None

                if place and record.imported_place_id is None and not update_existing:
                    record.source = source
                    record.raw_name = name
                    record.raw_address = address
                    record.raw_payload = row
                    record.checksum = checksum
                    record.status = ImportRecordStatus.SKIPPED
                    record.notes = (
                        "Fila omitida por duplicado razonable: mismo nombre, comuna y categoría."
                    )
                    record.imported_place = place
                    record.save(
                        update_fields=[
                            "source",
                            "raw_name",
                            "raw_address",
                            "raw_payload",
                            "checksum",
                            "status",
                            "notes",
                            "imported_place",
                            "updated_at",
                        ]
                    )
                    summary.skipped += 1
                    continue

                if place is None:
                    place = Place(source=source)

                point = Point(longitude, latitude, srid=4326) if has_coordinates else None
                region = row["region"] or dataset.default_region or PET_PLACE_DEFAULT_REGION
                country = row["country"] or dataset.default_country or PET_PLACE_DEFAULT_COUNTRY

                place.name = name
                place.category = category
                place.subcategory = None
                place.summary = notes[:280]
                place.description = notes
                place.street_address = address
                place.commune = commune
                place.region = region
                place.country = country
                place.formatted_address = _build_formatted_address(
                    address,
                    commune,
                    region,
                    country,
                )
                place.website = website
                place.source = source
                place.is_verified = False
                place.is_emergency_service = category.slug == "emergencias-veterinarias"
                place.is_open_24_7 = False
                place.status = PlaceStatus.ACTIVE if point or place.location else PlaceStatus.DRAFT
                place.location = point if point else place.location
                place.metadata = {
                    **place.metadata,
                    "raw_category": raw_category,
                    "import_notes": notes,
                    "import_source": row.get("source") or default_source,
                    "import_source_file": Path(csv_path).name,
                    "review_status": "pending" if not (point or place.location) else "ready",
                }
                place.save()

                _sync_contact_points(place, phone=phone, email=email, website=website)

                findings = audit_single_place(place)
                if any(finding.code == "missing_location" for finding in findings):
                    summary.geocoding_needed += 1

                record.source = source
                record.raw_name = name
                record.raw_address = address
                record.raw_payload = row
                record.checksum = checksum
                record.notes = ""
                record.save(
                    update_fields=[
                        "source",
                        "raw_name",
                        "raw_address",
                        "raw_payload",
                        "checksum",
                        "notes",
                        "updated_at",
                    ]
                )
                record.mark_imported(place)

                if created:
                    summary.created += 1
                else:
                    summary.updated += 1
            except Exception as exc:  # noqa: BLE001
                message = f"Línea {index}: {exc}"
                _save_failed_record(
                    dataset=dataset,
                    source=source,
                    external_id=external_id,
                    row=row,
                    message=message,
                )
                summary.failed += 1
                summary.error_messages.append(message)

    return summary
