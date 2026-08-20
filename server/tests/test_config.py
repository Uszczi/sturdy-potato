import pytest

from config import INSECURE_SECRET_KEY, Settings


def test_cors_allowed_origins_splits_and_strips_blanks() -> None:
    settings = Settings(cors_origins="http://a, http://b ,")

    assert settings.cors_allowed_origins == ["http://a", "http://b"]


def test_production_rejects_the_default_secret_key() -> None:
    with pytest.raises(ValueError, match="SECRET_KEY"):
        Settings(environment="production", secret_key=INSECURE_SECRET_KEY)


def test_production_accepts_a_custom_secret_key() -> None:
    settings = Settings(environment="production", secret_key="a-real-long-secret")

    assert settings.secret_key == "a-real-long-secret"


def test_development_allows_the_default_secret_key() -> None:
    settings = Settings(environment="development", secret_key=INSECURE_SECRET_KEY)

    assert settings.secret_key == INSECURE_SECRET_KEY
