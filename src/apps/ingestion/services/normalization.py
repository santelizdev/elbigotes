from django.utils.text import slugify

from apps.taxonomy.models import Category, Subcategory

CATEGORY_ALIAS_MAP = {
    "veterinaria": "veterinarias",
    "veterinarias": "veterinarias",
    "clinica veterinaria": "veterinarias",
    "clinicas veterinarias": "veterinarias",
    "refugio": "refugios-albergues",
    "refugios": "refugios-albergues",
    "albergue": "refugios-albergues",
    "parque": "parques-pet-friendly",
    "parques": "parques-pet-friendly",
    "parques pet friendly": "parques-pet-friendly",
    "emergencia veterinaria": "emergencias-veterinarias",
    "emergencias": "emergencias-veterinarias",
    "emergencias veterinarias 24/7": "emergencias-veterinarias",
    "guarderia": "guarderias",
    "guarderias": "guarderias",
    "guarderías": "guarderias",
}

SUBCATEGORY_ALIAS_MAP = {
    "urgencias": "urgencias",
    "hospital": "hospital",
    "rescate": "rescate",
    "refugio": "refugios",
    "canil": "caniles",
    "consulta": "consulta",
    "guarderia": "guarderia-diurna",
}


def normalize_category_slug(raw_value: str) -> str:
    slug = slugify(raw_value or "")
    return CATEGORY_ALIAS_MAP.get(slug, slug)


def normalize_subcategory_slug(raw_value: str) -> str:
    slug = slugify(raw_value or "")
    return SUBCATEGORY_ALIAS_MAP.get(slug, slug)


def resolve_category_pair(raw_category: str, raw_subcategory: str):
    """
    Convierte etiquetas libres del CSV a la taxonomía existente.
    Fallar temprano acá evita crear fichas inconsistentes difíciles de moderar después.
    """

    category_slug = normalize_category_slug(raw_category)
    subcategory_slug = normalize_subcategory_slug(raw_subcategory)

    category = Category.objects.filter(slug=category_slug).first()
    if not category:
        raise ValueError(f"No existe una categoría válida para '{raw_category}'.")

    subcategory = None
    if subcategory_slug:
        subcategory = Subcategory.objects.filter(slug=subcategory_slug, category=category).first()
        if not subcategory:
            raise ValueError(
                "No existe una subcategoría válida para "
                f"'{raw_subcategory}' dentro de '{category.slug}'."
            )

    return category, subcategory


PET_MAP_CATEGORY_ALIAS_MAP = {
    "veterinarias": "veterinarias",
    "veterinaria": "veterinarias",
    "refugios": "refugios-albergues",
    "refugio": "refugios-albergues",
    "parques": "parques-pet-friendly",
    "parque": "parques-pet-friendly",
    "emergencias": "emergencias-veterinarias",
    "emergencia": "emergencias-veterinarias",
    "guarderias": "guarderias",
    "guarderia": "guarderias",
}


def normalize_pet_map_category(raw_value: str) -> str:
    slug = slugify(raw_value or "")
    return PET_MAP_CATEGORY_ALIAS_MAP.get(slug, "")


def resolve_pet_map_category(raw_value: str) -> Category:
    """
    Resuelve la categoría estricta del CSV del mapa público.
    El importador solo acepta las cinco categorías definidas por producto.
    """

    category_slug = normalize_pet_map_category(raw_value)
    if not category_slug:
        raise ValueError(
            "La categoría debe ser una de: veterinarias, refugios, "
            "parques, emergencias, guarderias."
        )

    category = Category.objects.filter(slug=category_slug).first()
    if not category:
        raise ValueError(
            "La taxonomía no contiene la categoría requerida "
            f"'{category_slug}'. Ejecuta el seed inicial."
        )

    return category
