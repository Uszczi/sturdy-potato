#!/usr/bin/env sh
# Boot an isolated FastAPI API server for the Playwright e2e suite.
#
# The React SPA (served separately by Vite preview) is the app under test; this
# only needs to answer its /api calls. Uses a dedicated SQLite database that is
# wiped, migrated, and re-seeded on every start, so the suite always runs
# against the known demo fixtures (see server/src/cli/seed.py). Never points at
# the developer's real db.sqlite3.
set -e

HOST="${E2E_API_HOST:-127.0.0.1}"
PORT="${E2E_API_PORT:-8000}"

# This script lives at <repo>/client/e2e/scripts/serve.sh.
ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"

DB_FILE="${E2E_DB_FILE:-$ROOT/e2e-db.sqlite3}"
export DATABASE_URL="${DATABASE_URL:-sqlite+aiosqlite:///$DB_FILE}"
export SEEDDB_DEMO_PASSWORD="${SEEDDB_DEMO_PASSWORD:-demo-password-123}"

# Allow the SPA's browser origin (Vite preview) to call the API cross-origin.
export CORS_ORIGINS="${CORS_ORIGINS:-http://127.0.0.1:5173,http://localhost:5173}"

# Start from a clean database so every run is deterministic.
rm -f "$DB_FILE"

# The uv project and all entrypoints live under server/ (src/ on the path).
cd "$ROOT/server"
uv run alembic -c src/infrastructure/alembic/alembic.ini upgrade head
PYTHONPATH=src uv run python -m cli seed
exec uv run uvicorn main:app --app-dir src --host "$HOST" --port "$PORT"
