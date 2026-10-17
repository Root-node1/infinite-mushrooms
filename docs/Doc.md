# Infinite Mushrooms: Technical Documentation

Last updated: commit 4 (accounts app).

## 1. Overview

Infinite Mushrooms helps reishi and oyster mushroom farmers run their farm:

1. Track growing batches through each stage (inoculation, colonization, pinning, fruiting, harvest).
2. Get alerts at each stage by email, SMS and WhatsApp.
3. Log harvests, which become sellable stock.
4. Sell fresh and dried stock through a POS (cash and M-Pesa).

The product proposal (problem, market, competitors, phases) lives in the shared
Claude Doc "Mushroom Farm Manager: Reishi and Oyster". This file covers the code.

## 2. Tech stack

| Layer | Technology | Notes |
| --- | --- | --- |
| Frontend | React + TypeScript (Vite) | PWA, offline-tolerant. Not started. |
| Backend | Django 5.2, Django REST Framework 3.16 | Single source of truth |
| Database | PostgreSQL | psycopg 3 driver |
| Config | python-dotenv | Reads `apps/api/.env` |
| Alerts | n8n, self-hosted | Delivery only |
| SMS | Africa's Talking or similar | Planned |
| WhatsApp | WhatsApp Cloud API | Planned, needs Meta business verification |
| Payments | M-Pesa (Daraja) | Planned, Phase 2 |
| Scheduling | Celery beat or cron | Planned |
| Hosting | Contabo VPS, Cloudflare | zindika.app subdomains |

Docker is deliberately not used yet. Local development uses a Python venv and a
local PostgreSQL. Docker Compose can be added later without changing app code.

## 3. Architecture

One app, one backend. Do not split the farm and POS into two apps: they share batches,
stock and sales.

    React web app  ->  Django REST API  ->  PostgreSQL
                            |
                            v
                      n8n webhook  ->  email / SMS / WhatsApp

| Service | Domain | Role |
| --- | --- | --- |
| Web app | app.zindika.app | UI for farmers and staff |
| API | api.zindika.app | Business logic, data, alert rules |
| n8n | n8n.zindika.app | Message delivery with retries |

### Alert flow (planned)

1. A scheduled job checks batches for upcoming, due and overdue stages.
2. Django decides what to send and to whom, and saves a notification record.
3. Django calls an n8n webhook with `{farmer, channel, message}`.
4. n8n delivers it and reports success or failure back.

Rule: stage logic lives in Django, where it can be tested and versioned.
n8n is only a delivery pipe.

## 4. Repository structure

    apps/api/            Django project
      config/            settings.py, urls.py, wsgi.py, asgi.py
      accounts/          custom User model, admin, tests
      manage.py
      requirements.txt
      .env.example
    apps/web/            React + TypeScript (not started)
    infra/               deployment and n8n config (not started)
    docs/                this file

## 5. Backend setup

See the README for step-by-step setup. Summary:

    sudo service postgresql start
    cd apps/api && source .venv/bin/activate
    python manage.py migrate
    python manage.py runserver

After each WSL restart, run `sudo service postgresql start` again.

### Environment variables (apps/api/.env)

| Variable | Purpose | Example |
| --- | --- | --- |
| DJANGO_SECRET_KEY | Django secret, keep private | long random string |
| DJANGO_DEBUG | 1 for dev, 0 for production | 1 |
| DJANGO_ALLOWED_HOSTS | Comma-separated hosts | localhost,127.0.0.1 |
| POSTGRES_DB | Database name | infinite_mushrooms |
| POSTGRES_USER | Database user | infinite |
| POSTGRES_PASSWORD | Database password | set locally |
| POSTGRES_HOST | Database host | localhost |
| POSTGRES_PORT | Database port | 5432 |

`.env` is git-ignored. `.env.example` is committed and must stay in sync.

## 6. Apps and data model

### accounts

Custom user model, `AUTH_USER_MODEL = "accounts.User"`.

| Field | Type | Notes |
| --- | --- | --- |
| phone | CharField, unique | Login field, stored as E.164 |
| full_name | CharField | Required |
| email | EmailField | Optional |
| role | owner or staff | Default owner |
| is_active, is_staff | Boolean | Django admin flags |
| date_joined | DateTime | |

Phone normalisation (`normalize_phone`): strips spaces, dashes and brackets;
`0712345678` becomes `+254712345678`; `254...` gains a leading `+`; `00` becomes `+`;
anything that is not 10 to 15 digits after the `+` raises a `ValueError`.

Tests: `python manage.py test accounts` (normalisation, validation, uniqueness,
phone login, superuser flags).

### Planned models

`Farm`, `Species`, `StageTemplate`, `Batch`, `BatchStage`, `HarvestRecord`,
`StockItem`, `Sale`, `SaleItem`, `Payment`, `Notification`, `NotificationPreference`.

Stage templates are configurable per species (oyster, reishi): stage names,
expected durations, alert thresholds, yield units and quality grades. Stage
durations and conditions must come from the client farmer, not guesses.

## 7. API

| Method | Path | Description | Auth |
| --- | --- | --- | --- |
| GET | /api/health/ | Service health check | None |
| GET | /admin/ | Django admin | Staff login |

More endpoints are added with each phase.

## 8. Decisions log

| Decision | Reason |
| --- | --- |
| One app and one backend | Farm and POS share the same data |
| n8n for delivery only | Keeps logic testable and versioned |
| Custom User before the first migration | Changing the user model later is painful |
| Phone number as login | Farmers use phones, not emails |
| Venv and local Postgres, no Docker yet | Fewer moving parts early on |
| React + TypeScript frontend | Type safety across the API boundary |

## 9. Phases

1. MVP: auth, farms, batches, stage templates, alert job, email and SMS via n8n.
2. Harvest and POS: harvest logging, stock, sales, cash and M-Pesa, reports.
3. WhatsApp alerts, notification preferences, offline PWA, staff roles.
4. Sensors (temperature, humidity, CO2) and multi-farm support.

## 10. Known gaps

- Login endpoint must normalise the phone before calling `authenticate`, since
  `authenticate(phone=...)` expects E.164.
- WhatsApp needs Meta business verification, start it early.
- Kenyan SMS sender IDs are limited to 11 characters and approval can take weeks.
- Backups for the production database must exist before real farmer data goes in.

## 11. Commit log

| # | Commit | Summary |
| --- | --- | --- |
| 1 | chore: scaffold infinite-mushrooms monorepo | Folders, README, .gitignore |
| 2 | feat(api): Django + DRF project with local Postgres and venv | Settings, health endpoint |
| 3 | docs: full README and technical documentation | Full README and Doc.md |
| 4 | feat(accounts): custom phone-number User with owner/staff roles | User model, admin, tests |
