from fastapi import APIRouter, Depends, status

from api.dependencies import RegisterUserDep
from infrastructure.rate_limit import rate_limit_login
from schemas.auth import TokenPair, UserRegister

# Account creation is an unauthenticated, abuse-prone endpoint, so it shares the
# per-client throttle that guards login/refresh.
router = APIRouter(
    prefix="/register",
    tags=["api"],
    dependencies=[Depends(rate_limit_login)],
)


@router.post(
    "/", status_code=status.HTTP_201_CREATED, operation_id="api_register_create"
)
async def register(body: UserRegister, use_case: RegisterUserDep) -> TokenPair:
    tokens = await use_case.execute(body.username, body.password)
    return TokenPair(access=tokens.access, refresh=tokens.refresh)
