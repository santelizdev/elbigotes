# Operación y carga inicial

## Flujo de moderación y publicación

El flujo pensado para operar contenido real es:

1. registrar una `Source` y, si hace sentido, uno o más `SourceDataset`;
2. importar un CSV con `import_places_csv`;
3. revisar `ImportedPlaceRecord` para ver trazabilidad fila por fila;
4. ejecutar geocodificación para fichas sin coordenadas;
5. ejecutar auditoría de calidad y detección de duplicados;
6. moderar desde Django Admin usando:
   - `Place`
   - `PlaceQualityIssue`
   - `DuplicatePlaceCandidate`
   - `ImportedPlaceRecord`
   - `ClaimRequest`
7. publicar cambiando `status=active` y marcando `is_verified` cuando corresponda.

Este flujo evita publicar ciegamente datos crudos y deja un camino claro hacia perfiles reclamados.

## Comandos operativos

### 1. Importar lugares desde CSV

```bash
python src/manage.py import_places_csv data/examples/places_import_sample.csv \
  --source seed-manual \
  --dataset-slug directorio-inicial
```

Opciones útiles:

- `--dataset-name "Municipio de Santiago"`
- `--update-existing`
- `--dry-run`

### 2. Normalizar taxonomía

```bash
python src/manage.py normalize_place_categories
```

Sirve cuando llegan categorías libres desde distintas fuentes.

### 3. Geocodificar fichas sin coordenadas

```bash
python src/manage.py geocode_places --limit 100
```

La geocodificación también se puede encolar vía Celery con la tarea `apps.ingestion.tasks.geocode_place`.

### 4. Auditar calidad del dato

```bash
python src/manage.py audit_place_quality
```

Reglas mínimas actuales:

- falta de coordenadas;
- falta de contacto;
- ficha verificada sin contacto;
- servicio de emergencia sin flag 24/7;
- coordenadas fuera del rango esperado para Chile;
- ausencia de resumen editorial;
- ausencia de fuente.

### 5. Detectar duplicados básicos

```bash
python src/manage.py validate_place_duplicates
```

El detector usa nombre similar, comuna compartida y cercanía geográfica como señales iniciales.

### 6. Validar catálogo público antes de subir

```bash
python src/manage.py validate_public_catalog --fail-on-warning
```

Este comando revisa:

- taxonomía pública mínima cargada;
- lugares activos por categoría;
- registros importados fallidos o pendientes;
- datasets activos sin registros;
- lugares activos sin dirección pública o sin fuente.

## CSV esperado

Archivo de ejemplo: [places_import_sample.csv](/Users/delorean/elbigotes/data/examples/places_import_sample.csv)

Columnas soportadas:

- `external_id`
- `name`
- `summary`
- `description`
- `category`
- `subcategory`
- `status`
- `street_address`
- `formatted_address`
- `commune`
- `region`
- `country`
- `latitude`
- `longitude`
- `website`
- `phone`
- `email`
- `is_verified`
- `is_emergency_service`
- `is_open_24_7`
- `opening_hours`
- `source_url`
- `notes`

## Cómo pensar la moderación

- `ImportedPlaceRecord` conserva la fila original y el checksum del CSV.
- `SourceDataset` te permite separar lotes de carga por municipio, partner o scraping.
- `GeocodingLog` deja trazabilidad de qué se intentó geocodificar y con qué resultado.
- `PlaceQualityIssue` ordena la revisión por gravedad.
- `DuplicatePlaceCandidate` evita publicar la misma ficha varias veces cuando se mezclan fuentes.

## Preparación para perfiles reclamados y monetización

- `ClaimRequest` ya resuelve el flujo base para reclamar una ficha.
- `Place.is_featured` puede sostener destacados sin rediseñar el modelo.
- `Source`, datasets e import records permiten distinguir datos propios, partners y capturas externas.
