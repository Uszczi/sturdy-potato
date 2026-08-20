"""Request authentication for the API.

This module only wires the "who is the current user" dependency that protected
routes use. The actual decision lives in the ``GetCurrentUser`` use case, typed
against the repository and token ports; the JWT and password machinery lives in
``infrastructure.security``. Failures raise the domain ``InvalidToken`` error,
which the app's exception handler maps to a 401 (with ``WWW-Authenticate``), so
authentication shares the single error path used by every other use case.
"""

from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from infrastructure.db import SessionDep
from infrastructure.repositories import UserRepository
from infrastructure.security import token_service
from use_cases.auth import GetCurrentUser
from use_cases.entities import User
from use_cases.exceptions import InvalidToken

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


async def get_current_user_id(user: CurrentUser) -> int:
    return user.id


CurrentUserId = Annotated[int, Depends(get_current_user_id)]
