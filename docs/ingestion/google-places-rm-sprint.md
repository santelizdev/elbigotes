# Sprint Google Places: RM (Región Metropolitana)

Este documento describe el flujo de ingesta diseñado para priorizar **Clínicas y Tiendas 24/7** de alto impacto, manteniendo los costos bajos y garantizando la calidad de los datos para no generar falsos positivos (falsos 24/7 sin respaldo en Google).

## Principios del Flujo

1. **Nearby Search (Sin Details) es un Discovery**: Se corre de forma muy económica ($0.032 por cada 60 lugares). Extrae nombres, coordenadas e identifica la categoría general. *No valida si el lugar es 24/7*.
2. **Enriquecimiento Selectivo (Details)**: Solo para candidatos a ser 24/7 o lugares de alto impacto, hacemos una consulta específica de "Place Details" ($0.017 por consulta). Esto trae los horarios reales (`opening_hours`).
3. **Promoción de Staging a Producción**: El comando `promote_places` transforma la data de `ImportedPlaceRecord` a `Place`. Por seguridad estricta, ningún lugar será clasificado como `is_open_24_7 = True` si no tiene horarios reales (`opening_hours_raw`).

## Pasos para la Ingesta RM 

### 1. Aplicar Migraciones
Asegurar que la taxonomía (Tiendas y Peluquerías) existe.
```bash
docker compose exec web python /app/src/manage.py migrate
```

### 2. Descubrimiento Barato (Sin Details)
Barreremos las comunas más pobladas de la RM extrayendo las categorías clave.
```bash
docker compose exec web bash -lc 'python /app/scripts/ingest_google_places.py \
  --api-key "$GOOGLE_MAPS_API_KEY" \
  --dataset rm-sprint1-v1 \
  --categories veterinaria emergencia-veterinaria tiendas peluqueria-canina \
  --rm-top-communes \
  --max-records 1500 \
  --max-requests 300'
```

### 3. Enriquecimiento Selectivo
Encontrar en la base de datos (staging) los registros que sugieren ser urgencias o tiendas 24 horas y enriquecerlos con horarios completos de Google.
```bash
docker compose exec web python /app/src/manage.py enrich_google_place_details \
  --dataset rm-sprint1-v1 \
  --limit 300 \
  --max-requests 300
```
> **Nota**: Recomendamos un primer lote de 100–300 lugares de alto valor en vez de 1500 lugares incompletos.

### 4. Revisión (Dry Run)
Ver qué se va a insertar antes de tocar la tabla `Place` oficial.
```bash
docker compose exec web python /app/src/manage.py promote_places \
  --dataset rm-sprint1-v1 \
  --dry-run \
  --limit 100
```

### 5. Promoción Oficial
Pasar los datos de Staging a Producción.
```bash
docker compose exec web python /app/src/manage.py promote_places \
  --dataset rm-sprint1-v1
```

### 6. Revisión en el Admin
Las clínicas que dicen ser urgencia pero no trajeron horarios quedan guardadas como `DRAFT` y con el flag `needs_hours_review`. No serán expuestas en el mapa público como locales activos hasta revisión manual o re-enriquecimiento.

## Estrategia por Categoría

* `tiendas`: lista para producción con discovery barato + promote.
* `emergencia-veterinaria`: requiere Details selectivo para validar horarios.
* `peluqueria-canina`: requiere queries más específicas y validación separada.
* No mezclar categorías en un mismo test cuando se está midiendo calidad.

## Reutilizar data local en producción sin volver a consultar Google API

Es posible exportar los registros de staging (`Source`, `SourceDataset`, `ImportedPlaceRecord`) de un entorno local e importarlos en producción, ahorrando peticiones a la API.

### Opción 1: Exportar Dataset Específico (Recomendado)
Usa el script custom para exportar solo el dataset que necesitas:
```bash
docker compose exec web python /app/src/manage.py export_imported_dataset \
  --dataset rm-santiago-tiendas-v1 \
  --output /app/tmp/rm-santiago-tiendas-v1.json
```

### Opción 2: Usar dumpdata (Alternativa Manual)
Si exportas usando las herramientas nativas, cuida no exportar registros de otros tests:
```bash
docker compose exec web python /app/src/manage.py dumpdata ingestion.Source ingestion.SourceDataset ingestion.ImportedPlaceRecord \
  --indent 2 \
  --output /app/tmp/rm-santiago-tiendas-v1.json
```

### Importar en Producción
Una vez que el archivo esté en tu servidor VPS de producción, simplemente impórtalo:
```bash
docker compose exec web python /app/src/manage.py loaddata /app/tmp/rm-santiago-tiendas-v1.json
```
