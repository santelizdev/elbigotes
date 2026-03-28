# Google Places Import Runbook

Este documento deja el flujo operativo para:

- importar datos desde Google Places API a `ImportedPlaceRecord`
- promoverlos a `Place`
- publicarlos en lote
- mover la misma data al VPS sin volver a gastar cuota de Google

## 1. Requisitos

- `GOOGLE_MAPS_API_KEY` presente en `.env`
- contenedor `web` levantado
- taxonomía cargada

Comprobación rápida:

```bash
docker compose exec web bash -lc 'echo "$GOOGLE_MAPS_API_KEY" | wc -c'
```

Si devuelve más que `1`, la key está disponible dentro del contenedor.

## 2. Ingesta desde Google Places

Importante:

- ejecuta la expansión de la API key dentro del contenedor con `bash -lc`
- `--dry-run` evita guardar, pero igual consume cuota

Ejemplo:

```bash
docker compose exec web bash -lc 'python /app/scripts/ingest_google_places.py \
  --api-key "$GOOGLE_MAPS_API_KEY" \
  --dataset rm-parques-v1 \
  --categories parque \
  --only-communes santiago valparaiso la-serena concepcion'
```

Otro ejemplo:

```bash
docker compose exec web bash -lc 'python /app/scripts/ingest_google_places.py \
  --api-key "$GOOGLE_MAPS_API_KEY" \
  --dataset rm-emergencias-v1 \
  --categories emergencia-veterinaria \
  --only-communes santiago valparaiso la-serena concepcion'
```

## 3. Promoción a `Place`

Primero revisar una muestra:

```bash
docker compose exec web python /app/src/manage.py promote_places \
  --dataset rm-parques-v1 \
  --dry-run \
  --limit 50
```

Si la muestra se ve bien:

```bash
docker compose exec web python /app/src/manage.py promote_places \
  --dataset rm-parques-v1
```

Y para emergencias:

```bash
docker compose exec web python /app/src/manage.py promote_places \
  --dataset rm-emergencias-v1
```

Notas:

- los `Place` promovidos quedan en `draft`
- el comando filtra parte del ruido de Google por heurísticas de categoría

## 4. Publicación en lote

Primero validar:

```bash
docker compose exec web python /app/src/manage.py publish_ready_places \
  --dataset rm-parques-v1 \
  --ignore-review-status \
  --dry-run
```

Luego publicar:

```bash
docker compose exec web python /app/src/manage.py publish_ready_places \
  --dataset rm-parques-v1 \
  --ignore-review-status
```

Para emergencias:

```bash
docker compose exec web python /app/src/manage.py publish_ready_places \
  --dataset rm-emergencias-v1 \
  --ignore-review-status
```

## 5. Verificación local

Conteo por categoría activa:

```bash
docker compose exec web python /app/src/manage.py shell -c "from apps.places.models import Place; from django.db.models import Count; print(list(Place.objects.filter(status='active').values('category__slug').annotate(c=Count('id')).order_by('category__slug')))"
```

## 6. Deploy de código

Primero subir código:

```bash
git push origin main
```

En el VPS:

```bash
cd ~/apps/elbigotes
git pull origin main
docker compose up -d --build web frontend
```

## 7. Pasar la misma data al VPS sin volver a gastar Google

`git push` no mueve la base de datos. Si no quieres volver a consumir cuota, debes mover la data.

La ruta más rápida es restaurar la base local sobre el VPS.

### 7.1 Respaldar local

```bash
docker compose exec -T db sh -lc 'pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" -Fc' > /tmp/elbigotes_local_places.dump
```

### 7.2 Copiar dump al VPS

```bash
cat /tmp/elbigotes_local_places.dump | ssh deploy@TU_IP_O_HOST 'cat > /tmp/elbigotes_local_places.dump'
```

### 7.3 Respaldar la base actual del VPS

```bash
cd ~/apps/elbigotes
docker compose exec -T db sh -lc 'pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" -Fc' > /tmp/elbigotes_prod_backup.dump
```

### 7.4 Restaurar la base local en el VPS

```bash
cat /tmp/elbigotes_local_places.dump | docker compose exec -T db sh -lc 'pg_restore \
  --clean \
  --if-exists \
  --no-owner \
  -U "$POSTGRES_USER" \
  -d "$POSTGRES_DB"'
```

### 7.5 Aplicar migraciones y validar

```bash
docker compose up -d
docker compose exec web python /app/src/manage.py migrate --noinput
docker compose exec web python /app/src/manage.py shell -c "from apps.places.models import Place; from django.db.models import Count; print(list(Place.objects.filter(status='active').values('category__slug').annotate(c=Count('id')).order_by('category__slug')))"
```

## 8. Advertencia importante

La restauración completa reemplaza la base actual del VPS por la local.

Hazlo solo si:

- el VPS todavía no tiene data de negocio que quieras conservar
- o ya hiciste backup y aceptas sobrescribirla

Si necesitas mezclar la data nueva con una base productiva ya viva, no uses restore completo: prepara un export/import selectivo.

## 9. Checklist corto de cierre

1. Ingesta OK
2. `promote_places --dry-run` revisado
3. `promote_places` ejecutado
4. `publish_ready_places --dry-run` revisado
5. `publish_ready_places` ejecutado
6. Conteos activos validados
7. Código pusheado
8. Backup local y backup VPS hechos
9. Restore en VPS completado
10. Home y categorías revisadas manualmente

## 10. Operativa segura de Docker

Para evitar apagar el stack por error:

- usa `docker compose up -d` para levantar
- usa `docker compose up -d --build web` para backend
- usa `docker compose up -d --build frontend` para frontend
- evita `docker compose down` salvo mantenimiento planificado

Atajos del repo:

```bash
make up-detached
make restart-web
make restart-frontend
make status
make logs-app
```
