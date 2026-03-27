from apps.places.choices import PlaceStatus
from apps.places.models import Place


def get_publishable_places(
    *,
    include_address_only: bool = False,
    dataset_slug: str | None = None,
    ignore_review_status: bool = False,
):
    queryset = Place.objects.filter(status=PlaceStatus.DRAFT).exclude(category__isnull=True)

    if dataset_slug:
        queryset = queryset.filter(metadata__imported_from=dataset_slug)

    if include_address_only:
        queryset = queryset.exclude(formatted_address="")
    else:
        queryset = queryset.exclude(location=None)

    if not (ignore_review_status or include_address_only):
        queryset = queryset.filter(metadata__review_status="ready")

    return queryset


def publish_ready_places(
    *,
    include_address_only: bool = False,
    dataset_slug: str | None = None,
    ignore_review_status: bool = False,
) -> int:
    queryset = get_publishable_places(
        include_address_only=include_address_only,
        dataset_slug=dataset_slug,
        ignore_review_status=ignore_review_status,
    )
    return queryset.update(status=PlaceStatus.ACTIVE)
