from use_cases.dtos import IssuedTokens
from use_cases.exceptions import InvalidCredentials
from use_cases.ports import PasswordHasher, TokenIssuer, UserRepository


class AuthenticateUser:
    def __init__(
        self,
        users: UserRepository,
        passwords: PasswordHasher,
        tokens: TokenIssuer,
    ) -> None:
        self._users = users
        self._passwords = passwords
        self._tokens = tokens

    async def execute(self, username: str, password: str) -> IssuedTokens:
        user = await self._users.get_by_username(username)
        if (
            user is None
            or not user.is_active
            or not await self._passwords.verify(password, user.hashed_password)
        ):
            raise InvalidCredentials()
        return IssuedTokens(
            access=self._tokens.access_token(user.id),
            refresh=self._tokens.refresh_token(user.id),
        )
