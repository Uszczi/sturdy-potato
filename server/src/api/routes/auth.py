from fastapi import APIRouter

from api.dependencies import AuthenticateUserDep, RefreshAccessTokenDep
from schemas.auth import (
    AccessToken,
    TokenObtainPair,
    TokenPair,
    TokenRefresh,
)

router = APIRouter(prefix="/token", tags=["api"])


@router.post("/", operation_id="api_token_create")
async def obtain_token(
    body: TokenObtainPair, use_case: AuthenticateUserDep
) -> TokenPair:
    tokens = await use_case.execute(body.username, body.password)
    return TokenPair(access=tokens.access, refresh=tokens.refresh)


@router.post("/refresh/", operation_id="api_token_refresh_create")
async def refresh_token(
    body: TokenRefresh, use_case: RefreshAccessTokenDep
) -> AccessToken:
    return AccessToken(access=use_case.execute(body.refresh))
