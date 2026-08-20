from use_cases.entities import User
from use_cases.exceptions import InvalidToken
from use_cases.ports import TokenIssuer, UserRepository


class GetCurrentUser:
    """Resolve the authenticated user for a request from its access token.

    This keeps the "who is calling" decision in the use-case layer, typed
    against the ports, instead of letting the web layer reach into the ORM and
    the concrete token service directly.
    """

    def __init__(self, users: UserRepository, tokens: TokenIssuer) -> None:
        self._users = users
        self._tokens = tokens

    async def execute(self, access_token: str) -> User:
        # Raises InvalidToken if the token is missing/expired/not an access token.
        user_id = self._tokens.user_id_from_access(access_token)
        user = await self._users.get_by_id(user_id)
        if user is None or not user.is_active:
            raise InvalidToken()
        return user
