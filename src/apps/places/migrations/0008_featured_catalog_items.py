from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("taxonomy", "0002_seed_food_stores_category"),
        ("places", "0007_place_opening_hours"),
    ]

    operations = [
        migrations.CreateModel(
            name="FeaturedCatalogItem",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("title", models.CharField(max_length=200)),
                ("slug", models.SlugField(max_length=220, unique=True)),
                ("description", models.TextField(blank=True)),
                (
                    "item_type",
                    models.CharField(
                        choices=[("product", "Product"), ("service", "Service"), ("promo", "Promo")],
                        max_length=20,
                    ),
                ),
                ("image", models.ImageField(blank=True, upload_to="places/featured-catalog/%Y/%m/")),
                ("price_label", models.CharField(blank=True, max_length=120)),
                ("cta_label", models.CharField(blank=True, max_length=120)),
                ("is_active", models.BooleanField(default=True)),
                (
                    "category",
                    models.ForeignKey(
                        on_delete=models.deletion.PROTECT,
                        related_name="featured_catalog_items",
                        to="taxonomy.category",
                    ),
                ),
            ],
            options={
                "verbose_name": "Featured catalog item",
                "verbose_name_plural": "Featured catalog items",
                "ordering": ["title"],
            },
        ),
        migrations.CreateModel(
            name="PlaceFeaturedCatalogItem",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("custom_price_label", models.CharField(blank=True, max_length=120)),
                ("custom_cta_url", models.URLField(blank=True)),
                ("is_active", models.BooleanField(default=True)),
                ("sort_order", models.PositiveIntegerField(default=0)),
                (
                    "featured_item",
                    models.ForeignKey(
                        on_delete=models.deletion.CASCADE,
                        related_name="place_assignments",
                        to="places.featuredcatalogitem",
                    ),
                ),
                (
                    "place",
                    models.ForeignKey(
                        on_delete=models.deletion.CASCADE,
                        related_name="featured_catalog_assignments",
                        to="places.place",
                    ),
                ),
            ],
            options={
                "verbose_name": "Place featured catalog item",
                "verbose_name_plural": "Place featured catalog items",
                "ordering": ["sort_order", "id"],
            },
        ),
        migrations.AddConstraint(
            model_name="placefeaturedcatalogitem",
            constraint=models.UniqueConstraint(
                fields=("place", "featured_item"),
                name="places_featured_catalog_assignment_unique_pair",
            ),
        ),
    ]
