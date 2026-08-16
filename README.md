# Sturdy Potato

The Django project is split into two application boundaries:

- `potato/api` owns the REST API and its `/api/` routes.
- `potato/web` owns the authenticated task pages and their `/tasks/` routes.
- `potato/infrastructure` owns the database models and repositories shared by both.
- `potato/todo` contains the shared task validation schemas and compatibility imports.

Both surfaces use the same Django settings, authentication, dependency-injection container,
and database. The split keeps transport-specific code separate without changing the public
URLs or the existing task behavior.

## Development

Install Python dependencies with `uv` and JavaScript dependencies with `npm install`.

Run the Django application:

```bash
uv run python potato/manage.py runserver
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
