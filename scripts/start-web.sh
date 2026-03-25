#!/bin/sh
set -eu

python src/manage.py wait_for_db
python src/manage.py migrate --noinput
python src/manage.py collectstatic --noinput
exec gunicorn config.wsgi:application \
  --chdir /app/src \
  --bind 0.0.0.0:${APP_PORT:-8000} \
  --workers ${GUNICORN_WORKERS:-3}

