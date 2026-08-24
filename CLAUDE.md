# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository shape

A uv workspace (`server`, `mcp`) plus a Vite/React SPA in `client/` and an Aspire
apphost that runs the whole stack. `README.md` covers running the app; `CONTEXT.md`
is the domain glossary (use its vocabulary — Workspace, Project, Task, Workflow,
Status, Board, Column — and avoid the synonyms it lists); `docs/adr/` holds design
decisions; `AGENTS.md` points at `docs/agents/` for issue-tracker and triage
conventions (issues live in GitHub `Uszczi/sturdy-potato`, managed with `gh`).

## Commands

Everything runs through `just` (see `Justfile`). `just all` = `lint test e2e`.

```bash
just start                  # Aspire: postgres + redis + migrations + server + vite client
just db / just redis        # standalone containers if not using Aspire
just run                    # fastapi dev, http://localhost:8000, docs at /docs
just migrate / just makemigrations "msg" / just seed
just lint                   # ruff check --fix, ruff format, mypy (server only)
just lint-check             # non-mutating variant
just test                   # pytest, 100% coverage gate, -n auto
just client-lint            # oxlint
just client-build           # tsc -b && vite build
just e2e [args]             # playwright; `just e2e-install` once for chromium
```

Single test: `cd server && uv run pytest tests/use_cases/test_use_cases.py::test_name`
(no coverage gate outside `just test`; `pythonpath=["src"]` and `asyncio_mode=auto`
come from `server/pyproject.toml`).
Single e2e spec: `just e2e e2e/kanban.spec.ts -g "pattern"`.

`just test` starts throwaway PostgreSQL and Redis via testcontainers, so a Docker
daemon must be running. `just e2e` boots its own isolated API + freshly seeded
database on non-default ports (`client/e2e/scripts/serve.sh`), also via Docker.

mypy runs `--strict` over the server; `just lint` does not cover `mcp/` or the
client. Alembic always needs its config path: `-c src/infrastructure/alembic/alembic.ini`.

## Server architecture (`server/src`)

Ports-and-adapters, in three layers, with the dependency arrow pointing inward:

- `api/routes/` — HTTP only. Routes parse `schemas/` input, call one use case, and
  serialize the returned entity. `api/dependencies.py` wires every use case; each
  `_use_case(lambda uow: ...)` names the repositories that use case needs.
- `use_cases/` — the business logic, framework-free. It defines its own
  `entities.py`, `dtos.py`, `exceptions.py` and `ports.py` (repository Protocols)
  and **must not import** `infrastructure`, FastAPI, SQLModel or `schemas`.
- `infrastructure/` — SQLAlchemy repositories implementing the ports, plus db,
  cache, security, rate limiting, admin, Alembic and the Ollama/MCP client.

`UnitOfWork` (`infrastructure/unit_of_work.py`) owns the transaction: repositories
flush but never commit, and the request-scoped `get_unit_of_work` dependency
commits once (or rolls back). Use cases raise `UseCaseError` subclasses; a single
handler in `main.py` maps them to HTTP responses, so routes contain no error
mapping and no `HTTPException`.

Because ports are Protocols, use cases are tested against `tests/fakes.py`
(in-memory repositories) with no database or app; `tests/api/routes/` exercises the
real stack against testcontainers.

Flat "src as root" layout: imports are top-level (`from use_cases.tasks import ...`,
not `from src...`). That is deliberate — `hatch` maps `src/` to the wheel root so
the `mcp` workspace member can import the use-case layer in-process.

### Domain invariants worth knowing before touching tasks

- Which statuses exist is **per board**: a project owns its Workflow (copied from
  the workspace default at creation, edited independently after); the inbox uses
  the workspace's Workflow. So a status key alone never tells you whether a task
  is finished.
- `Task.is_done` is denormalised (ADR-0001) and `status` is the source of truth.
  Never write a status without a `StatusAssignment` (key + done-ness) — that pairing
  is what keeps the two in step. Four write paths maintain it: task create, status
  change, project change, and a workflow edit that changes terminal-ness.
- Task routes are nested under `/api/workspaces/{workspace_id}/...`; the
  `WorkspaceId` dependency in `auth.py` does the membership check.

## MCP server (`mcp/`)

`potato-mcp` exposes the task tools over streamable HTTP (`just mcp`) or stdio
(`just mcp-stdio`). Tools are thin adapters over the *same* use cases the REST API
uses — no duplicated logic — running inside `acting_context()`, which supplies the
transaction, caller and workspace from request headers (or `MCP_ACCESS_TOKEN` /
`MCP_WORKSPACE_ID` under stdio). It needs the same Postgres and matching
`SECRET_KEY`/`DATABASE_URL` as the API.

The `/api/workspaces/{id}/chat/` route streams SSE: it forwards the caller's bearer
token to the MCP server, so the model's tool calls are scoped to exactly what that
user could do. `just chat` is a terminal client for the same loop.

## Client (`client/`)

React 19 + TanStack Router (file-based routes, `routeTree.gen.ts` is generated) +
zustand + Tailwind 4/daisyUI, drag-and-drop via `@dnd-kit/react`.

`client/api-client/` is **generated** from the running server's OpenAPI schema —
never hand-edit it. Regenerate with `just generate-api-client` while the API is up;
it wipes the directory first. Generated method names come from the routes'
explicit `operation_id`s, so changing one renames a client method.

`src/api.ts` uses an empty base path: same-origin in production (FastAPI serves the
built SPA), and in dev the Vite proxy forwards `/api` to `127.0.0.1:8000`. The
zustand store (`src/stores/app-store.ts`) caches tasks and workflows per board
(`boardKey(projectId)`, `"inbox"` for `null`), loading and refetching one board at
a time rather than the whole task list.

## Conventions

- Comments in this codebase explain *why*, not what, and are dense around
  non-obvious decisions. Match that when editing.
- The 100% coverage gate is real: new server code needs tests in the same change.
- Add an ADR under `docs/adr/` for decisions that constrain future work, and extend
  `CONTEXT.md` when you introduce a domain term.
