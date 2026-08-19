from datetime import UTC, datetime, timedelta
from typing import Annotated, Any

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pwdlib import PasswordHash

from config import settings
from infrastructure.db import SessionDep
from infrastructure.models import User

_password_hash = PasswordHash.recommended()

_ALGORITHM = "HS256"
_ACCESS = "access"
_REFRESH = "refresh"

_bearer_scheme = HTTPBearer(auto_error=True)

_credentials_error = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Invalid or expired token.",
    headers={"WWW-Authenticate": "Bearer"},
)


def hash_password(password: str) -> str:
    return _password_hash.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    return _password_hash.verify(password, hashed_password)


def _create_token(user_id: int, token_type: str, lifetime: timedelta) -> str:
    now = datetime.now(UTC)
    payload = {
        "user_id": user_id,
        "token_type": token_type,
        "iat": now,
        "exp": now + lifetime,
    }
    return jwt.encode(payload, settings.secret_key, algorithm=_ALGORITHM)


def create_access_token(user_id: int) -> str:
    return _create_token(user_id, _ACCESS, settings.access_token_lifetime)


def create_refresh_token(user_id: int) -> str:
    return _create_token(user_id, _REFRESH, settings.refresh_token_lifetime)


def _decode(token: str, expected_type: str) -> dict[str, Any]:
    try:
        payload: dict[str, Any] = jwt.decode(
            token, settings.secret_key, algorithms=[_ALGORITHM]
        )
    except jwt.PyJWTError:
        raise _credentials_error from None
    if payload.get("token_type") != expected_type:
        raise _credentials_error
    return payload


def user_id_from_refresh(token: str) -> int:
    payload = _decode(token, _REFRESH)
    user_id = payload.get("user_id")
    if not isinstance(user_id, int):
        raise _credentials_error
    return user_id


async def get_current_user(
    session: SessionDep,
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(_bearer_scheme)],
) -> User:
    payload = _decode(credentials.credentials, _ACCESS)
    user_id = payload.get("user_id")
    if not isinstance(user_id, int):
        raise _credentials_error
    user = await session.get(User, user_id)
    if user is None or not user.is_active:
        raise _credentials_error
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


async def get_current_user_id(user: CurrentUser) -> int:
    assert user.id is not None
    return user.id


CurrentUserId = Annotated[int, Depends(get_current_user_id)]
