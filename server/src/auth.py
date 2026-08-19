"""Request authentication for the API.

The JWT and password machinery lives in ``infrastructure.security``; this module
only wires the "who is the current user" dependency that protected routes use.
"""

from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from infrastructure.db import SessionDep
from infrastructure.models import User
from infrastructure.security import token_service
from use_cases.exceptions import InvalidToken

_bearer_scheme = HTTPBearer(auto_error=True)

_credentials_error = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Invalid or expired token.",
    headers={"WWW-Authenticate": "Bearer"},
)


async def get_current_user(
    session: SessionDep,
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(_bearer_scheme)],
) -> User:
    try:
        user_id = token_service.user_id_from_access(credentials.credentials)
    except InvalidToken:
        raise _credentials_error from None
    user = await session.get(User, user_id)
    if user is None or not user.is_active:
        raise _credentials_error
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


async def get_current_user_id(user: CurrentUser) -> int:
    assert user.id is not None
    return user.id


CurrentUserId = Annotated[int, Depends(get_current_user_id)]
