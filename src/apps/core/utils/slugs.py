from django.utils.text import slugify


def generate_unique_slug(instance, source_value: str, slug_field: str = "slug") -> str:
    """
    Genera slugs estables a nivel de modelo sin duplicar lógica en cada app.
    """

    slug = slugify(source_value)[:200]
    if not slug:
        slug = instance.__class__.__name__.lower()

    model_class = instance.__class__
    candidate = slug
    counter = 2

    while model_class._default_manager.filter(**{slug_field: candidate}).exclude(
        pk=instance.pk
    ).exists():
        candidate = f"{slug[:190]}-{counter}"
        counter += 1
    return candidate

