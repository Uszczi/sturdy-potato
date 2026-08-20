from fastapi import APIRouter, Depends

from api.dependencies import AuthenticateUserDep, RefreshAccessTokenDep
from infrastructure.rate_limit import rate_limit_login
from schemas.auth import (
    AccessToken,
    TokenObtainPair,
    TokenPair,
    TokenRefresh,
)

# Both endpoints are unauthenticated guessing targets, so every request first
# passes the per-client rate limiter.
router = APIRouter(
    prefix="/token",
    tags=["api"],
    dependencies=[Depends(rate_limit_login)],
)


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
    return AccessToken(access=await use_case.execute(body.refresh))
