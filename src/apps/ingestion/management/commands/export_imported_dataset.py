import os
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.core.serializers import serialize

from apps.ingestion.models import ImportedPlaceRecord, SourceDataset, Source


class Command(BaseCommand):
    help = "Exporta de forma segura un dataset local (Source, SourceDataset, ImportedPlaceRecord) a un JSON."

    def add_arguments(self, parser):
        parser.add_argument(
            "--dataset",
            required=True,
            help="Slug del SourceDataset a exportar.",
        )
        parser.add_argument(
            "--output",
            required=True,
            help="Ruta del archivo JSON de salida (ej. /app/tmp/mi-dataset.json).",
        )

    def handle(self, *args, **options):
        dataset_slug = options["dataset"]
        output_path = options["output"]

        try:
            dataset = SourceDataset.objects.get(slug=dataset_slug)
        except SourceDataset.DoesNotExist:
            raise CommandError(f"No se encontró el dataset con slug: {dataset_slug}")

        source = dataset.source
        records = ImportedPlaceRecord.objects.filter(dataset=dataset).order_by("created_at")
        
        total_records = records.count()
        self.stdout.write(f"Preparando exportación del dataset '{dataset_slug}'...")
        self.stdout.write(f"  Source: {source.slug}")
        self.stdout.write(f"  ImportedPlaceRecords: {total_records}")

        # Recopilar objetos a exportar en el orden correcto para satisfacer llaves foráneas
        objects_to_serialize = [source, dataset] + list(records)

        # Serializar
        json_data = serialize("json", objects_to_serialize, indent=2)

        # Crear el directorio si no existe
        out_file = Path(output_path)
        out_file.parent.mkdir(parents=True, exist_ok=True)

        # Escribir el archivo
        with open(out_file, "w", encoding="utf-8") as f:
            f.write(json_data)

        self.stdout.write(self.style.SUCCESS(f"¡Exportación exitosa! Archivo guardado en: {output_path}"))
