FROM node:22-bookworm-slim AS frontend

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci

COPY assets ./assets
COPY templates ./templates
COPY static ./static
COPY vite.config.mjs ./
RUN npm run build


FROM python:3.13-slim-bookworm AS python-dependencies

COPY --from=ghcr.io/astral-sh/uv:0.11.19 /uv /uvx /bin/

WORKDIR /app

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project


FROM python:3.13-slim-bookworm

WORKDIR /app

ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DJANGO_DEBUG=0 \
    DJANGO_ALLOWED_HOSTS="localhost,127.0.0.1"

RUN apt-get update \
    && apt-get install --no-install-recommends -y \
        libgdal32 \
        libsqlite3-mod-spatialite \
    && rm -rf /var/lib/apt/lists/*

COPY --from=python-dependencies /app/.venv /app/.venv
COPY --from=frontend /app/static /app/static
COPY potato ./potato
COPY templates ./templates

RUN mkdir -p /app/staticfiles /app/data \
    && python potato/manage.py collectstatic --noinput \
    && python potato/manage.py check

WORKDIR /app/potato

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "--insecure", "0.0.0.0:8000"]
