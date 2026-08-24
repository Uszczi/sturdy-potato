"""Request authentication for the API.

This module wires the "who is the current user" and "which workspace" dependencies
that protected routes use. The actual decision lives in the ``GetCurrentUser`` use case, typed
against the repository and token ports; the JWT and password machinery lives in
``infrastructure.security``. Failures raise the domain ``InvalidToken`` error,
which the app's exception handler maps to a 401 (with ``WWW-Authenticate``), so
authentication shares the single error path used by every other use case.
"""

from typing import Annotated

from fastapi import Depends, Header
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.db import SessionDep
from infrastructure.repositories import UserRepository, WorkspaceRepository
from infrastructure.security import token_service
from use_cases.auth import GetCurrentUser
from use_cases.entities import User
from use_cases.exceptions import InvalidToken, WorkspaceNotFound

# auto_error=False so a missing Authorization header reaches us as ``None`` and
# is reported as an InvalidToken (401), rather than the scheme's own 403.
_bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    session: SessionDep,
    credentials: Annotated[
        HTTPAuthorizationCredentials | None, Depends(_bearer_scheme)
    ],
) -> User:
    if credentials is None:
        raise InvalidToken()
    use_case = GetCurrentUser(UserRepository(session), token_service)
    return await use_case.execute(credentials.credentials)


CurrentUser = Annotated[User, Depends(get_current_user)]


async def get_access_token(
    credentials: Annotated[
        HTTPAuthorizationCredentials | None, Depends(_bearer_scheme)
    ],
) -> str:
    """The caller's raw bearer JWT, for forwarding to the MCP server.

    The chat route re-presents this token to the MCP server (which runs the task
    tools), so the model can only touch what the caller could. A missing token is
    the same InvalidToken (401) failure as everywhere else.
    """
    if credentials is None:
        raise InvalidToken()
    return credentials.credentials


AccessToken = Annotated[str, Depends(get_access_token)]


async def get_current_user_id(user: CurrentUser) -> int:
    return user.id


CurrentUserId = Annotated[int, Depends(get_current_user_id)]


WORKSPACE_HEADER = "X-Workspace-Id"


async def _authorized(user_id: int, workspace_id: int, session: AsyncSession) -> int:
    """Confirm membership, or 404.

    A non-member (or unknown workspace) 404s rather than 403s so membership never
    leaks a workspace's existence.
    """
    if not await WorkspaceRepository(session).is_member(user_id, workspace_id):
        raise WorkspaceNotFound()
    return workspace_id


async def get_workspace_id_from_path(
    workspace_id: int, user_id: CurrentUserId, session: SessionDep
) -> int:
    """Authorize the ``{workspace_id}`` path segment of the workspaces router."""
    return await _authorized(user_id, workspace_id, session)


async def get_current_workspace_id(
    user_id: CurrentUserId,
    session: SessionDep,
    workspace_id: Annotated[int | None, Header(alias=WORKSPACE_HEADER)] = None,
) -> int:
    """The workspace a resource route acts on, named by ``X-Workspace-Id``.

    Resource routes (tasks, projects, comments, chat) are not nested under the
    id: the caller selects the workspace out-of-band with a header, and omitting
    it means "my personal workspace" — the one registration mints — so a client
    that never switches workspaces does not have to resolve an id at all. The
    same header carries the choice to the MCP server, which reads it too.
    """
    if workspace_id is None:
        personal = await WorkspaceRepository(session).get_personal(user_id)
        if personal is None:
            # Every registered user owns one, so this only happens if it was
            # deleted out from under them.
            raise WorkspaceNotFound()
        return personal.id
    return await _authorized(user_id, workspace_id, session)


# The authorized workspace id for a resource route, from the header.
WorkspaceId = Annotated[int, Depends(get_current_workspace_id)]

# The authorized workspace id for a route that names one in its path.
PathWorkspaceId = Annotated[int, Depends(get_workspace_id_from_path)]
