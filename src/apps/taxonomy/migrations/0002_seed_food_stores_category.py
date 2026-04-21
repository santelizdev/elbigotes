from django.db import migrations


def seed_food_stores_category(apps, schema_editor):
    Category = apps.get_model("taxonomy", "Category")

    category, created = Category.objects.get_or_create(
        slug="tiendas-de-alimentos",
        defaults={
            "name": "Tiendas de alimentos",
            "description": "Locales de alimento, snacks y abastecimiento diario para mascotas.",
            "icon_name": "shopping-basket",
            "is_active": True,
            "sort_order": 1,
        },
    )

    if created:
        return

    category.name = "Tiendas de alimentos"
    category.description = category.description or "Locales de alimento, snacks y abastecimiento diario para mascotas."
    category.icon_name = category.icon_name or "shopping-basket"
    category.is_active = True
    category.save(update_fields=["name", "description", "icon_name", "is_active"])


def noop(apps, schema_editor):
    return


class Migration(migrations.Migration):

    dependencies = [
        ("taxonomy", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(seed_food_stores_category, noop),
    ]
