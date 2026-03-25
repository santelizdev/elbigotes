import uuid

import django.contrib.gis.db.models.fields
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("ingestion", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="LostPetReport",
            fields=[
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("pet_name", models.CharField(max_length=120)),
                (
                    "species",
                    models.CharField(choices=[("dog", "Dog"), ("cat", "Cat"), ("other", "Other")], max_length=20),
                ),
                ("breed", models.CharField(blank=True, max_length=120)),
                (
                    "sex",
                    models.CharField(
                        choices=[("male", "Male"), ("female", "Female"), ("unknown", "Unknown")],
                        default="unknown",
                        max_length=20,
                    ),
                ),
                ("color_description", models.CharField(max_length=255)),
                ("distinctive_marks", models.TextField(blank=True)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("lost", "Lost"),
                            ("sighted", "Sighted"),
                            ("found", "Found"),
                            ("closed", "Closed"),
                        ],
                        default="lost",
                        max_length=20,
                    ),
                ),
                ("last_seen_at", models.DateTimeField()),
                (
                    "last_seen_location",
                    django.contrib.gis.db.models.fields.PointField(geography=True, srid=4326),
                ),
                ("last_seen_address", models.CharField(max_length=255)),
                ("last_seen_reference", models.CharField(blank=True, max_length=255)),
                ("reporter_name", models.CharField(max_length=120)),
                ("reporter_phone", models.CharField(max_length=40)),
                ("reporter_email", models.EmailField(blank=True, max_length=254)),
                ("additional_contact", models.CharField(blank=True, max_length=255)),
                ("photo_url", models.URLField(blank=True)),
                ("is_reward_offered", models.BooleanField(default=False)),
                ("reward_amount", models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ("metadata", models.JSONField(blank=True, default=dict)),
                (
                    "source",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=models.deletion.SET_NULL,
                        related_name="lost_pet_reports",
                        to="ingestion.source",
                    ),
                ),
            ],
            options={
                "verbose_name": "Lost pet report",
                "verbose_name_plural": "Lost pet reports",
                "ordering": ["-last_seen_at", "-created_at"],
            },
        ),
    ]
