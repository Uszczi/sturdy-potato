from datetime import timedelta
from pathlib import Path
from typing import Self

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent

# The default secret is fine for local dev but must never sign tokens in
# production, where anyone reading the source could forge them.
INSECURE_SECRET_KEY = "insecure-dev-secret-change-me-with-a-long-random-value"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Set ENVIRONMENT=production in deployments; this gates the secret-key check.
    environment: str = "development"

    database_url: str = f"sqlite+aiosqlite:///{BASE_DIR / 'db.sqlite3'}"

    secret_key: str = INSECURE_SECRET_KEY

    access_token_lifetime: timedelta = timedelta(minutes=15)
    refresh_token_lifetime: timedelta = timedelta(days=7)

    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"

    # Built SPA assets. Present in the production image; absent in local dev
    # (Vite serves the client), where main.py skips mounting it.
    frontend_dir: Path = BASE_DIR / "client-dist"

    @property
    def cors_allowed_origins(self) -> list[str]:
        return [
            origin.strip() for origin in self.cors_origins.split(",") if origin.strip()
        ]

    @model_validator(mode="after")
    def _require_secure_secret_in_production(self) -> Self:
        # Fail fast at startup rather than silently signing forgeable tokens.
        if self.environment == "production" and self.secret_key == INSECURE_SECRET_KEY:
            raise ValueError(
                "SECRET_KEY must be set to a strong, non-default value when "
                "ENVIRONMENT=production."
            )
        return self


settings = Settings()
