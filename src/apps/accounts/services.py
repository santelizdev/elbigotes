from django.contrib.gis.geos import Point
from django.db import transaction

from apps.accounts.models import (
    BusinessKind,
    BusinessProfile,
    PetOwnerProfile,
    PetProfile,
    User,
    UserRole,
)
from apps.ingestion.models import Source, SourceKind
from apps.places.choices import ContactPointKind, PlaceStatus
from apps.places.models import ContactPoint, Place
from apps.taxonomy.models import Category

BUSINESS_KIND_TO_CATEGORY = {
    BusinessKind.VETERINARY: "veterinarias",
    BusinessKind.DAYCARE: "guarderias",
    BusinessKind.EMERGENCY: "emergencias-veterinarias",
    BusinessKind.SHELTER: "refugios-albergues",
    BusinessKind.PARK: "parques-pet-friendly",
}


def _get_registration_source():
    source, _ = Source.objects.get_or_create(
        slug="business-registration",
        defaults={
            "name": "Business Registration",
            "kind": SourceKind.PARTNER,
            "reliability_score": 0.65,
        },
    )
    return source


def _get_category_for_business_kind(business_kind: str):
    category_slug = BUSINESS_KIND_TO_CATEGORY[business_kind]
    return Category.objects.get(slug=category_slug)


def _sync_contact_points(place: Place, *, phone: str, email: str, website: str) -> None:
    ContactPoint.objects.update_or_create(
        place=place,
        kind=ContactPointKind.PHONE,
        value=phone,
        defaults={"label": "Contacto principal", "is_primary": True},
    )
    ContactPoint.objects.update_or_create(
        place=place,
        kind=ContactPointKind.EMAIL,
        value=email,
        defaults={"label": "Email", "is_primary": False},
    )
    if website:
        ContactPoint.objects.update_or_create(
            place=place,
            kind=ContactPointKind.WEBSITE,
            value=website,
            defaults={"label": "Sitio web", "is_primary": False},
        )


def _apply_business_place_fields(place, *, profile, user, place_data, is_primary: bool):
    category = _get_category_for_business_kind(place_data["business_kind"])
    source = _get_registration_source()
    latitude = place_data["latitude"]
    longitude = place_data["longitude"]
    place_label = place_data["place_label"]

    place.source = source
    place.owner_business_profile = profile
    place.name = place_data["business_name"]
    place.category = category
    place.summary = "Alta comercial creada desde registro publico."
    place.description = (
        f"Ficha creada desde el registro inicial de {user.first_name or user.email}."
        if is_primary
        else f"Sucursal adicional creada desde el area cliente de {user.first_name or user.email}."
    )
    place.status = PlaceStatus.DRAFT
    place.formatted_address = f"{place_label}, {place_data['commune']}, {place_data['region']}"
    place.street_address = place_label
    place.commune = place_data["commune"]
    place.region = place_data["region"]
    place.country = "Chile"
    place.website = place_data.get("website", "")
    place.is_verified = False
    place.is_emergency_service = place_data["business_kind"] == BusinessKind.EMERGENCY
    place.is_open_24_7 = place_data["business_kind"] == BusinessKind.EMERGENCY
    place.location = Point(float(longitude), float(latitude), srid=4326)
    place.metadata = {
        **place.metadata,
        "registration_origin": "public_business_signup" if is_primary else "business_branch_signup",
        "registration_email": user.email,
        "public_contact_email": user.email,
        "email_verification_status": "pending",
    }
    place.save()
    _sync_contact_points(
        place,
        phone=place_data["phone"],
        email=user.email,
        website=place_data.get("website", ""),
    )
    return place


def _build_primary_place_for_business(profile, profile_data, user):
    place = (
        Place.objects.filter(
            name__iexact=profile_data["business_name"],
            commune__iexact=profile_data["commune"],
            category=_get_category_for_business_kind(profile_data["business_kind"]),
        )
        .order_by("id")
        .first()
    ) or Place()
    return _apply_business_place_fields(
        place,
        profile=profile,
        user=user,
        place_data=profile_data,
        is_primary=True,
    )


@transaction.atomic
def register_business_account(validated_data):
    password = validated_data.pop("password")
    user = User.objects.create_user(
        password=password,
        role=UserRole.BUSINESS_OWNER,
        **validated_data["user"],
    )
    profile_data = validated_data["profile"].copy()
    profile = BusinessProfile.objects.create(
        user=user,
        place=None,
        **{
            key: value
            for key, value in profile_data.items()
            if key not in {"place_label", "latitude", "longitude"}
        },
    )
    place = _build_primary_place_for_business(profile, profile_data, user)
    profile.place = place
    profile.save(update_fields=["place", "updated_at"])
    return user, profile


@transaction.atomic
def update_business_account(profile: BusinessProfile, validated_data):
    user_data = validated_data.get("user", {})
    profile_data = validated_data.get("profile", {})

    if "first_name" in user_data:
        profile.user.first_name = user_data["first_name"]
    if "last_name" in user_data:
        profile.user.last_name = user_data["last_name"]
    profile.user.save(update_fields=["first_name", "last_name", "updated_at"])

    for field in ("business_name", "phone", "commune", "region", "website", "marketing_opt_in", "notes"):
        if field in profile_data:
            setattr(profile, field, profile_data[field])
    profile.save()

    if profile.place_id:
        place_data = {
            "business_name": profile.business_name,
            "business_kind": profile.business_kind,
            "phone": profile.phone,
            "commune": profile.commune,
            "region": profile.region,
            "website": profile.website,
            "place_label": profile.place.street_address or profile.place.formatted_address or "Punto principal",
            "latitude": profile.place.location.y,
            "longitude": profile.place.location.x,
        }
        _apply_business_place_fields(
            profile.place,
            profile=profile,
            user=profile.user,
            place_data=place_data,
            is_primary=True,
        )

    return profile.user, profile


@transaction.atomic
def create_business_branch(profile: BusinessProfile, validated_data):
    place = _apply_business_place_fields(
        Place(),
        profile=profile,
        user=profile.user,
        place_data={
            "business_name": validated_data["branch_name"],
            "business_kind": profile.business_kind,
            "phone": validated_data.get("phone") or profile.phone,
            "commune": validated_data["commune"],
            "region": validated_data["region"],
            "website": validated_data.get("website", ""),
            "place_label": validated_data["place_label"],
            "latitude": validated_data["latitude"],
            "longitude": validated_data["longitude"],
        },
        is_primary=False,
    )
    return place


@transaction.atomic
def register_pet_owner_account(validated_data):
    password = validated_data.pop("password")
    initial_pet = validated_data.pop("pet")
    user = User.objects.create_user(
        password=password,
        role=UserRole.PET_OWNER,
        **validated_data["user"],
    )
    profile = PetOwnerProfile.objects.create(user=user, **validated_data["profile"])
    pet = PetProfile.objects.create(owner=profile, **initial_pet)
    return user, profile, pet
