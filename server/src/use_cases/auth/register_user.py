from use_cases.dtos import IssuedTokens
from use_cases.exceptions import UsernameConflict
from use_cases.ports import PasswordHasher, TokenIssuer, UserRepository


class RegisterUser:
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
        if await self._users.get_by_username(username) is not None:
            raise UsernameConflict()
        user = await self._users.create(username, self._passwords.hash(password))
        # Registration signs the new user straight in, so return a token pair
        # exactly like AuthenticateUser does.
        return IssuedTokens(
            access=self._tokens.access_token(user.id),
            refresh=self._tokens.refresh_token(user.id),
        )
