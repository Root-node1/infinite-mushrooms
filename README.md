# Infinite Mushrooms

Farm management app and point of sale (POS) for reishi and oyster mushroom growers.
Farmers track growing batches, get alerts at every stage through to harvest
(email, SMS, WhatsApp), and sell the harvest through a built-in POS.

Built on commission for a reishi and oyster farmer, by the Zindika team.

## Tech stack

| Layer | Technology |
| --- | --- |
| Frontend | React + TypeScript (Vite), PWA |
| Backend | Django 5.2 + Django REST Framework |
| Database | PostgreSQL |
| Alerts | n8n (delivery only): email, SMS, WhatsApp |
| Scheduling | Celery beat or cron (planned) |
| Hosting | Contabo VPS behind Cloudflare (zindika.app) |

## Architecture

One app, one backend. Batches, inventory and sales share the same data.

| Service | Domain | Role |
| --- | --- | --- |
| Web app | app.zindika.app | Farmer dashboard, batch tracking, POS |
| API | api.zindika.app | Single source of truth and all business logic |
| n8n | n8n.zindika.app | Delivers messages only, no business logic |

Django decides what to send and to whom, then calls an n8n webhook.
n8n delivers it through the right channel and reports back.

## Repository structure

    infinite-mushrooms/
    ├── apps/
    │   ├── api/        Django + DRF backend
    │   │   ├── config/     project settings and root URLs
    │   │   ├── accounts/   custom phone-number User
    │   │   └── manage.py
    │   └── web/        React + TypeScript frontend (not started)
    ├── infra/          deployment and n8n config (not started)
    ├── docs/           Doc.md and technical notes
    └── README.md

## Getting started (backend)

Requires Python 3.10+ and PostgreSQL (WSL/Ubuntu or Linux).

1. Start Postgres and create the database:

        sudo service postgresql start
        sudo -u postgres psql
        CREATE USER infinite WITH PASSWORD 'infinite_dev_pw' CREATEDB;
        CREATE DATABASE infinite_mushrooms OWNER infinite;

2. Set up the Python environment:

        cd apps/api
        python3 -m venv .venv
        source .venv/bin/activate
        pip install -r requirements.txt

3. Configure environment variables:

        cp .env.example .env
        # set DJANGO_SECRET_KEY to a long random value

4. Migrate, create an admin and run:

        python manage.py migrate
        python manage.py createsuperuser
        python manage.py runserver

5. Check it works:

        curl http://localhost:8000/api/health/

   Admin is at http://localhost:8000/admin/

Run the tests with `python manage.py test`.

## Commands (run.sh)

One script wraps the common tasks. Run `./run.sh help` for the list.

    ./run.sh setup      # venv, dependencies, .env
    ./run.sh db         # start Postgres, create dev user and database
    ./run.sh migrate
    ./run.sh api        # dev server on :8000
    ./run.sh ci         # exactly what CI runs: check + migration check + tests
    ./run.sh progress   # checklist counts

## CI

GitHub Actions (`.github/workflows/ci.yml`) runs on every pull request and every push to
`main`: Django check, missing-migration check and the full test suite against a Postgres 16
service container. Run `./run.sh ci` locally before pushing.

## Authentication

Users log in with a phone number, not a username. Numbers are stored in
E.164 format and local Kenyan numbers (07xx) default to +254.
Roles: `owner` (farm owner) and `staff` (farm staff).

## Project status

Phase 1 (MVP): batch tracking and stage alerts. In progress.

- [x] Monorepo scaffold
- [x] Django + DRF project with PostgreSQL
- [x] Custom phone-number User with roles
- [ ] Farms, species and stage templates, batches
- [ ] Stage alert job and n8n webhook
- [ ] React + TypeScript frontend
- [ ] POS, harvest and stock (Phase 2)
- [ ] WhatsApp alerts and sensors (Phases 3 and 4)

Full details are in [docs/Doc.md](docs/Doc.md).
Role-by-role MVP checklist: [docs/CHECKLIST.md](docs/CHECKLIST.md).

## Conventions

- Small, commit-sized changes with conventional messages (`feat:`, `fix:`, `chore:`, `docs:`).
- Every commit updates `docs/Doc.md` and this README.
- Business logic lives in Django, never in n8n.
- Never commit `.env` or `.venv`.
