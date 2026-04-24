# Editorial Catalog & Public Pet Operations

## Scope
Este sprint dejó resueltos dos módulos editoriales/manuales para el backoffice:

- catálogo reutilizable de productos, servicios y promociones destacadas por `Place`,
- operativos públicos/municipales orientados a mascotas con vigencia automática.

La meta fue sumar contenido administrable desde Django Admin sin duplicar registros y sin mezclar esta lógica con la ingesta automática de Google Places.

## Models Created
### Featured Catalog
- `FeaturedCatalogItem`: item editorial reutilizable con `title`, `slug`, `description`, `item_type`, `category`, imagen opcional, labels opcionales de precio/CTA, activación y timestamps.
- `PlaceFeaturedCatalogItem`: tabla puente entre `Place` y `FeaturedCatalogItem` con overrides por ficha (`custom_price_label`, `custom_cta_url`), activación, orden y unicidad por par `place + featured_item`.

### Public Operations
- `PublicPetOperation`: operativo público con `title`, `slug`, `operation_type`, `creator_type`, `creator_name`, `address`, `commune`, `region`, `latitude`, `longitude`, `starts_at`, `ends_at`, `requirements`, `image`, `status` y timestamps.

## Admin Flow
### Featured Catalog
- El equipo editorial crea `FeaturedCatalogItem` desde admin.
- Luego puede asociarlo a varios `Place` sin duplicar el item base.
- `PlaceAdmin` muestra un inline para administrar el vínculo, el orden y los overrides visibles en API.

### Public Operations
- `PublicPetOperation` se crea manualmente desde admin con `slug` prepopulado, filtros por tipo/estado/comuna y selector dependiente `región -> comuna`.
- La dirección usa Google Places Autocomplete para confirmar la opción correcta antes de guardar.
- `latitude` y `longitude` se completan automáticamente y quedan visibles solo como referencia editorial.
- El editor valida la dirección final sobre un preview dinámico de Google Maps antes de publicar.
- Los operativos vencidos se conservan en la base para trazabilidad; no se borran automáticamente.
- Requiere `GOOGLE_MAPS_API_KEY` disponible en entorno para habilitar el autocompletado editorial.

## Public API
### Place Detail
- `GET /api/v1/places/{slug}/`
- Expone `featured_items` activos ordenados por `sort_order`.
- `price_label` final prioriza el override del vínculo.
- `cta_url` final viene desde `custom_cta_url`.

### Public Operations
- `GET /api/v1/places/public-operations/`
- `GET /api/v1/places/public-operations/{slug}/`

Filtros disponibles:

- `operation_type`
- `commune`
- `status`
- `upcoming=true`
- `include_expired=true`

Comportamiento por defecto:

- solo devuelve operativos `published` y todavía vigentes,
- no expone vencidos ni drafts en el catálogo público,
- si se usa `include_expired=true`, pueden consultarse operativos históricos no draft.

## Visibility & Expiration Rules
- Un operativo es públicamente visible solo cuando `status = published` y sigue vigente.
- Si `ends_at` existe, sigue vigente mientras `ends_at >= now`.
- Si `ends_at` es `null`, sigue vigente mientras `starts_at >= now`.
- La evaluación usa datetimes timezone-aware bajo el contexto Chile (`America/Santiago`).

Se agregaron propiedades:

- `is_expired`
- `is_publicly_visible`

## Automatic Expiration
Se agregó el command:

- `python src/manage.py expire_public_pet_operations`

El command busca operativos `published` vencidos y los cambia a `expired`.
También se dejó una tarea Celery programada diariamente para ejecutar esta expiración de forma automática usando la infraestructura existente del proyecto.

## Design Decisions
- `FeaturedCatalogItem` vive separado de `Place` para permitir reutilización real entre múltiples fichas.
- La relación `PlaceFeaturedCatalogItem` concentra overrides específicos por sucursal o ficha pública.
- `PublicPetOperation` quedó en `apps.places` porque comparte taxonomía, geografía editorial y exposición pública con el directorio.
- `PublicPetOperation` ya no depende de `Category` ni de `Place`, porque el módulo representa por sí mismo una capa editorial distinta del directorio base.
- `latitude` y `longitude` se conservan en la base para poder mostrar el operativo sobre el mapa público sin geocodificar en runtime.
- Las coordenadas no se capturan manualmente: se derivan desde Google Places Autocomplete cuando el editor confirma la dirección.
- El frontend expone la sección como una entrada propia en `Categorías` bajo el texto `Jornadas/Operativos`.

## Limitations
- El endpoint público no tiene autenticación diferenciada para un modo interno; `include_expired=true` sirve para auditoría ligera pero no expone drafts.
- No existe todavía un flujo de ingestión automática de operativos desde municipios o datasets externos.
- La expiración automática conserva el registro y solo cambia su visibilidad/estado; no elimina archivos ni genera archivado SEO todavía.
- No se implementó búsqueda geográfica ni clustering para operativos en esta versión.
- La lista de regiones y comunas del admin replica la misma base territorial usada en frontend y hoy se mantiene dentro del repositorio, no desde una fuente externa compartida.
