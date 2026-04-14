from django.db import migrations, models


def backfill_place_verification_status(apps, schema_editor):
    ClaimRequest = apps.get_model("claims", "ClaimRequest")
    Place = apps.get_model("places", "Place")

    Place.objects.filter(is_verified=True).update(verification_status="verified")
    Place.objects.filter(is_verified=False).update(verification_status="unverified")
    claimed_place_ids = ClaimRequest.objects.filter(
        status__in=["pending", "under_review"]
    ).values_list("place_id", flat=True)
    Place.objects.filter(id__in=claimed_place_ids, is_verified=False).update(
        verification_status="claim_requested"
    )


def reverse_place_verification_status(apps, schema_editor):
    Place = apps.get_model("places", "Place")
    Place.objects.filter(verification_status="verified").update(is_verified=True)
    Place.objects.exclude(verification_status="verified").update(is_verified=False)


class Migration(migrations.Migration):

    dependencies = [
        ("claims", "0001_initial"),
        ("places", "0005_place_google_reputation_fields"),
    ]

    operations = [
        migrations.AddField(
            model_name="place",
            name="verification_status",
            field=models.CharField(
                choices=[
                    ("unverified", "Unverified"),
                    ("claim_requested", "Claim requested"),
                    ("verified", "Verified"),
                ],
                default="unverified",
                max_length=24,
            ),
        ),
        migrations.RunPython(backfill_place_verification_status, reverse_place_verification_status),
    ]
