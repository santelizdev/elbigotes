import django.contrib.gis.db.models.fields
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("ingestion", "0001_initial"),
        ("taxonomy", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Place",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=200)),
                ("slug", models.SlugField(max_length=220, unique=True)),
                ("summary", models.CharField(blank=True, max_length=280)),
                ("description", models.TextField(blank=True)),
                (
                    "status",
                    models.CharField(
                        choices=[("draft", "Draft"), ("active", "Active"), ("archived", "Archived")],
                        default="draft",
                        max_length=20,
                    ),
                ),
                ("location", django.contrib.gis.db.models.fields.PointField(geography=True, srid=4326)),
                ("street_address", models.CharField(blank=True, max_length=255)),
                ("commune", models.CharField(blank=True, max_length=120)),
                ("region", models.CharField(blank=True, max_length=120)),
                ("country", models.CharField(default="Chile", max_length=120)),
                ("postal_code", models.CharField(blank=True, max_length=20)),
                ("formatted_address", models.CharField(blank=True, max_length=255)),
                ("website", models.URLField(blank=True)),
                ("metadata", models.JSONField(blank=True, default=dict)),
                ("is_verified", models.BooleanField(default=False)),
                ("is_featured", models.BooleanField(default=False)),
                ("is_emergency_service", models.BooleanField(default=False)),
                ("is_open_24_7", models.BooleanField(default=False)),
                (
                    "category",
                    models.ForeignKey(
                        on_delete=models.deletion.PROTECT,
                        related_name="places",
                        to="taxonomy.category",
                    ),
                ),
                (
                    "source",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=models.deletion.SET_NULL,
                        related_name="places",
                        to="ingestion.source",
                    ),
                ),
                (
                    "subcategory",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=models.deletion.PROTECT,
                        related_name="places",
                        to="taxonomy.subcategory",
                    ),
                ),
            ],
            options={
                "verbose_name": "Place",
                "verbose_name_plural": "Places",
                "ordering": ["-is_featured", "name"],
            },
        ),
        migrations.CreateModel(
            name="ContactPoint",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("label", models.CharField(max_length=80)),
                (
                    "kind",
                    models.CharField(
                        choices=[
                            ("phone", "Phone"),
                            ("whatsapp", "WhatsApp"),
                            ("email", "Email"),
                            ("website", "Website"),
                            ("instagram", "Instagram"),
                            ("facebook", "Facebook"),
                        ],
                        max_length=20,
                    ),
                ),
                ("value", models.CharField(max_length=255)),
                ("notes", models.CharField(blank=True, max_length=255)),
                ("is_primary", models.BooleanField(default=False)),
                ("sort_order", models.PositiveIntegerField(default=0)),
                (
                    "place",
                    models.ForeignKey(
                        on_delete=models.deletion.CASCADE,
                        related_name="contact_points",
                        to="places.place",
                    ),
                ),
            ],
            options={
                "verbose_name": "Contact point",
                "verbose_name_plural": "Contact points",
                "ordering": ["sort_order", "-is_primary", "kind"],
            },
        ),
        migrations.AddIndex(model_name="place", index=models.Index(fields=["status"], name="places_plac_status_33e508_idx")),
        migrations.AddIndex(model_name="place", index=models.Index(fields=["slug"], name="places_plac_slug_9f756d_idx")),
        migrations.AddIndex(
            model_name="place",
            index=models.Index(fields=["region", "commune"], name="places_plac_region_a0bca2_idx"),
        ),
    ]

