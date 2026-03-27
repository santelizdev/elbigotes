from io import BytesIO
import re

from django.contrib.gis.geos import Point
from django.core.files.base import ContentFile
from django.utils.text import slugify
from rest_framework import serializers

from apps.accounts.models import PetOwnerProfile, PetProfile, User, UserRole
from apps.lost_pets.models import LostPetReport


def _optimize_lost_pet_photo(uploaded_file):
    if not uploaded_file:
        return None

    try:
        from PIL import Image, ImageOps
    except ImportError as exc:  # pragma: no cover - depende de la imagen del contenedor
        raise serializers.ValidationError(
            {"photo": "Pillow no está instalado en el backend. Reconstruye la imagen del proyecto."}
        ) from exc

    try:
        uploaded_file.seek(0)
        image = Image.open(uploaded_file)
        image = ImageOps.exif_transpose(image)
        image.load()
    except Exception as exc:  # noqa: BLE001
        raise serializers.ValidationError(
            {"photo": "No fue posible procesar la imagen subida."}
        ) from exc

    if image.width * image.height > 25_000_000:
        raise serializers.ValidationError(
            {"photo": "La imagen es demasiado grande para este servidor."}
        )

    if image.mode not in {"RGB", "L"}:
        image = image.convert("RGB")
    elif image.mode == "L":
        image = image.convert("RGB")

    image.thumbnail((1600, 1600))

    output = BytesIO()
    image.save(output, format="JPEG", quality=82, optimize=True, progressive=True)
    output.seek(0)

    file_stem = slugify(getattr(uploaded_file, "name", "mascota")) or "mascota"
    return ContentFile(output.read(), name=f"{file_stem}.jpg")


def _build_owner_seed_email(reporter_email: str, reporter_phone: str) -> str:
    if reporter_email:
        return reporter_email.strip().lower()

    normalized_phone = re.sub(r"\D", "", reporter_phone or "") or "anon"
    return f"lostpet-{normalized_phone}@petowners.elbigotes.local"


def _extract_commune_from_address(address: str) -> str:
    parts = [part.strip() for part in (address or "").split(",") if part.strip()]
    return parts[-1] if parts else ""


def _sync_owner_and_pet_profiles(report: LostPetReport) -> None:
    owner_email = _build_owner_seed_email(report.reporter_email, report.reporter_phone)
    owner_user, created = User.objects.get_or_create(
        email=owner_email,
        defaults={
            "first_name": report.reporter_name,
            "role": UserRole.PET_OWNER,
            "is_active": False,
        },
    )
    if created:
        owner_user.set_unusable_password()
        owner_user.save(update_fields=["password", "username"])

    if not owner_user.first_name and report.reporter_name:
        owner_user.first_name = report.reporter_name
        owner_user.save(update_fields=["first_name"])

    owner_profile, _ = PetOwnerProfile.objects.get_or_create(
        user=owner_user,
        defaults={
            "phone": report.reporter_phone,
            "address_line": report.last_seen_address,
            "commune": _extract_commune_from_address(report.last_seen_address),
            "region": "Región Metropolitana",
            "marketing_opt_in": False,
        },
    )
    if not owner_profile.phone:
        owner_profile.phone = report.reporter_phone
    if report.last_seen_address and not owner_profile.address_line:
        owner_profile.address_line = report.last_seen_address
    if not owner_profile.commune:
        owner_profile.commune = _extract_commune_from_address(report.last_seen_address)
    owner_profile.save()

    pet_profile, _ = PetProfile.objects.get_or_create(
        owner=owner_profile,
        name=report.pet_name,
        species=report.species,
        defaults={
            "breed": report.breed,
            "sex": report.sex,
        },
    )
    if report.breed and not pet_profile.breed:
        pet_profile.breed = report.breed
    if pet_profile.sex == "unknown" and report.sex:
        pet_profile.sex = report.sex
    pet_profile.save()

    report.metadata = {
        **report.metadata,
        "pet_owner_profile_id": owner_profile.id,
        "pet_profile_id": pet_profile.id,
    }
    report.pet_profile = pet_profile
    report.save(update_fields=["metadata", "pet_profile", "updated_at"])


def create_lost_pet_report(validated_data):
    """
    Convierte coordenadas primitivas a geometría PostGIS en un solo punto de entrada.
    Así la API no filtra detalles de persistencia hacia serializers o vistas.
    """

    latitude = validated_data.pop("last_seen_latitude", None)
    longitude = validated_data.pop("last_seen_longitude", None)
    photo = validated_data.pop("photo", None)
    validated_data["last_seen_location"] = (
        Point(float(longitude), float(latitude), srid=4326)
        if latitude is not None and longitude is not None
        else None
    )
    validated_data["photo"] = _optimize_lost_pet_photo(photo)
    report = LostPetReport.objects.create(**validated_data)
    _sync_owner_and_pet_profiles(report)
    return report
