from fastapi import APIRouter, HTTPException, status
from sqlmodel import select

from auth import (
    create_access_token,
    create_refresh_token,
    user_id_from_refresh,
    verify_password,
)
from db import SessionDep
from models import User
from schemas.auth import (
    AccessToken,
    TokenObtainPair,
    TokenPair,
    TokenRefresh,
)

router = APIRouter(prefix="/token", tags=["api"])

_invalid_credentials = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="No active account found with the given credentials.",
)


@router.post("/", operation_id="api_token_create")
async def obtain_token(body: TokenObtainPair, session: SessionDep) -> TokenPair:
    user = await session.scalar(select(User).where(User.username == body.username))
    if (
        user is None
        or not user.is_active
        or not verify_password(body.password, user.hashed_password)
    ):
        raise _invalid_credentials
    assert user.id is not None
    return TokenPair(
        access=create_access_token(user.id),
        refresh=create_refresh_token(user.id),
    )


@router.post("/refresh/", operation_id="api_token_refresh_create")
async def refresh_token(body: TokenRefresh) -> AccessToken:
    user_id = user_id_from_refresh(body.refresh)
    return AccessToken(access=create_access_token(user_id))
