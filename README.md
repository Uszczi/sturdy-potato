# Sturdy Potato

The Django project is split into two application boundaries:

- `server/api` owns the REST API and its `/api/` routes.
- `server/web` owns the authenticated task and project pages under `/tasks/` and `/projects/`.
- `server/infrastructure` owns the database models and repositories shared by both.
- Projects belong to one user, and tasks may be assigned to one of that user's projects.
- `server/serializers/todo/task.py` contains the shared task validation schemas.

Both surfaces use the same Django settings, authentication, dependency-injection container,
and database. The split keeps transport-specific code separate without changing the public
URLs or the existing task behavior.

## Development

Install Python dependencies with `uv` and JavaScript dependencies with `npm install`.

Run the Django application:

```bash
uv run python server/manage.py runserver
```

Build the Vite assets:

```bash
npm run build
```

Run the test suite:

```bash
uv run pytest
```

Run the Django project through Aspire:

```bash
npm run aspire:start
```

Run the application with Docker Compose:

```bash
docker compose up --build
```

The application is available at `http://localhost:8000`. SQLite data is stored in
the `sqlite_data` Compose volume.

Run the production Compose deployment with `DJANGO_DEBUG=false` and
`DJANGO_ENV=prod`. It serves the Django ASGI application with Uvicorn for
async and WebSocket support:

```bash
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1 \
DJANGO_SECRET_KEY=replace-with-a-long-random-value \
docker compose -f deployment/prod/docker-compose.yml up --build
```

The production site is available at `http://localhost:8000`.
