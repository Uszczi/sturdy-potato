from config import Settings


def test_cors_allowed_origins_splits_and_strips_blanks() -> None:
    settings = Settings(cors_origins="http://a, http://b ,")

    assert settings.cors_allowed_origins == ["http://a", "http://b"]
