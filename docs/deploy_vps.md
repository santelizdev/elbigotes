# Deploy en VPS Linux con Nginx

Esta guía asume Ubuntu 24.04, Docker y un dominio apuntando al VPS.

## 1. Preparar el servidor

```bash
sudo apt update
sudo apt install -y ca-certificates curl git ufw
```

Instalar Docker siguiendo el repositorio oficial y habilitar:

```bash
sudo systemctl enable docker
sudo systemctl start docker
```

## 2. Clonar el proyecto

```bash
git clone <tu-repo> /srv/elbigotes
cd /srv/elbigotes
cp .env.example .env
```

## 3. Ajustar variables de entorno

Variables mínimas para producción:

- `DJANGO_SETTINGS_MODULE=config.settings.production`
- `DJANGO_SECRET_KEY=<secreto real>`
- `DJANGO_DEBUG=False`
- `DJANGO_ALLOWED_HOSTS=tu-dominio.com,www.tu-dominio.com`
- `DJANGO_CSRF_TRUSTED_ORIGINS=https://tu-dominio.com,https://www.tu-dominio.com`
- `CORS_ALLOWED_ORIGINS=https://tu-frontend.com,https://www.tu-dominio.com`
- `CORS_ALLOWED_ORIGIN_REGEXES=`
- `CORS_ALLOW_ALL_ORIGINS=False`
- `CORS_ALLOW_CREDENTIALS=False`
- `POSTGRES_DB`
- `POSTGRES_USER`
- `POSTGRES_PASSWORD`
- `POSTGRES_HOST=db`
- `POSTGRES_PORT=5432`
- `REDIS_URL`
- `CELERY_BROKER_URL`
- `CELERY_RESULT_BACKEND`
- `GEOCODING_PROVIDER`
- `GEOCODING_USER_AGENT`
- `API_THROTTLE_ANON=120/hour`
- `API_THROTTLE_USER=600/hour`

## 4. Construir y levantar

```bash
docker compose build
docker compose up -d
```

Luego crear superusuario y cargar seeds o CSV reales:

```bash
docker compose run --rm web python src/manage.py createsuperuser
docker compose run --rm web python src/manage.py seed_platform
docker compose run --rm web python src/manage.py import_places_csv data/examples/places_import_sample.csv --source seed-manual --dataset-slug inicio
docker compose run --rm web python src/manage.py validate_public_catalog --fail-on-warning
```

## 5. Configurar Nginx

El repositorio ya trae una configuración base en [default.conf](/Users/delorean/elbigotes/compose/nginx/default.conf). Si vas a usar Nginx del host en vez del contenedor:

1. publica `web` solo internamente;
2. configura upstream a Gunicorn en `127.0.0.1:8000`;
3. sirve `/static/` y `/media/` desde volúmenes persistentes;
4. agrega certificados TLS con Let's Encrypt.

## 6. SSL con Certbot

Si Nginx corre en el host:

```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d tu-dominio.com -d www.tu-dominio.com
```

## 7. Operación recurrente

- `docker compose logs -f web celery_worker celery_beat nginx`
- `docker compose exec web python src/manage.py audit_place_quality`
- `docker compose exec web python src/manage.py validate_place_duplicates`
- `docker compose exec web python src/manage.py geocode_places --limit 100`

## 8. Recomendaciones de monitoreo

- errores de aplicación: Sentry para Django, Celery y Next.js;
- métricas: Prometheus o al menos healthchecks de contenedores;
- logs estructurados: centralizar stdout con Loki o similar;
- jobs: alertar si Celery Beat o workers dejan de procesar colas;
- base de datos: monitorear crecimiento de `ImportedPlaceRecord`, `GeocodingLog` y `SourceSyncRun`.

## 9. Escalabilidad recomendada

- media storage externo: S3 o Cloudflare R2 para fotos y adjuntos;
- CDN: poner Cloudflare o CDN similar frente a frontend y assets;
- cache: Redis como cache de listados y búsquedas geográficas frecuentes;
- separación de servicios: frontend Next.js, backend Django, workers Celery y PostGIS en contenedores separados;
- búsqueda futura: considerar OpenSearch o PostgreSQL full-text avanzado cuando el volumen crezca.
