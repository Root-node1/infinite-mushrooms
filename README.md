# Infinite Mushrooms

Farm management app and POS for reishi and oyster mushroom growers.
Batch tracking, stage alerts (email, SMS, WhatsApp) and sales.

## Structure
- `apps/web`: React + TypeScript PWA (app.zindika.app)
- `apps/api`: Django + DRF (api.zindika.app)
- `infra`: deployment and n8n config (n8n.zindika.app)
- `docs`: proposal and technical notes

## Backend setup (apps/api)

Requires Python 3.10+ and PostgreSQL.

    sudo service postgresql start
    cd apps/api
    python3 -m venv .venv && source .venv/bin/activate
    pip install -r requirements.txt
    cp .env.example .env    # then set DJANGO_SECRET_KEY
    python manage.py runserver
    curl http://localhost:8000/api/health/

Create the database and user first:

    CREATE USER infinite WITH PASSWORD 'infinite_dev_pw' CREATEDB;
    CREATE DATABASE infinite_mushrooms OWNER infinite;

Migrations are intentionally not run yet: the custom user model comes first.

## Status
Phase 1 (MVP): batch tracking and stage alerts. In progress.
