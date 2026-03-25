import os
from tempfile import NamedTemporaryFile

from django.contrib import admin, messages
from django.db import transaction
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.urls import path

from apps.ingestion.forms import ImportPetPlacesAdminForm
from apps.ingestion.models import (
    GeocodingLog,
    ImportedPlaceRecord,
    Source,
    SourceDataset,
    SourceSyncRun,
)
from apps.ingestion.services.importers import import_pet_places_from_csv


class SourceDatasetInline(admin.TabularInline):
    model = SourceDataset
    extra = 0
    fields = ("name", "slug", "default_region", "is_active")


@admin.register(Source)
class SourceAdmin(admin.ModelAdmin):
    list_display = ("name", "kind", "is_active", "reliability_score")
    list_filter = ("kind", "is_active")
    search_fields = ("name", "slug", "domain")
    prepopulated_fields = {"slug": ("name",)}
    inlines = [SourceDatasetInline]


@admin.register(SourceDataset)
class SourceDatasetAdmin(admin.ModelAdmin):
    list_display = ("name", "source", "default_region", "is_active")
    list_filter = ("source", "is_active")
    search_fields = ("name", "slug", "source__name")
    autocomplete_fields = ("source",)
    prepopulated_fields = {"slug": ("name",)}


@admin.register(SourceSyncRun)
class SourceSyncRunAdmin(admin.ModelAdmin):
    list_display = ("source", "status", "started_at", "finished_at", "items_seen", "items_created")
    list_filter = ("status", "source")
    search_fields = ("source__name", "error_message")
    autocomplete_fields = ("source",)
    readonly_fields = ("created_at", "updated_at")


@admin.register(ImportedPlaceRecord)
class ImportedPlaceRecordAdmin(admin.ModelAdmin):
    change_list_template = "admin/ingestion/importedplacerecord/change_list.html"
    list_display = ("external_id", "dataset", "status", "imported_place", "imported_at")
    list_filter = ("status", "dataset", "source")
    search_fields = ("external_id", "raw_name", "raw_address", "notes")
    autocomplete_fields = ("dataset", "source", "imported_place")
    readonly_fields = ("created_at", "updated_at", "imported_at")

    def get_urls(self):
        custom_urls = [
            path(
                "import-pet-places/",
                self.admin_site.admin_view(self.import_pet_places_view),
                name="ingestion_importedplacerecord_import_pet_places",
            )
        ]
        return custom_urls + super().get_urls()

    def import_pet_places_view(self, request: HttpRequest) -> HttpResponse:
        form = ImportPetPlacesAdminForm(request.POST or None, request.FILES or None)

        if request.method == "POST" and form.is_valid():
            temp_path = None
            try:
                uploaded_file = form.cleaned_data["csv_file"]
                with NamedTemporaryFile(delete=False, suffix=".csv") as temp_file:
                    for chunk in uploaded_file.chunks():
                        temp_file.write(chunk)
                    temp_path = temp_file.name

                with transaction.atomic():
                    summary = import_pet_places_from_csv(
                        temp_path,
                        dataset_name=form.cleaned_data.get("dataset_name"),
                        default_source=form.cleaned_data.get("default_source") or "manual_seed",
                        update_existing=form.cleaned_data["update_existing"],
                    )
                    if form.cleaned_data["dry_run"]:
                        transaction.set_rollback(True)

                level = messages.WARNING if form.cleaned_data["dry_run"] else messages.SUCCESS
                prefix = (
                    "Validación completada"
                    if form.cleaned_data["dry_run"]
                    else "Importación completada"
                )
                self.message_user(
                    request,
                    (
                        f"{prefix}: procesados={summary.processed}, creados={summary.created}, "
                        f"actualizados={summary.updated}, ignorados={summary.ignored}, "
                        f"errores={summary.failed}, pendientes_revision={summary.geocoding_needed}."
                    ),
                    level=level,
                )
                for error_message in summary.error_messages[:10]:
                    self.message_user(request, error_message, level=messages.ERROR)

                return redirect("admin:ingestion_importedplacerecord_changelist")
            except Exception as exc:  # noqa: BLE001
                form.add_error(None, str(exc))
            finally:
                if temp_path and os.path.exists(temp_path):
                    os.unlink(temp_path)

        context = {
            **self.admin_site.each_context(request),
            "opts": self.model._meta,
            "title": "Importar lugares para el mapa",
            "form": form,
        }
        return TemplateResponse(request, "admin/ingestion/import_pet_places.html", context)


@admin.register(GeocodingLog)
class GeocodingLogAdmin(admin.ModelAdmin):
    list_display = ("place", "provider", "status", "matched_address", "created_at")
    list_filter = ("provider", "status")
    search_fields = ("place__name", "query", "matched_address", "error_message")
    autocomplete_fields = ("place", "triggered_by")
    readonly_fields = ("created_at", "updated_at")
