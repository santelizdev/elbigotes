import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("places", "0002_operational_quality"),
        ("ingestion", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="SourceDataset",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=150)),
                ("slug", models.SlugField(max_length=220, unique=True)),
                ("description", models.TextField(blank=True)),
                ("default_country", models.CharField(default="Chile", max_length=120)),
                ("default_region", models.CharField(blank=True, max_length=120)),
                ("metadata", models.JSONField(blank=True, default=dict)),
                ("is_active", models.BooleanField(default=True)),
                (
                    "source",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="datasets",
                        to="ingestion.source",
                    ),
                ),
            ],
            options={
                "verbose_name": "Source dataset",
                "verbose_name_plural": "Source datasets",
                "ordering": ["source__name", "name"],
            },
        ),
        migrations.CreateModel(
            name="GeocodingLog",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("provider", models.CharField(max_length=40)),
                ("query", models.CharField(max_length=255)),
                (
                    "status",
                    models.CharField(
                        choices=[("pending", "Pending"), ("succeeded", "Succeeded"), ("failed", "Failed")],
                        max_length=20,
                    ),
                ),
                ("matched_address", models.CharField(blank=True, max_length=255)),
                ("latitude", models.FloatField(blank=True, null=True)),
                ("longitude", models.FloatField(blank=True, null=True)),
                ("raw_response", models.JSONField(blank=True, default=dict)),
                ("error_message", models.TextField(blank=True)),
                (
                    "place",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="geocoding_logs",
                        to="places.place",
                    ),
                ),
                (
                    "triggered_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="geocoding_logs",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "Geocoding log",
                "verbose_name_plural": "Geocoding logs",
                "ordering": ["-created_at"],
            },
        ),
        migrations.CreateModel(
            name="ImportedPlaceRecord",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("external_id", models.CharField(max_length=120)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("pending", "Pending"),
                            ("imported", "Imported"),
                            ("skipped", "Skipped"),
                            ("failed", "Failed"),
                        ],
                        default="pending",
                        max_length=20,
                    ),
                ),
                ("checksum", models.CharField(blank=True, max_length=64)),
                ("raw_name", models.CharField(max_length=200)),
                ("raw_address", models.CharField(blank=True, max_length=255)),
                ("raw_payload", models.JSONField(blank=True, default=dict)),
                ("notes", models.TextField(blank=True)),
                ("imported_at", models.DateTimeField(blank=True, null=True)),
                (
                    "dataset",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="import_records",
                        to="ingestion.sourcedataset",
                    ),
                ),
                (
                    "imported_place",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="import_records",
                        to="places.place",
                    ),
                ),
                (
                    "source",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="import_records",
                        to="ingestion.source",
                    ),
                ),
            ],
            options={
                "verbose_name": "Imported place record",
                "verbose_name_plural": "Imported place records",
                "ordering": ["-created_at"],
            },
        ),
        migrations.AddConstraint(
            model_name="sourcedataset",
            constraint=models.UniqueConstraint(
                fields=("source", "name"),
                name="ingestion_dataset_unique_name",
            ),
        ),
        migrations.AddConstraint(
            model_name="importedplacerecord",
            constraint=models.UniqueConstraint(
                fields=("dataset", "external_id"),
                name="ingestion_import_record_unique_external_id",
            ),
        ),
    ]

