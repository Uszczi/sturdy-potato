# Sturdy Potato

A FastAPI backend for a React todo SPA. The server is organized as:

- `server/src/main.py` builds the FastAPI app and wires the routers.
- `server/src/api/routes/` owns the HTTP layer (`/api/tasks/`, `/api/tasks/{id}/comments/`, `/api/projects/`, `/api/token/`, `/api/register/`, `/api/time/`).
- `server/src/infrastructure/cache.py` holds the async Redis client used for caching.
- `server/src/repositories/` holds the async SQLAlchemy data access, one class per aggregate.
- `server/src/models.py` defines the SQLModel tables (`User`, `Project`, `Todo`, `Comment`).
- `server/src/schemas/` contains the Pydantic request/response models.
- `server/src/auth.py` handles password hashing (argon2) and JWT issue/verify.
- `server/src/seed.py` seeds the demo user and example data.

Projects belong to one user, and tasks may be assigned to one of that user's projects.
Tasks can carry comments; deleting a task cascades to its comments.
Schema changes are versioned with Alembic (`server/src/infrastructure/alembic/`).
Python tooling (`pyproject.toml`, `uv.lock`, `Dockerfile`) lives under `server/`.

## Development

Install Python dependencies with `uv` and JavaScript dependencies (for the SPA and
e2e suite) with `npm install` inside `client/`.

The app uses PostgreSQL (via the async `asyncpg` driver) and Redis (for caching).
`aspire start` runs both containers for you; to run the API on its own
(`just migrate` / `just run`), start a local Postgres and Redis first (in separate
terminals):

```bash
just db
just redis
```

Apply migrations and seed the demo data:

```bash
just migrate
just seed
```

Run the API (http://localhost:8000, docs at `/docs`):

```bash
just run
```

`GET /api/time/` returns the current server time and caches it in Redis for 15
minutes: the first call computes the timestamp (`"cached": false`), and every call
within the window returns that same frozen value (`"cached": true`) until the
entry expires.

Create a new migration after changing the models:

```bash
just makemigrations "describe the change"
```

Run the test suite (100% coverage required). Tests run against real PostgreSQL and
Redis instances that [testcontainers](https://testcontainers.com/) starts
automatically, so a running Docker daemon is required:

```bash
just test
```

Run the application with Docker Compose:

```bash
cd server && docker compose up --build
```

The API is available at `http://localhost:8000`. Postgres data is stored in the
`postgres_data` Compose volume.

Run the production Compose deployment (serves the ASGI app with Uvicorn workers,
backed by a Postgres container):

```bash
SECRET_KEY=replace-with-a-long-random-value \
POSTGRES_PASSWORD=replace-with-a-strong-password \
CORS_ORIGINS=https://example.com \
docker compose -f deployment/prod/docker-compose.yml up --build
```
