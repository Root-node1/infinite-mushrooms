#!/usr/bin/env bash
# Infinite Mushrooms dev runner. Usage: ./run.sh <command>
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
API="$ROOT/apps/api"
WEB="$ROOT/apps/web"
PY="$API/.venv/bin/python"

die() { echo "error: $*" >&2; exit 1; }

need_venv() { [ -x "$PY" ] || die "no venv found. Run: ./run.sh setup"; }

manage() {
  need_venv
  (cd "$API" && "$PY" manage.py "$@")
}

pg() { (cd /tmp && sudo -u postgres psql "$@"); }

usage() {
  cat << 'USAGE'
Usage: ./run.sh <command>

  setup      create venv, install dependencies, create apps/api/.env
  db         start Postgres and create the dev user and database
  migrate    apply database migrations
  api        run the Django dev server on :8000
  web        run the React dev server (once apps/web is scaffolded)
  test       run the backend tests (extra args are passed through)
  check      Django system check and "migrations missing" check
  ci         run exactly what CI runs: Django check + tests, web lint + build
  progress   show checklist counts from docs/CHECKLIST.md
USAGE
}

cmd_setup() {
  command -v python3 > /dev/null || die "python3 not found"
  [ -x "$PY" ] || python3 -m venv "$API/.venv"
  "$API/.venv/bin/pip" install -r "$API/requirements.txt"
  if [ ! -f "$API/.env" ]; then
    cp "$API/.env.example" "$API/.env"
    secret="$(python3 -c 'import secrets; print(secrets.token_urlsafe(50))')"
    sed -i "s|^DJANGO_SECRET_KEY=.*|DJANGO_SECRET_KEY=$secret|" "$API/.env"
    echo "created apps/api/.env"
  fi
  if [ -f "$WEB/package.json" ]; then
    (cd "$WEB" && npm install)
  fi
  echo "setup done. Next: ./run.sh db && ./run.sh migrate"
}

cmd_db() {
  sudo service postgresql start
  role="$(pg -tAc "SELECT 1 FROM pg_roles WHERE rolname='infinite'")"
  [ "$role" = "1" ] || pg -c "CREATE USER infinite WITH PASSWORD 'infinite_dev_pw' CREATEDB;"
  db="$(pg -tAc "SELECT 1 FROM pg_database WHERE datname='infinite_mushrooms'")"
  [ "$db" = "1" ] || pg -c "CREATE DATABASE infinite_mushrooms OWNER infinite;"
  echo "postgres ready"
}

cmd_check() {
  manage check
  manage makemigrations --check --dry-run
}

cmd_web() {
  [ -f "$WEB/package.json" ] || die "apps/web is not scaffolded yet"
  (cd "$WEB" && npm run dev)
}

cmd_web_ci() {
  [ -f "$WEB/package.json" ] || return 0
  (cd "$WEB" && { [ -d node_modules ] || npm ci; } && npm run lint && npm run build)
}

cmd_progress() {
  [ -f "$ROOT/docs/CHECKLIST.md" ] || die "docs/CHECKLIST.md not found"
  awk '
    /^## /          { sec = substr($0, 4); next }
    sec ~ /^Added/  { next }
    /^\| ✓/         { done[sec]++; if (!(sec in seen)) { seen[sec] = 1; order[++n] = sec } }
    /^\| ✗/         { todo[sec]++; if (!(sec in seen)) { seen[sec] = 1; order[++n] = sec } }
    END {
      printf "%-34s %5s %8s\n", "Section", "Done", "Pending"
      for (i = 1; i <= n; i++) {
        s = order[i]
        printf "%-34s %5d %8d\n", s, done[s] + 0, todo[s] + 0
        td += done[s]; tp += todo[s]
      }
      printf "%-34s %5d %8d\n", "TOTAL", td, tp
    }
  ' "$ROOT/docs/CHECKLIST.md"
}

case "${1:-help}" in
  setup)    cmd_setup ;;
  db)       cmd_db ;;
  migrate)  manage migrate ;;
  api)      shift; manage runserver "$@" ;;
  web)      cmd_web ;;
  test)     shift; manage test "$@" ;;
  check)    cmd_check ;;
  ci)       cmd_check; manage test; cmd_web_ci ;;
  progress) cmd_progress ;;
  help|-h|--help) usage ;;
  *)        usage; exit 1 ;;
esac
