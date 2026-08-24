# Sturdy Potato

A FastAPI backend for a React todo SPA. The server is organized as:

- `server/src/main.py` builds the FastAPI app, wires the routers, maps domain
  errors to HTTP responses, and serves the built SPA when it is present.
- `server/src/api/routes/` owns the HTTP layer. Resource routes (`/api/tasks/`,
  `/api/tasks/{id}/comments/`, `/api/projects/`, `/api/chat/`) act on the
  workspace named by the `X-Workspace-Id` header, defaulting to the caller's
  personal one; `/api/workspaces/` (and `/api/workspaces/{id}/`), `/api/token/`,
  `/api/register/` and `/api/time/` need no workspace.
- `server/src/api/dependencies.py` builds each use case from the request's unit of
  work, naming the repositories it needs.
- `server/src/use_cases/` holds the business logic, free of any framework. It owns
  its own entities, DTOs, errors and `ports.py` (the repository Protocols), so it
  never imports `infrastructure`.
- `server/src/infrastructure/repositories/` implements those ports with async
  SQLAlchemy, one class per aggregate, and `unit_of_work.py` commits them together.
- `server/src/infrastructure/models.py` defines the SQLModel tables (`User`,
  `Workspace`, `WorkspaceMembership`, `Project`, `Task`, `Comment`).
- `server/src/infrastructure/cache.py` holds the async Redis client used for caching.
- `server/src/infrastructure/security.py` handles password hashing (argon2) and JWT
  issue/verify; `server/src/auth.py` turns those into the request's current user
  and workspace.
- `server/src/schemas/` contains the Pydantic request/response models.
- `server/src/cli/` is the management entrypoint (`python -m cli`), including
  `seed.py` for the demo user and example data.

Projects belong to a workspace, and a user reaches them through their membership of
it. Tasks may be assigned to one of the workspace's projects. Tasks can carry
comments; deleting a task cascades to its comments, and deleting a project cascades
to its tasks.

Which statuses a task can occupy is per-board: a project owns its **workflow** (an
ordered list of statuses, rendered as the kanban's columns), copied from the
workspace's default when the project is created and edited independently after
that. The workspace's own workflow also serves the inbox — the tasks belonging to
no project. See `CONTEXT.md` for the vocabulary and `docs/adr/` for why a task
carries a denormalised `is_done` alongside its status.
Schema changes are versioned with Alembic (`server/src/infrastructure/alembic/`).
The repo is a uv workspace: the root `pyproject.toml` and `uv.lock` tie together
the `server/` and `mcp/` members, which share the root `.venv`. `mcp/` serves the
same use cases as MCP tools, so the assistant and the REST API run identical logic.

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
