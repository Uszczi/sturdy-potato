from datetime import timedelta
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# Repository root (server/config.py -> server -> repo root).
BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    """Application settings, overridable via environment variables."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # SQLAlchemy async URL. Defaults to the SQLite file at the repo root.
    database_url: str = f"sqlite+aiosqlite:///{BASE_DIR / 'db.sqlite3'}"

    # Signing key for the JWT access/refresh tokens. Override in production.
    secret_key: str = "insecure-dev-secret-change-me-with-a-long-random-value"

    # Token lifetimes mirror the previous SimpleJWT configuration so the SPA's
    # refresh cadence is unchanged.
    access_token_lifetime: timedelta = timedelta(minutes=15)
    refresh_token_lifetime: timedelta = timedelta(days=7)

    # Browser origins allowed to call the API cross-origin (the Vite dev/preview
    # server for the React SPA). Comma-separated in the environment via
    # CORS_ORIGINS.
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"

    @property
    def cors_allowed_origins(self) -> list[str]:
        return [
            origin.strip() for origin in self.cors_origins.split(",") if origin.strip()
        ]


settings = Settings()
