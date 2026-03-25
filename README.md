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
- **Contenedores**: Docker + Docker Compose + Nginx
- **Frontend** (próximamente): Next.js 15 (App Router) + TypeScript + Leaflet

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