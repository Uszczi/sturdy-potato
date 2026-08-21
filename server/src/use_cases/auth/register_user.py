from use_cases.dtos import IssuedTokens
from use_cases.exceptions import UsernameConflict
from use_cases.ports import (
    PasswordHasher,
    TokenIssuer,
    UserRepository,
    WorkspaceRepository,
)

# Name of the workspace every new user gets to hold their own data.
PERSONAL_WORKSPACE_NAME = "Personal"


class RegisterUser:
    def __init__(
        self,
        users: UserRepository,
        workspaces: WorkspaceRepository,
        passwords: PasswordHasher,
        tokens: TokenIssuer,
    ) -> None:
        self._users = users
        self._workspaces = workspaces
        self._passwords = passwords
        self._tokens = tokens

    async def execute(self, username: str, password: str) -> IssuedTokens:
        if await self._users.get_by_username(username) is not None:
            raise UsernameConflict()
        user = await self._users.create(username, self._passwords.hash(password))
        # Every user starts with a personal workspace that owns their projects,
        # tasks and comments; membership is what grants access.
        await self._workspaces.create(
            user.id, PERSONAL_WORKSPACE_NAME, is_personal=True
        )
        # Registration signs the new user straight in, so return a token pair
        # exactly like AuthenticateUser does.
        return IssuedTokens(
            access=self._tokens.access_token(user.id),
            refresh=self._tokens.refresh_token(user.id),
        )
