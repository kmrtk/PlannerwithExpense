import pytest

from app.config import DEFAULT_JWT_SECRET, Settings


def test_settings_rejects_default_secret_in_production():
    with pytest.raises(ValueError):
        Settings(environment="production", jwt_secret=DEFAULT_JWT_SECRET)


def test_settings_allows_default_secret_in_development():
    settings = Settings(environment="development", jwt_secret=DEFAULT_JWT_SECRET)
    assert settings.jwt_secret == DEFAULT_JWT_SECRET


def test_settings_allows_custom_secret_in_production():
    settings = Settings(environment="production", jwt_secret="a-strong-unique-secret")
    assert settings.environment == "production"
