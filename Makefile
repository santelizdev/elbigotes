PROJECT_NAME=elbigotes

.PHONY: build up up-detached restart-web restart-frontend status down logs logs-app migrate makemigrations shell superuser seed test lint format validate_catalog

build:
	docker compose build

up:
	docker compose up --build

up-detached:
	docker compose up -d

restart-web:
	docker compose up -d --build web

restart-frontend:
	docker compose up -d --build frontend

status:
	docker compose ps

down:
	@echo "WARNING: 'docker compose down' detiene todo el stack. Usa 'make up-detached', 'make restart-web' o 'make restart-frontend' salvo mantencion planificada."
	docker compose down

logs:
	docker compose logs -f web celery_worker celery_beat

logs-app:
	docker compose logs -f web frontend

migrate:
	docker compose run --rm web python src/manage.py migrate

makemigrations:
	docker compose run --rm web python src/manage.py makemigrations

shell:
	docker compose run --rm web python src/manage.py shell

superuser:
	docker compose run --rm web python src/manage.py createsuperuser

seed:
	docker compose run --rm web python src/manage.py seed_platform

validate_catalog:
	docker compose run --rm web python src/manage.py validate_public_catalog --fail-on-warning

test:
	docker compose run --rm web pytest

lint:
	docker compose run --rm web ruff check .

format:
	docker compose run --rm web ruff check . --fix
