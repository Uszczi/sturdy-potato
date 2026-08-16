#!/usr/bin/env sh
# Boot an isolated Django instance for Playwright e2e tests.
#
# Uses a dedicated SQLite database that is wiped and re-seeded on every start,
# so the suite always runs against the known demo fixtures (see the `seeddb`
# management command). Never points at the developer's real db.sqlite3.
set -e

HOST="${E2E_HOST:-127.0.0.1}"
PORT="${E2E_PORT:-8099}"

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"

export DJANGO_DB_PATH="${DJANGO_DB_PATH:-$ROOT/potato/e2e-db.sqlite3}"
export SEEDDB_DEMO_PASSWORD="${SEEDDB_DEMO_PASSWORD:-demo-password-123}"
export SEEDDB_SUPERUSER_PASSWORD="${SEEDDB_SUPERUSER_PASSWORD:-admin-password-123}"

# Serve the built Vite assets (manifest) instead of the dev server, which isn't
# running during e2e, so the pages are fully styled.
export DJANGO_VITE_DEV_MODE=false

# Build the frontend assets so the manifest and CSS exist.
cd "$ROOT"
npm run build

# Start from a clean database so every run is deterministic.
rm -f "$DJANGO_DB_PATH"

cd "$ROOT/potato"
uv run python manage.py migrate --noinput
uv run python manage.py seeddb
exec uv run python manage.py runserver "$HOST:$PORT" --noreload
