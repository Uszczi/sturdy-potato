# The MCP server: exposes the task tools over HTTP (http://<host>:8001/mcp).
#
# Built from the repo root so it can use the uv *workspace* (root pyproject.toml
# + root uv.lock). Like the API image, it installs only third-party deps into the
# venv and provides the first-party packages as source on PYTHONPATH — here BOTH
# the MCP package and the server's use-case layer it reuses in-process.
FROM python:3.13-slim-bookworm AS python-dependencies

COPY --from=ghcr.io/astral-sh/uv:0.11.19 /uv /uvx /bin/

WORKDIR /app

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

# Resolve from the frozen workspace lock. --no-install-workspace installs every
# member's dependencies (fastmcp, fastapi, sqlalchemy, ...) but not the member
# packages themselves; those come in as source below. The member pyproject files
# are needed for uv to see the workspace layout.
COPY pyproject.toml uv.lock ./
COPY server/pyproject.toml ./server/pyproject.toml
COPY mcp/pyproject.toml ./mcp/pyproject.toml
RUN uv sync --frozen --no-dev --no-install-workspace


FROM python:3.13-slim-bookworm

WORKDIR /app

ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/src \
    MCP_TRANSPORT=http \
    MCP_HOST=0.0.0.0 \
    MCP_PORT=8001

COPY --from=python-dependencies /app/.venv /app/.venv

# The MCP server reuses the server's use_cases/infrastructure/config in-process,
# so both source trees sit side by side on PYTHONPATH (/app/src).
COPY server/src ./src
COPY mcp/src/potato_mcp ./src/potato_mcp

EXPOSE 8001

CMD ["python", "-m", "potato_mcp"]
