#!/usr/bin/env sh
# Boot an isolated Django API server for the Playwright e2e suite.
#
# The React SPA (served separately by Vite preview) is the app under test; this
# only needs to answer its /api calls. Uses a dedicated SQLite database that is
# wiped and re-seeded on every start, so the suite always runs against the known
# demo fixtures (see the `seeddb` management command). Never points at the
# developer's real db.sqlite3.
set -e

HOST="${E2E_API_HOST:-127.0.0.1}"
PORT="${E2E_API_PORT:-8000}"

# This script lives at <repo>/client/e2e/scripts/serve.sh.
ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"

export DJANGO_DB_PATH="${DJANGO_DB_PATH:-$ROOT/e2e-db.sqlite3}"
export SEEDDB_DEMO_PASSWORD="${SEEDDB_DEMO_PASSWORD:-demo-password-123}"
export SEEDDB_SUPERUSER_PASSWORD="${SEEDDB_SUPERUSER_PASSWORD:-admin-password-123}"

# Allow the SPA's browser origin (Vite preview) to call the API cross-origin.
export DJANGO_CORS_ALLOWED_ORIGINS="${DJANGO_CORS_ALLOWED_ORIGINS:-http://127.0.0.1:5173,http://localhost:5173}"

# Start from a clean database so every run is deterministic.
rm -f "$DJANGO_DB_PATH"

cd "$ROOT/server"
uv run python manage.py migrate --noinput
uv run python manage.py seeddb
exec uv run python manage.py runserver "$HOST:$PORT" --noreload
