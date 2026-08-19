from datetime import timedelta
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = f"sqlite+aiosqlite:///{BASE_DIR / 'db.sqlite3'}"

    secret_key: str = "insecure-dev-secret-change-me-with-a-long-random-value"

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


settings = Settings()
