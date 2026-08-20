from use_cases.exceptions import InvalidToken
from use_cases.ports import TokenIssuer, UserRepository


class RefreshAccessToken:
    def __init__(self, users: UserRepository, tokens: TokenIssuer) -> None:
        self._users = users
        self._tokens = tokens

    async def execute(self, refresh_token: str) -> str:
        # Raises InvalidToken if the refresh token is missing/expired/wrong type.
        user_id = self._tokens.user_id_from_refresh(refresh_token)
        # Re-check the account on every refresh: a deleted or deactivated user
        # must not keep minting access tokens for the refresh token's lifetime.
        user = await self._users.get_by_id(user_id)
        if user is None or not user.is_active:
            raise InvalidToken()
        return self._tokens.access_token(user.id)
