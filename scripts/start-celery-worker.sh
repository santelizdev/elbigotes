#!/bin/sh
set -eu

python src/manage.py wait_for_db
exec celery -A config --workdir /app/src worker -l info
