from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("taxonomy", "0002_seed_food_stores_category"),
        ("places", "0008_featured_catalog_items"),
    ]

    operations = [
        migrations.CreateModel(
            name="PublicPetOperation",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("title", models.CharField(max_length=200)),
                ("slug", models.SlugField(max_length=220, unique=True)),
                (
                    "operation_type",
                    models.CharField(
                        choices=[
                            ("vaccination", "Vaccination"),
                            ("sterilization", "Sterilization"),
                            ("microchip", "Microchip"),
                            ("adoption", "Adoption"),
                            ("other", "Other"),
                        ],
                        max_length=20,
                    ),
                ),
                ("address", models.CharField(max_length=255)),
                ("commune", models.CharField(max_length=120)),
                ("region", models.CharField(blank=True, max_length=120)),
                ("latitude", models.FloatField(blank=True, null=True)),
                ("longitude", models.FloatField(blank=True, null=True)),
                ("starts_at", models.DateTimeField()),
                ("ends_at", models.DateTimeField(blank=True, null=True)),
                ("requirements", models.TextField(blank=True)),
                ("quota", models.CharField(blank=True, max_length=120)),
                ("price_label", models.CharField(blank=True, max_length=120)),
                ("registration_url", models.URLField(blank=True)),
                ("source_url", models.URLField()),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("draft", "Draft"),
                            ("published", "Published"),
                            ("expired", "Expired"),
                        ],
                        default="draft",
                        max_length=20,
                    ),
                ),
                (
                    "category",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=models.deletion.PROTECT,
                        related_name="public_pet_operations",
                        to="taxonomy.category",
                    ),
                ),
                (
                    "place",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=models.deletion.SET_NULL,
                        related_name="public_pet_operations",
                        to="places.place",
                    ),
                ),
            ],
            options={
                "verbose_name": "Public pet operation",
                "verbose_name_plural": "Public pet operations",
                "ordering": ["starts_at", "title"],
                "indexes": [
                    models.Index(fields=["slug"], name="places_publ_slug_098f67_idx"),
                    models.Index(fields=["status", "starts_at"], name="places_publ_status__ec73ee_idx"),
                    models.Index(fields=["operation_type", "commune"], name="places_publ_operati_651f44_idx"),
                ],
            },
        ),
    ]
