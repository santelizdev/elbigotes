# Elbigotes Backend

Backend base para una plataforma geoespacial del ecosistema pet en Chile, preparada para crecer a otros países. Esta primera iteración prioriza un dominio claro, filtros geográficos con PostGIS y una arquitectura que soporte moderación, ingestión de datos y futuros clientes como Next.js.

## Stack

- Django + Django REST Framework
- PostgreSQL + PostGIS
- Redis + Celery
- Docker + Nginx

## Principios de arquitectura

- `src/config`: configuración transversal del proyecto, settings por entorno y bootstrap de Celery.
- `src/apps/core`: piezas reutilizables del proyecto, healthcheck, utilidades comunes y comandos de management.
- `src/apps/taxonomy`: taxonomía pública del ecosistema pet para categorías y subcategorías.
- `src/apps/places`: directorio georreferenciado de lugares y servicios pet friendly.
- `src/apps/lost_pets`: reportes de mascotas perdidas con último punto conocido.
- `src/apps/claims`: flujo inicial para reclamos de propiedad o administración de fichas.
- `src/apps/accounts`: base para administración y moderación interna.
- `src/apps/ingestion`: metadatos de fuentes y tareas asíncronas de sincronización.

La documentación complementaria vive en [docs/architecture.md](/Users/delorean/elbigotes/docs/architecture.md), [docs/api.md](/Users/delorean/elbigotes/docs/api.md), [docs/operations.md](/Users/delorean/elbigotes/docs/operations.md) y [docs/deploy_vps.md](/Users/delorean/elbigotes/docs/deploy_vps.md).

## Cómo correr el proyecto con Docker

1. Crear el archivo `.env` a partir de `.env.example`.
2. Construir los contenedores:

```bash
make build
```

3. Levantar el stack:

```bash
make up
```

4. Crear datos semilla mínimos:

```bash
make seed
```

## Flujo local sin Docker

Este proyecto está pensado para correr preferentemente con Docker porque PostGIS y GDAL requieren librerías del sistema. Si quieres correrlo nativamente, usa Python 3.13, instala PostgreSQL con extensión PostGIS y luego:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements/dev.txt
export DJANGO_SETTINGS_MODULE=config.settings.local
python src/manage.py migrate
python src/manage.py runserver
```

## Comandos útiles

- `make migrate`
- `make makemigrations`
- `make seed`
- `make superuser`
- `make test`

## Siguientes pasos sugeridos

- autenticación y permisos por rol para dashboards internos;
- ingestión real desde fuentes municipales, refugios y veterinarias;
- ranking de confiabilidad y trazabilidad de cambios por ficha;
- endpoints públicos optimizados para el frontend Next.js;
- observabilidad con Sentry, métricas y auditoría de moderación.
