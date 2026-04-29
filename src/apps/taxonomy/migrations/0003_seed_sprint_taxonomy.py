from django.db import migrations


def seed_sprint_taxonomy(apps, schema_editor):
    Category = apps.get_model("taxonomy", "Category")
    Subcategory = apps.get_model("taxonomy", "Subcategory")

    # 1. Sembrar Peluquerías caninas
    peluqueria_cat, _ = Category.objects.get_or_create(
        slug="peluquerias-caninas",
        defaults={
            "name": "Peluquerías caninas",
            "description": "Estética, baño, grooming y peluquería para mascotas.",
            "icon_name": "scissors",
            "is_active": True,
            "sort_order": 2,
        },
    )

    Subcategory.objects.get_or_create(
        category=peluqueria_cat,
        slug="peluquerias-caninas-grooming",
        defaults={"name": "Grooming", "is_active": True, "sort_order": 1},
    )
    Subcategory.objects.get_or_create(
        category=peluqueria_cat,
        slug="peluquerias-caninas-bano-y-corte",
        defaults={"name": "Baño y corte", "is_active": True, "sort_order": 2},
    )

    # 2. Sembrar subcategorías de Tiendas de alimentos
    # La categoría ya existe por 0002_seed_food_stores_category
    tiendas_cat = Category.objects.filter(slug="tiendas-de-alimentos").first()
    if tiendas_cat:
        Subcategory.objects.get_or_create(
            category=tiendas_cat,
            slug="tiendas-de-alimentos-pet-shop",
            defaults={"name": "Pet Shop", "is_active": True, "sort_order": 1},
        )
        Subcategory.objects.get_or_create(
            category=tiendas_cat,
            slug="tiendas-de-alimentos-alimentos",
            defaults={"name": "Alimentos", "is_active": True, "sort_order": 2},
        )
        Subcategory.objects.get_or_create(
            category=tiendas_cat,
            slug="tiendas-de-alimentos-accesorios",
            defaults={"name": "Accesorios", "is_active": True, "sort_order": 3},
        )


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("taxonomy", "0002_seed_food_stores_category"),
    ]

    operations = [
        migrations.RunPython(seed_sprint_taxonomy, noop),
    ]
