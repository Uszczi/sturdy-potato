FROM python:3.13-slim-bookworm AS python-dependencies

COPY --from=ghcr.io/astral-sh/uv:0.11.19 /uv /uvx /bin/

WORKDIR /app

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

COPY server/pyproject.toml server/uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project


FROM python:3.13-slim-bookworm

WORKDIR /app

ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/src

COPY --from=python-dependencies /app/.venv /app/.venv
COPY server/src ./src

RUN mkdir -p /app/data

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "3"]
