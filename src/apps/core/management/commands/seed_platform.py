from django.contrib.gis.geos import Point
from django.core.management.base import BaseCommand
from django.db import transaction

from apps.ingestion.models import Source, SourceKind
from apps.places.models import ContactPoint, ContactPointKind, Place, PlaceStatus
from apps.taxonomy.models import Category, Subcategory


class Command(BaseCommand):
    help = "Carga una taxonomía y un conjunto mínimo de lugares base para el MVP."

    @transaction.atomic
    def handle(self, *args, **options):
        source, _ = Source.objects.update_or_create(
            slug="seed-manual",
            defaults={
                "name": "Seed Manual",
                "kind": SourceKind.MANUAL,
                "domain": "",
                "reliability_score": 1.0,
            },
        )

        categories = {
            "mascotas-perdidas": {
                "name": "Mascotas perdidas",
                "subcategories": [("reportes", "Reportes públicos")],
            },
            "refugios-albergues": {
                "name": "Refugios y albergues",
                "subcategories": [("refugios", "Refugios"), ("rescate", "Rescate")],
            },
            "parques-pet-friendly": {
                "name": "Parques pet friendly",
                "subcategories": [("caniles", "Caniles"), ("plazas", "Plazas")],
            },
            "emergencias-veterinarias": {
                "name": "Emergencias veterinarias 24/7",
                "subcategories": [("urgencias", "Urgencias"), ("hospital", "Hospital veterinario")],
            },
            "veterinarias": {
                "name": "Veterinarias",
                "subcategories": [("consulta", "Consulta general"), ("especialidades", "Especialidades")],
            },
            "guarderias": {
                "name": "Guarderías",
                "subcategories": [("guarderia-diurna", "Guardería diurna"), ("hotel", "Hotel")],
            },
        }

        category_map = {}
        for slug, payload in categories.items():
            category, _ = Category.objects.update_or_create(
                slug=slug,
                defaults={
                    "name": payload["name"],
                    "description": f"Categoría base para {payload['name'].lower()}",
                    "is_active": True,
                    "sort_order": 10,
                },
            )
            category_map[slug] = category
            for child_slug, child_name in payload["subcategories"]:
                Subcategory.objects.update_or_create(
                    slug=child_slug,
                    defaults={
                        "category": category,
                        "name": child_name,
                        "description": f"Subcategoría base para {child_name.lower()}",
                        "is_active": True,
                        "sort_order": 10,
                    },
                )

        seed_places = [
            {
                "slug": "hospital-veterinario-santiago-centro",
                "name": "Hospital Veterinario Santiago Centro",
                "summary": "Urgencias veterinarias 24/7 con atención general.",
                "category_slug": "emergencias-veterinarias",
                "subcategory_slug": "hospital",
                "latitude": -33.4372,
                "longitude": -70.6506,
                "formatted_address": "Santiago Centro, Región Metropolitana, Chile",
                "commune": "Santiago",
                "region": "Región Metropolitana",
                "is_emergency_service": True,
                "is_open_24_7": True,
                "phone": "+56225550000",
            },
            {
                "slug": "parque-canino-providencia",
                "name": "Parque Canino Providencia",
                "summary": "Espacio pet friendly para paseo y recreación.",
                "category_slug": "parques-pet-friendly",
                "subcategory_slug": "caniles",
                "latitude": -33.4254,
                "longitude": -70.6113,
                "formatted_address": "Providencia, Región Metropolitana, Chile",
                "commune": "Providencia",
                "region": "Región Metropolitana",
                "is_emergency_service": False,
                "is_open_24_7": False,
                "phone": "",
            },
        ]

        for payload in seed_places:
            place, _ = Place.objects.update_or_create(
                slug=payload["slug"],
                defaults={
                    "name": payload["name"],
                    "summary": payload["summary"],
                    "category": category_map[payload["category_slug"]],
                    "subcategory": Subcategory.objects.get(slug=payload["subcategory_slug"]),
                    "status": PlaceStatus.ACTIVE,
                    "location": Point(payload["longitude"], payload["latitude"], srid=4326),
                    "formatted_address": payload["formatted_address"],
                    "commune": payload["commune"],
                    "region": payload["region"],
                    "country": "Chile",
                    "is_verified": True,
                    "is_emergency_service": payload["is_emergency_service"],
                    "is_open_24_7": payload["is_open_24_7"],
                    "source": source,
                },
            )
            if payload["phone"]:
                ContactPoint.objects.update_or_create(
                    place=place,
                    kind=ContactPointKind.PHONE,
                    value=payload["phone"],
                    defaults={"label": "Central", "is_primary": True},
                )

        self.stdout.write(self.style.SUCCESS("Datos semilla cargados correctamente."))

