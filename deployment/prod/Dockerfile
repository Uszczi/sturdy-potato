FROM node:22-bookworm-slim AS client-build

WORKDIR /build

# Install deps first so this layer caches unless the lockfile changes.
COPY client/package.json client/package-lock.json ./
RUN npm ci

COPY client/ ./
RUN npm run build


FROM python:3.13-slim-bookworm AS python-dependencies

COPY --from=ghcr.io/astral-sh/uv:0.11.19 /uv /uvx /bin/

WORKDIR /app

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

# Resolve from the frozen workspace lock (root pyproject.toml + root uv.lock).
# --no-install-workspace installs every member's third-party deps but not the
# member packages themselves; the first-party source comes in below on
# PYTHONPATH. The member pyproject files let uv see the workspace layout.
COPY pyproject.toml uv.lock ./
COPY server/pyproject.toml ./server/pyproject.toml
COPY mcp/pyproject.toml ./mcp/pyproject.toml
RUN uv sync --frozen --no-dev --no-install-workspace


FROM python:3.13-slim-bookworm

WORKDIR /app

ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/src

COPY --from=python-dependencies /app/.venv /app/.venv
COPY server/src ./src

# Built SPA, served same-origin by FastAPI (see main.py / settings.frontend_dir).
COPY --from=client-build /build/dist ./client-dist

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "3"]
