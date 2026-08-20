import hashlib
import hmac
from datetime import timedelta
from pathlib import Path
from typing import Self

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent

# The default secret is fine for local dev but must never sign tokens in
# production, where anyone reading the source could forge them.
INSECURE_SECRET_KEY = "insecure-dev-secret-change-me-with-a-long-random-value"

# The only environments allowed to run with the insecure default secret. Any
# other value (``production``, ``prod``, ``staging``, a typo, …) is treated as a
# real deployment and must supply a strong key: the check fails closed so a
# misspelled ENVIRONMENT can't silently ship forgeable tokens.
DEV_ENVIRONMENTS = frozenset({"development", "test"})


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Deployments set ENVIRONMENT to anything outside DEV_ENVIRONMENTS (e.g.
    # "production"); that gates both the secret-key check and the admin panel.
    environment: str = "development"

    database_url: str = (
        "postgresql+asyncpg://postgres:postgres@localhost:5432/sturdy_potato"
    )

    redis_url: str = "redis://localhost:6379/0"

    secret_key: str = INSECURE_SECRET_KEY

    access_token_lifetime: timedelta = timedelta(minutes=15)
    refresh_token_lifetime: timedelta = timedelta(days=7)

    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"

    # The SQLAdmin database UI is a powerful, full-table editor. It is off by
    # default and must be explicitly enabled (behind staff login) per deployment
    # so it is never exposed just by shipping the image.
    admin_enabled: bool = False

    # Built SPA assets. Present in the production image; absent in local dev
    # (Vite serves the client), where main.py skips mounting it.
    frontend_dir: Path = BASE_DIR / "client-dist"

    @property
    def is_development(self) -> bool:
        return self.environment in DEV_ENVIRONMENTS

    @property
    def cors_allowed_origins(self) -> list[str]:
        return [
            origin.strip() for origin in self.cors_origins.split(",") if origin.strip()
        ]

    @property
    def admin_session_secret(self) -> str:
        # Derive a distinct key for the admin session cookie so it never shares
        # signing material with the JWTs; a leak of one must not forge the other.
        return hmac.new(
            self.secret_key.encode(), b"admin-session", hashlib.sha256
        ).hexdigest()

    @model_validator(mode="after")
    def _require_secure_secret_outside_dev(self) -> Self:
        # Fail fast at startup rather than silently signing forgeable tokens.
        # Fails closed: anything but a known dev environment needs a real key.
        if not self.is_development and self.secret_key == INSECURE_SECRET_KEY:
            raise ValueError(
                "SECRET_KEY must be set to a strong, non-default value when "
                f"ENVIRONMENT is not one of {sorted(DEV_ENVIRONMENTS)}."
            )
        return self


settings = Settings()
