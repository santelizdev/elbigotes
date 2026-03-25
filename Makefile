PROJECT_NAME=elbigotes

.PHONY: build up down logs migrate makemigrations shell superuser seed test lint format validate_catalog

build:
	docker compose build

up:
	docker compose up --build

down:
	docker compose down

logs:
	docker compose logs -f web celery_worker celery_beat

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
