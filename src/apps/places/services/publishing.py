from apps.places.choices import PlaceStatus
from apps.places.models import Place


def get_publishable_places(*, include_address_only: bool = False):
    queryset = Place.objects.filter(status=PlaceStatus.DRAFT).exclude(category__isnull=True)

    if include_address_only:
        return queryset.exclude(formatted_address="").exclude(summary="")

    return queryset.filter(metadata__review_status="ready").exclude(location=None)


def publish_ready_places(*, include_address_only: bool = False) -> int:
    queryset = get_publishable_places(include_address_only=include_address_only)
    return queryset.update(status=PlaceStatus.ACTIVE)
