"""Concrete security services: password hashing and JWT issuing.

These implement the ``PasswordHasher`` and ``TokenIssuer`` ports the auth use
cases depend on. All the pwdlib/pyjwt specifics live here so the use-case layer
stays free of them.
"""

from datetime import UTC, datetime, timedelta
from typing import Any

import jwt
from asyncer import asyncify
from pwdlib import PasswordHash

from config import settings
from use_cases.exceptions import InvalidToken

_ALGORITHM = "HS256"
_ACCESS = "access"
_REFRESH = "refresh"


class Argon2PasswordHasher:
    def __init__(self) -> None:
        self._hasher = PasswordHash.recommended()

    def hash(self, password: str) -> str:
        return self._hasher.hash(password)

    async def verify(self, password: str, hashed_password: str) -> bool:
        # Argon2 verification is CPU-bound; keep it off the event loop.
        return await asyncify(self._hasher.verify)(password, hashed_password)


class JwtTokenService:
    def _create(self, user_id: int, token_type: str, lifetime: timedelta) -> str:
        now = datetime.now(UTC)
        payload = {
            "user_id": user_id,
            "token_type": token_type,
            "iat": now,
            "exp": now + lifetime,
        }
        return jwt.encode(payload, settings.secret_key, algorithm=_ALGORITHM)

    def access_token(self, user_id: int) -> str:
        return self._create(user_id, _ACCESS, settings.access_token_lifetime)

    def refresh_token(self, user_id: int) -> str:
        return self._create(user_id, _REFRESH, settings.refresh_token_lifetime)

    def _user_id(self, token: str, expected_type: str) -> int:
        try:
            payload: dict[str, Any] = jwt.decode(
                token, settings.secret_key, algorithms=[_ALGORITHM]
            )
        except jwt.PyJWTError:
            raise InvalidToken() from None
        if payload.get("token_type") != expected_type:
            raise InvalidToken()
        user_id = payload.get("user_id")
        if not isinstance(user_id, int):
            raise InvalidToken()
        return user_id

    def user_id_from_access(self, token: str) -> int:
        return self._user_id(token, _ACCESS)

    def user_id_from_refresh(self, token: str) -> int:
        return self._user_id(token, _REFRESH)


password_hasher = Argon2PasswordHasher()
token_service = JwtTokenService()
