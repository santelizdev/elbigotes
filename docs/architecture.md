# Arquitectura base

## Objetivo

Esta base se diseñó para resolver dos necesidades que conviven desde el inicio:

1. publicar fichas georreferenciadas consultables por mapa;
2. moderar y enriquecer datos desde múltiples fuentes con trazabilidad.

## Decisiones importantes

### `Place` como agregado principal

`Place` concentra la información pública consultable por mapa. Se relaciona con:

- `Category` y `Subcategory` para taxonomía navegable;
- `ContactPoint` para no mezclar muchos campos de contacto rígidos en la tabla principal;
- `Source` para conservar procedencia y abrir la puerta a sincronizaciones futuras;
- `ClaimRequest` para moderar solicitudes de propiedad o administración.

Esta separación evita que `Place` se vuelva un modelo monolítico difícil de evolucionar.

### PostGIS desde el inicio

Los filtros por cercanía y futuras búsquedas por bounding box requieren capacidades geoespaciales reales. Por eso:

- la base usa `django.contrib.gis.db.backends.postgis`;
- los puntos públicos usan `PointField(geography=True)` en SRID 4326;
- los listados pueden anotar distancia y filtrar por radio.

### Apps pequeñas y con responsabilidades claras

Cada app expone solo lo que le corresponde:

- `models.py` para el estado persistente;
- `admin.py` para moderación;
- `api/serializers.py` y `api/views.py` para la capa HTTP;
- `filters.py`, `selectors.py` o `services.py` cuando la lógica deja de ser trivial.

Esto hace más simple mover parte del dominio a servicios internos o nuevos módulos sin reescribir toda la API.

### Settings por entorno

`config/settings/base.py` contiene lo compartido.

- `local.py` habilita desarrollo y CORS relajado.
- `production.py` endurece cookies, proxy SSL y seguridad.
- `test.py` elimina complejidad innecesaria para la suite automatizada.

El proyecto se selecciona con `DJANGO_SETTINGS_MODULE`.

### Celery listo aunque el MVP sea pequeño

La app `ingestion` ya incluye tareas ejemplo porque:

- las sincronizaciones futuras no deben bloquear requests;
- la normalización y deduplicación de fuentes externas será costosa;
- notificaciones, reindexaciones y auditorías también son candidatas a trabajo asíncrono.

## Escalabilidad futura

- multi país: `country` ya vive en `Place` y la taxonomía puede internacionalizarse;
- filtros más complejos: se puede sumar `PolygonField` o caché geoespacial sin rehacer el modelo base;
- frontend independiente: la API ya nace desacoplada del panel admin;
- moderación: `ClaimRequest` y los flags de verificación dejan un camino claro hacia workflows internos.

