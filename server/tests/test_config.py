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


@pytest.mark.parametrize("environment", ["prod", "staging", "Production", "prd"])
def test_non_dev_environments_reject_the_default_secret_key(environment: str) -> None:
    # The guard fails closed: anything but a known dev environment (a typo, an
    # abbreviation, a different stage) must supply a strong key.
    with pytest.raises(ValueError, match="SECRET_KEY"):
        Settings(environment=environment, secret_key=INSECURE_SECRET_KEY)


def test_test_environment_allows_the_default_secret_key() -> None:
    settings = Settings(environment="test", secret_key=INSECURE_SECRET_KEY)

    assert settings.is_development is True


def test_admin_session_secret_is_derived_and_distinct() -> None:
    settings = Settings(secret_key="a-real-long-secret")

    # Never the raw signing key, but stable for a given key.
    assert settings.admin_session_secret != settings.secret_key
    assert (
        settings.admin_session_secret
        == Settings(secret_key="a-real-long-secret").admin_session_secret
    )
