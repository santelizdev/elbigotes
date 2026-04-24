import logging
from datetime import timedelta

from celery import shared_task
from django.utils import timezone

from apps.ingestion.models import Source, SourceSyncRun, SyncRunStatus
from apps.ingestion.services.geocoding import geocode_place_instance
from apps.places.models import Place
from apps.places.services.duplicates import rebuild_duplicate_candidates
from apps.places.services.quality import audit_places, audit_single_place

logger = logging.getLogger(__name__)


@shared_task
def sync_active_sources() -> int:
    """
    Tarea base que deja resuelto el esqueleto para futuras sincronizaciones reales.
    Hoy registra ejecuciones mínimas por fuente para validar scheduler y observabilidad.
    """

    synced = 0
    for source in Source.objects.filter(is_active=True):
        run = SourceSyncRun.objects.create(
            source=source,
            status=SyncRunStatus.RUNNING,
            started_at=timezone.now(),
        )
        run.status = SyncRunStatus.SUCCEEDED
        run.finished_at = timezone.now()
        run.stats = {"message": "Base ingestion heartbeat"}
        run.save(update_fields=["status", "finished_at", "stats", "updated_at"])
        synced += 1
        logger.info("Source %s marked as synced", source.slug)
    return synced


@shared_task
def geocode_place(place_id: int) -> int:
    place = Place.objects.get(pk=place_id)
    geocode_place_instance(place)
    return place_id


@shared_task
def audit_places_consistency(place_id: int | None = None) -> int:
    if place_id is not None:
        place = Place.objects.get(pk=place_id)
        audit_single_place(place)
        return 1
    return audit_places()


@shared_task
def rebuild_place_duplicates() -> int:
    return rebuild_duplicate_candidates()


@shared_task
def cleanup_old_sync_runs(days: int = 30) -> int:
    threshold = timezone.now() - timedelta(days=days)
    deleted, _ = SourceSyncRun.objects.filter(created_at__lt=threshold).delete()
    return deleted
