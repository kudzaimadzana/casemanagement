# CI / Linux entrypoints. On Windows use scripts/tasks.ps1 with the same target names.
PY ?= python

.PHONY: install run lint format test cov up down logs migrate

install:
	$(PY) -m pip install -r requirements-dev.txt

# No Docker: SQLite in instance/, in-process fake Redis, Flask debug server on localhost.
# Applies migrations and loads demo accounts/data on first run (both are idempotent).
LOCAL_ENV = APP_PROFILE=development APP_DB_URL=sqlite:///$(CURDIR)/instance/dev.db \
	APP_DB_MIGRATION_URL=sqlite:///$(CURDIR)/instance/dev.db USE_FAKE_REDIS=true \
	BEHIND_PROXY=false FLASK_SKIP_DOTENV=1

run:
	mkdir -p instance
	$(LOCAL_ENV) $(PY) -m flask --app wsgi db upgrade
	$(LOCAL_ENV) $(PY) -m flask --app wsgi seed demo
	$(LOCAL_ENV) $(PY) -m flask --app wsgi run --debug --host 127.0.0.1 --port 5000

lint:
	$(PY) -m ruff check .
	$(PY) -m black --check .

format:
	$(PY) -m ruff check --fix .
	$(PY) -m black .

test:
	$(PY) -m pytest

cov:
	$(PY) -m pytest --cov --cov-report=term-missing

up:
	docker compose up --build -d

down:
	docker compose down

logs:
	docker compose logs -f web worker nginx

migrate:
	docker compose run --rm migrate
