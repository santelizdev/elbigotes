# El Bigotes

**Plataforma geoespacial para el ecosistema pet en Chile**

El Bigotes es un directorio inteligente y comunidad en tiempo real para dueños de mascotas. Conecta a las personas con **lugares pet-friendly**, reporta **mascotas perdidas**, encuentra refugios, veterinarias, guarderías y más, todo con potentes filtros geográficos.

Este repositorio contiene el **backend** (Django), preparado para escalar a otros países de Latam.

![Python](https://img.shields.io/badge/Python-3.13-blue.svg)
![Django](https://img.shields.io/badge/Django-5.x-green.svg)
![PostGIS](https://img.shields.io/badge/PostGIS-enabled-orange.svg)
![Docker](https://img.shields.io/badge/Docker-ready-blue.svg)

## Características principales

- **Búsqueda geoespacial potente** con PostGIS (radio, bounding box, etc.)
- Directorio de **lugares pet-friendly** (veterinarias, parques, guarderías, hoteles, etc.)
- Sistema de **reportes de mascotas perdidas** con última ubicación conocida
- Motor de **ingestión asíncrona** de datos (CSV, APIs externas, geocodeo)
- Arquitectura modular y escalable (`apps/` separadas por dominio)
- Preparado para frontend en **Next.js** (endpoints REST listos)
- Soporte completo para moderación y calidad de datos

## Stack Tecnológico

- **Backend**: Django 5 + Django REST Framework
- **Base de datos**: PostgreSQL + PostGIS
- **Tareas asíncronas**: Celery + Redis
- **Contenedores**: Docker + Docker Compose
- **Frontend**: Next.js 15 (App Router) + TypeScript + Leaflet

## Estructura del proyecto

```bash
src/apps/
├── core/           # Utilidades, healthcheck, comandos base
├── taxonomy/       # Categorías y subcategorías del ecosistema pet
├── places/         # Lugares y servicios pet-friendly
├── lost_pets/      # Reportes de mascotas perdidas
├── ingestion/      # Importación y sincronización de datos
├── accounts/       # Usuarios, perfiles y permisos
├── claims/         # Reclamos y moderación
└── config/         # Settings por entorno y Celery

## Despliegue Recomendado

La arquitectura recomendada a partir de este punto es:

- `frontend` (Next.js) publica la app web.
- `web` (Django) publica API, admin, `static` y `media`.
- Hestia es el unico reverse proxy publico en VPS.

### Local con Docker

- `frontend` queda publicado en `http://localhost:13000`
- `web` queda publicado en `http://localhost:18000`
- El navegador llama la API directo a `http://localhost:18000/api/v1`
- El SSR de Next llama internamente a `http://web:8000/api/v1`

Variables clave del `.env` local:

```env
NEXT_PUBLIC_SITE_URL=http://localhost:13000
NEXT_PUBLIC_API_BASE_URL=http://localhost:18000/api/v1
INTERNAL_API_BASE_URL=http://web:8000/api/v1
```

### VPS con Hestia

- Hestia termina SSL y hace reverse proxy.
- `frontend` debe exponerse solo a loopback, por ejemplo `127.0.0.1:13000`
- `web` debe exponerse solo a loopback, por ejemplo `127.0.0.1:18000`
- Hestia debe enrutar:
  - `/` -> `127.0.0.1:13000`
  - `/api`, `/admin`, `/static`, `/media` -> `127.0.0.1:18000`

Variables clave del `.env` en VPS:

```env
NEXT_PUBLIC_SITE_URL=https://www.elbigotes.cl
NEXT_PUBLIC_API_BASE_URL=/api/v1
INTERNAL_API_BASE_URL=http://web:8000/api/v1
DJANGO_ALLOWED_HOSTS=www.elbigotes.cl,elbigotes.cl,127.0.0.1,localhost,web
```

### Diferencia importante entre local y VPS

La unica diferencia deliberada es la URL que usa el navegador:

- En local el navegador consume Django directo por puerto (`http://localhost:18000`)
- En VPS el navegador consume la API por el mismo dominio publico (`/api/v1`) a traves de Hestia

El SSR de Next se mantiene estable en ambos casos usando `INTERNAL_API_BASE_URL=http://web:8000/api/v1`.
