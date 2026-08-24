"""Per-call acting context: resolve *who* and *where* for the caller.

The MCP server holds no session or logged-in user of its own. Every tool runs
inside :func:`acting_context`, which reproduces the API's two-step authorization:

- **User** from a bearer access token, via the same ``GetCurrentUser`` use case
  and ``token_service`` the REST API uses.
- **Workspace** from a workspace id, authorized against the caller's membership —
  read from the same ``X-Workspace-Id`` header the REST API takes it from.

Over HTTP these come from the ``Authorization: Bearer`` and ``X-Workspace-Id``
request headers. Over stdio there are no request headers, so they fall back to
the ``MCP_ACCESS_TOKEN`` and ``MCP_WORKSPACE_ID`` environment variables — letting
a client launch the process directly with credentials in its env.

It also owns the transaction boundary (open session, commit on success, roll back
on error), the same contract as the API's ``get_unit_of_work`` dependency.
"""

import os
from collections.abc import AsyncGenerator, Mapping
from contextlib import asynccontextmanager
from dataclasses import dataclass

from fastmcp.server.dependencies import get_http_headers
from infrastructure.db import async_session_maker
from infrastructure.repositories import UserRepository, WorkspaceRepository
from infrastructure.security import token_service
from infrastructure.unit_of_work import UnitOfWork
from use_cases.auth import GetCurrentUser
from use_cases.entities import User
from use_cases.exceptions import InvalidToken, WorkspaceNotFound

_WORKSPACE_HEADER = "x-workspace-id"
_ACCESS_TOKEN_ENV = "MCP_ACCESS_TOKEN"
_WORKSPACE_ENV = "MCP_WORKSPACE_ID"


@dataclass(frozen=True)
class ActingContext:
    """What a tool needs to act: the transaction, the caller, the workspace."""

    uow: UnitOfWork
    user: User
    workspace_id: int


def _bearer_token(headers: Mapping[str, str]) -> str:
    value = headers.get("authorization")
    if value and value.lower().startswith("bearer "):
        return value[len("bearer ") :].strip()
    # stdio transport carries no headers: fall back to the environment.
    env = os.getenv(_ACCESS_TOKEN_ENV)
    if env:
        return env.strip()
    # No credentials is the same failure as a bad token: an invalid caller.
    raise InvalidToken()


def _workspace_id(headers: Mapping[str, str]) -> int:
    raw = headers.get(_WORKSPACE_HEADER) or os.getenv(_WORKSPACE_ENV)
    if raw is None:
        raise WorkspaceNotFound(
            f"A workspace id is required "
            f"({_WORKSPACE_HEADER} header or {_WORKSPACE_ENV} env)."
        )
    try:
        return int(raw)
    except ValueError:
        raise WorkspaceNotFound("The workspace id must be an integer.") from None


@asynccontextmanager
async def acting_context() -> AsyncGenerator[ActingContext]:
    # include_all=True: FastMCP strips sensitive headers (Authorization, Cookie)
    # from the default view, but the bearer token is exactly what we need here.
    headers = get_http_headers(include_all=True)
    token = _bearer_token(headers)
    workspace_id = _workspace_id(headers)

    async with async_session_maker() as session:
        user = await GetCurrentUser(UserRepository(session), token_service).execute(
            token
        )
        # 404 (not 403) so membership never leaks a workspace's existence.
        if not await WorkspaceRepository(session).is_member(user.id, workspace_id):
            raise WorkspaceNotFound()

        uow = UnitOfWork(session)
        try:
            yield ActingContext(uow=uow, user=user, workspace_id=workspace_id)
            await uow.commit()
        except Exception:
            await uow.rollback()
            raise
