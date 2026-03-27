from io import BytesIO

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image
from rest_framework.test import APIClient

from apps.accounts.models import PetOwnerProfile, PetProfile, User, UserRole
from apps.lost_pets.choices import LostPetModerationStatus
from apps.lost_pets.models import LostPetReport


def _build_uploaded_photo() -> SimpleUploadedFile:
    image_bytes = BytesIO()
    image = Image.new("RGB", (1200, 800), color=(13, 153, 149))
    image.save(image_bytes, format="PNG")
    image_bytes.seek(0)
    return SimpleUploadedFile("perdido.png", image_bytes.read(), content_type="image/png")


@pytest.mark.django_db
def test_create_lost_pet_report_accepts_multipart_photo_without_coordinates(tmp_path, settings):
    settings.MEDIA_ROOT = tmp_path
    client = APIClient()

    response = client.post(
        "/api/v1/lost-pets/reports/",
        data={
            "pet_name": "Luna",
            "species": "dog",
            "breed": "Mestiza",
            "sex": "female",
            "color_description": "Blanca con manchas menta",
            "status": "lost",
            "last_seen_at": "2026-03-20T12:30:00Z",
            "last_seen_address": "Providencia 1234, Providencia",
            "last_seen_reference": "Cerca del metro",
            "reporter_name": "Camila",
            "reporter_phone": "+56912345678",
            "reporter_email": "camila@example.com",
            "is_reward_offered": "false",
            "photo": _build_uploaded_photo(),
        },
        format="multipart",
    )

    assert response.status_code == 201
    assert response.data["pet_name"] == "Luna"
    assert response.data["latitude"] is None
    assert response.data["longitude"] is None
    assert response.data["photo_url"].endswith(".jpg")

    report = LostPetReport.objects.get(pet_name="Luna")
    assert report.last_seen_location is None
    assert report.photo.name.endswith(".jpg")

    owner_user = User.objects.get(email="camila@example.com")
    owner_profile = PetOwnerProfile.objects.get(user=owner_user)
    pet_profile = PetProfile.objects.get(owner=owner_profile, name="Luna")

    assert owner_user.role == UserRole.PET_OWNER
    assert owner_profile.phone == "+56912345678"
    assert pet_profile.species == "dog"
    assert report.pet_profile == pet_profile


@pytest.mark.django_db
def test_create_lost_pet_report_without_email_creates_seed_pet_owner_account():
    client = APIClient()

    response = client.post(
        "/api/v1/lost-pets/reports/",
        data={
            "pet_name": "Rayo",
            "species": "dog",
            "sex": "male",
            "color_description": "Negro",
            "status": "lost",
            "last_seen_at": "2026-03-20T12:30:00Z",
            "last_seen_address": "Diagonal 123, Ñuñoa",
            "last_seen_reference": "Plaza cercana",
            "last_seen_latitude": "-33.4562",
            "last_seen_longitude": "-70.5973",
            "reporter_name": "Diego",
            "reporter_phone": "+56933334444",
            "is_reward_offered": "false",
        },
        format="multipart",
    )

    assert response.status_code == 201

    owner_user = User.objects.get(email="lostpet-56933334444@petowners.elbigotes.local")
    owner_profile = PetOwnerProfile.objects.get(user=owner_user)
    pet_profile = PetProfile.objects.get(owner=owner_profile, name="Rayo")
    report = LostPetReport.objects.get(pet_name="Rayo")

    assert owner_user.role == UserRole.PET_OWNER
    assert owner_profile.commune == "Ñuñoa"
    assert pet_profile.species == "dog"
    assert report.pet_profile == pet_profile


@pytest.mark.django_db
def test_create_lost_pet_report_rejects_invalid_photo_content_type():
    client = APIClient()

    response = client.post(
        "/api/v1/lost-pets/reports/",
        data={
            "pet_name": "Toby",
            "species": "dog",
            "sex": "male",
            "color_description": "Cafe",
            "status": "lost",
            "last_seen_at": "2026-03-20T12:30:00Z",
            "last_seen_address": "Santiago Centro",
            "reporter_name": "Diego",
            "reporter_phone": "+56987654321",
            "is_reward_offered": "false",
            "photo": SimpleUploadedFile(
                "fake.gif",
                b"GIF89a",
                content_type="image/gif",
            ),
        },
        format="multipart",
    )

    assert response.status_code == 400
    assert "photo" in response.data


@pytest.mark.django_db
def test_create_lost_pet_report_rejects_recent_duplicate_report():
    client = APIClient()
    payload = {
        "pet_name": "Luna",
        "species": "dog",
        "sex": "female",
        "color_description": "Cafe",
        "status": "lost",
        "last_seen_at": "2026-03-20T12:30:00Z",
        "last_seen_address": "Providencia 123",
        "reporter_name": "Ana",
        "reporter_phone": "+56911111111",
        "is_reward_offered": "false",
    }

    first_response = client.post(
        "/api/v1/lost-pets/reports/",
        data=payload,
        format="multipart",
    )
    second_response = client.post(
        "/api/v1/lost-pets/reports/",
        data=payload,
        format="multipart",
    )

    assert first_response.status_code == 201
    assert second_response.status_code == 400


@pytest.mark.django_db
def test_lost_pet_list_only_returns_approved_reports():
    client = APIClient()
    approved = LostPetReport.objects.create(
        pet_name="Bruno",
        species="dog",
        sex="male",
        color_description="Cafe",
        status="lost",
        last_seen_at="2026-03-20T12:30:00Z",
        last_seen_address="Santiago Centro",
        reporter_name="Ana",
        reporter_phone="+56900001111",
        moderation_status=LostPetModerationStatus.APPROVED,
    )
    LostPetReport.objects.create(
        pet_name="Nina",
        species="cat",
        sex="female",
        color_description="Gris",
        status="lost",
        last_seen_at="2026-03-20T12:40:00Z",
        last_seen_address="Providencia",
        reporter_name="Luz",
        reporter_phone="+56900002222",
        moderation_status=LostPetModerationStatus.PENDING,
    )

    response = client.get("/api/v1/lost-pets/reports/")

    assert response.status_code == 200
    assert len(response.data["results"]) == 1
    assert response.data["results"][0]["id"] == str(approved.id)
