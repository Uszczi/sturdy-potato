from use_cases.ports import TokenIssuer


class RefreshAccessToken:
    def __init__(self, tokens: TokenIssuer) -> None:
        self._tokens = tokens

    def execute(self, refresh_token: str) -> str:
        # Raises InvalidToken if the refresh token is missing/expired/wrong type.
        user_id = self._tokens.user_id_from_refresh(refresh_token)
        return self._tokens.access_token(user_id)
