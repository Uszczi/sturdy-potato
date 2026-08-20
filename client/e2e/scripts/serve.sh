#!/usr/bin/env sh
# Boot an isolated FastAPI API server for the Playwright e2e suite.
#
# The React SPA (served separately by Vite preview) is the app under test; this
# only needs to answer its /api calls. Uses a dedicated PostgreSQL container
# that is recreated from scratch, migrated, and re-seeded on every start, so the
# suite always runs against the known demo fixtures (see server/src/cli/seed.py).
# The container/port are distinct from the dev database, so it never touches a
# developer's local PostgreSQL.
set -e

HOST="${E2E_API_HOST:-127.0.0.1}"
PORT="${E2E_API_PORT:-8000}"

# This script lives at <repo>/client/e2e/scripts/serve.sh.
ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"

DB_CONTAINER="${E2E_DB_CONTAINER:-sturdy-potato-e2e-db}"
DB_PORT="${E2E_DB_PORT:-5433}"
DB_NAME="${E2E_DB_NAME:-sturdy_potato_e2e}"
export DATABASE_URL="${DATABASE_URL:-postgresql+asyncpg://postgres:postgres@127.0.0.1:$DB_PORT/$DB_NAME}"

REDIS_CONTAINER="${E2E_REDIS_CONTAINER:-sturdy-potato-e2e-redis}"
REDIS_PORT="${E2E_REDIS_PORT:-6380}"
export REDIS_URL="${REDIS_URL:-redis://127.0.0.1:$REDIS_PORT/0}"

export SEEDDB_DEMO_PASSWORD="${SEEDDB_DEMO_PASSWORD:-demo-password-123}"

# Allow the SPA's browser origin (Vite preview) to call the API cross-origin.
export CORS_ORIGINS="${CORS_ORIGINS:-http://127.0.0.1:5173,http://localhost:5173}"

# Recreate the database and cache containers so every run starts clean. Ports are
# distinct from the dev services, so this never touches a developer's own data.
docker rm -f "$DB_CONTAINER" "$REDIS_CONTAINER" >/dev/null 2>&1 || true
docker run -d --name "$DB_CONTAINER" \
	-e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB="$DB_NAME" \
	-p "$DB_PORT:5432" postgres:17-alpine >/dev/null
docker run -d --name "$REDIS_CONTAINER" -p "$REDIS_PORT:6379" redis:7-alpine >/dev/null

# Wait until PostgreSQL is ready to accept connections before migrating.
until docker exec "$DB_CONTAINER" pg_isready -U postgres -d "$DB_NAME" >/dev/null 2>&1; do
	sleep 0.5
done

# The uv project and all entrypoints live under server/ (src/ on the path).
cd "$ROOT/server"
uv run alembic -c src/infrastructure/alembic/alembic.ini upgrade head
PYTHONPATH=src uv run python -m cli seed
exec uv run uvicorn main:app --app-dir src --host "$HOST" --port "$PORT"
