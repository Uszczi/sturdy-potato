# Sturdy Potato

A FastAPI backend for a React todo SPA. The server is organized as:

- `server/src/main.py` builds the FastAPI app and wires the routers.
- `server/src/api/routes/` owns the HTTP layer (`/api/tasks/`, `/api/projects/`, `/api/token/`).
- `server/src/repositories/` holds the async SQLAlchemy data access, one class per aggregate.
- `server/src/models.py` defines the SQLModel tables (`User`, `Project`, `Todo`).
- `server/src/schemas/` contains the Pydantic request/response models.
- `server/src/auth.py` handles password hashing (argon2) and JWT issue/verify.
- `server/src/seed.py` seeds the demo user and example data.

Projects belong to one user, and tasks may be assigned to one of that user's projects.
Schema changes are versioned with Alembic (`server/src/infrastructure/alembic/`).
Python tooling (`pyproject.toml`, `uv.lock`, `Dockerfile`) lives under `server/`.

## Development

Install Python dependencies with `uv` and JavaScript dependencies (for the SPA and
e2e suite) with `npm install` inside `client/`.

Apply migrations and seed the demo data:

```bash
just migrate
just seed
```

Run the API (http://localhost:8000, docs at `/docs`):

```bash
just run
```

Create a new migration after changing the models:

```bash
just makemigrations "describe the change"
```

Run the test suite (100% coverage required):

```bash
just test
```

Run the application with Docker Compose:

```bash
cd server && docker compose up --build
```

The API is available at `http://localhost:8000`. SQLite data is stored in the
`sqlite_data` Compose volume.

Run the production Compose deployment (serves the ASGI app with Uvicorn workers):

```bash
SECRET_KEY=replace-with-a-long-random-value \
CORS_ORIGINS=https://example.com \
docker compose -f deployment/prod/docker-compose.yml up --build
```
