from decimal import Decimal, InvalidOperation

import django.core.validators
from django.db import migrations, models


def build_google_maps_url(place_id: str) -> str:
    if not place_id:
        return ""
    return f"https://www.google.com/maps/place/?q=place_id:{place_id}"


def backfill_google_reputation(apps, schema_editor):
    Place = apps.get_model("places", "Place")

    for place in Place.objects.iterator():
        metadata = place.metadata or {}
        rating = metadata.get("google_rating")
        reviews_count = metadata.get("google_total_ratings", 0) or 0
        google_place_id = metadata.get("google_place_id", "")

        update_fields = []

        if rating is not None and place.google_rating is None:
            try:
                place.google_rating = Decimal(str(rating)).quantize(Decimal("0.1"))
                update_fields.append("google_rating")
            except (InvalidOperation, TypeError, ValueError):
                pass

        if reviews_count and not place.google_reviews_count:
            try:
                place.google_reviews_count = max(int(reviews_count), 0)
                update_fields.append("google_reviews_count")
            except (TypeError, ValueError):
                pass

        if google_place_id and not place.google_maps_url:
            place.google_maps_url = build_google_maps_url(str(google_place_id))
            update_fields.append("google_maps_url")

        if update_fields:
            place.save(update_fields=update_fields)


class Migration(migrations.Migration):

    dependencies = [
        ("places", "0004_place_owner_business_profile"),
    ]

    operations = [
        migrations.AddField(
            model_name="place",
            name="google_maps_url",
            field=models.URLField(blank=True),
        ),
        migrations.AddField(
            model_name="place",
            name="google_rating",
            field=models.DecimalField(
                blank=True,
                decimal_places=1,
                max_digits=2,
                null=True,
                validators=[
                    django.core.validators.MinValueValidator(0),
                    django.core.validators.MaxValueValidator(5),
                ],
            ),
        ),
        migrations.AddField(
            model_name="place",
            name="google_reviews_count",
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.RunPython(backfill_google_reputation, migrations.RunPython.noop),
    ]
