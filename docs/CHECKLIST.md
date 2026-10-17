# Infinite Mushrooms: MVP Checklist (Phase 1)

Last updated: 18 Oct 2026

Stack: React + TypeScript (apps/web), Django + DRF (apps/api), PostgreSQL. Monorepo.

Legend: ✓ done | ✗ pending

MVP goal: one real farmer runs one real cycle, with batch tracking and stage alerts by email and SMS.

Live counts: run `./run.sh progress`

## DevOps

| Status | Task | Owner |
| --- | --- | --- |
| ✓ | Monorepo scaffold (apps, infra, docs, .gitignore) | |
| ✓ | run.sh dev runner (setup, db, api, test, ci, progress) | |
| ✗ | GitHub Actions CI green: Postgres service, Django tests on every PR | |
| ✗ | Branch protection on main: PR required, CI must pass | |
| ✗ | Kanban board with columns, WIP limits and definition of done | |
| ✗ | Cloudflare DNS: app, api and n8n subdomains on zindika.app | |
| ✗ | VPS hardening: SSH keys only, firewall, non-root user | |
| ✗ | Self-host n8n on the VPS | |
| ✗ | Postgres backups on the VPS (no auto backup was bought) | |
| ✗ | Staging deploy for API and web | |
| ✗ | CD pipeline: deploy to VPS from main after CI passes | |

## Server (backend, Django)

| Status | Task | Owner |
| --- | --- | --- |
| ✓ | Django + DRF + PostgreSQL project with health endpoint | |
| ✓ | accounts: custom phone-number User, owner and staff roles, phone login backend | |
| ✗ | farms: Farm, Species, StageTemplate, Batch, BatchStage models | |
| ✗ | Stage timeline service (generate dated stages from templates) | |
| ✗ | DRF endpoints: farms, batches, stages | |
| ✗ | Login endpoint with token auth | |
| ✗ | Daily alert job: due and overdue stages | |
| ✗ | Notification model and n8n webhook call | |
| ✗ | Tests for each of the above | |

## Frontend (React + TypeScript)

| Status | Task | Owner |
| --- | --- | --- |
| ✗ | Vite + React + TypeScript scaffold in apps/web | |
| ✗ | Typed API client | |
| ✗ | Login screen | |
| ✗ | Batch list and create-batch form | |
| ✗ | Batch detail with stage timeline | |
| ✗ | Dashboard: what is due today | |
| ✗ | PWA basics: installable, tolerant of poor connectivity | |
| ✗ | CI web job: lint, typecheck, test, build | |

## Product and client

| Status | Task | Owner |
| --- | --- | --- |
| ✓ | Project named: Infinite Mushrooms | |
| ✗ | Get real stage durations and conditions from the farmer (oyster and reishi) | |
| ✗ | Agree commission terms in writing (scope, price, payments, code ownership) | |
| ✗ | Start SMS sender ID registration and Meta WhatsApp verification | |

## Added (not in the original plan)

| Status | Task | Why it was added |
| --- | --- | --- |
| ✓ | README and docs/Doc.md written | Documentation updated with every commit |
| ✓ | Phone login backend (accepts 0712..., 254712..., +254712...) | Admin login failed with local number format |
| ✓ | run.sh dev runner | One command per task for every dev |
| ✗ | GitHub Actions CI | Green or red signal before anything merges |
| ✗ | Three role docs: DevOps, frontend, server devs | Frontend designer does not touch the server |
| ✗ | Kanban board with WIP limits | Team process for all teams |

## Rules

- Every commit updates docs/Doc.md, README and this checklist.
- One task = one card = one small PR.
- Business logic lives in Django, never in n8n.
