# MC-CMS: First Mutual Health Managed Care Case Management System

Flask + Jinja/HTMX application that gives FMH Managed Care a proactive, population-level view of
members: Member 360, disease registries, risk stratification, early-warning alerts, work queues
and case management. The full specification is [docs/PRD (1).md](docs/PRD%20(1).md). Choices
made where the PRD is silent are in [docs/DECISIONS.md](docs/DECISIONS.md).

**Status:** skeleton: foundation, login with roles and audit logging, synthetic demo data, and
an initial dashboard, services analytics, and searchable member records. New to the project? Start
with [docs/ONBOARDING.md](docs/ONBOARDING.md).

The Dashboard and Services pages filter claims by service date and category. The Members page
filters by search text, status, sex and plan, and shows claim count, paid total and latest claim at
a glance. The disease registry page provides diabetes, hypertension, CKD, and oncology cohorts
based on diagnosis and claim evidence. HbA1c is an explicitly labeled demo mock because pathology
results are not yet modeled. Member details show profile, clinical, utilization and financial
sections with a claims-derived five-tier risk assessment. The reference demo persona's 645%
claims ratio, ICU/HDU days and exhausted benefits are explicitly labeled mock scenario values;
annual premium, admission dates, ward-day quantities and benefit limits are not stored. These mock
values are hidden in production, and no equivalent values are inferred for other members. Clinical
CSV export is limited to users with `member.export` and every export is audited. The dashboard also
shows claim-derived clinical, financial and care-management warning signals to users with
`alert.view`; these are recalculated on page load and are not yet persisted or dismissible.

## Quick run without Docker

Requires Python 3.12, 3.13, or 3.14. On Windows, install dependencies once to create `.venv`:

```
.\scripts\tasks.ps1 install
```

On Linux/macOS, create and activate a virtual environment with Python 3.12, 3.13, or 3.14, then run
`make install`.

```
.\scripts\tasks.ps1 run      # Windows
make run                     # Linux/macOS
```

This opens http://127.0.0.1:5000 using SQLite (`instance/dev.db`) and an in-process fake Redis.
The first run applies migrations and creates one demo account per role (`officer`, `manager`,
`analyst`, `sysadmin`, `exec`) plus 300 synthetic members. Passwords are printed and saved in
`instance/demo-accounts.txt`. `.\scripts\tasks.ps1 reset-demo` regenerates them.

There's no build and no services to install, but sessions reset whenever the server restarts.
Use it for UI work; check anything involving MySQL, Redis or TLS on the Docker stack below.

## Running the dev stack (Docker)

Prerequisite: Docker Desktop (Windows/macOS) or Docker Engine + Compose v2.24+ (Linux).

1. Create the two local env files (both git-ignored):
   - `.env` from `.env.compose.example`: compose settings and DB/Redis bootstrap passwords.
   - `.env.development` from `.env.example`: app settings. The passwords in its URLs must match `.env`.
   On Linux, set `COMPOSE_PATH_SEPARATOR=:` and use `:` in `COMPOSE_FILE`.
2. Start everything:
   ```
   docker compose up --build -d
   docker compose run --rm migrate
   ```
3. Load demo accounts and data: `docker compose run --rm migrate flask seed demo`
4. Open https://localhost:8443. The certificate is self-signed in dev, so accept the browser warning.

Services: `web` (Flask), `worker` (APScheduler), `db` (MySQL 8), `redis`, `nginx` (TLS). In dev,
MySQL (3306) and Redis (6379) are published on localhost only.

Health: `/healthz` (liveness) and `/readyz` (DB + Redis + last ETL status).

## Tests and lint

| | Linux / CI | Windows |
|---|---|---|
| Install | `make install` | `.\scripts\tasks.ps1 install` |
| Tests | `make test` | `.\scripts\tasks.ps1 test` |
| Coverage | `make cov` | `.\scripts\tasks.ps1 cov` |
| Lint | `make lint` | `.\scripts\tasks.ps1 lint` |
| Format | `make format` | `.\scripts\tasks.ps1 format` |

Tests run on the `testing` profile (SQLite + fakeredis), so they need neither Docker nor MySQL.

## Profiles

`APP_PROFILE` = `development` | `testing` | `production` selects the config class in
`app/config.py` and loads `.env.{profile}`. Real environment variables override the file.
Production refuses to start if `SECRET_KEY`, `APP_DB_URL` or `REDIS_URL` are missing or
placeholders.

## Production

Set `.env` to `COMPOSE_FILE=docker-compose.yml` and `MCCMS_ENV_FILE=.env.production`, mount the real
TLS certificate at `/etc/nginx/certs/server.crt` and `server.key` on the `nginx` service, then run
`docker compose up -d` and `docker compose run --rm migrate`. Migrations run as a one-off
container, never on web start.
