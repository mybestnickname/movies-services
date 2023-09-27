"""Flask configuration."""
from typing import Optional

from pydantic import BaseSettings, Field


class Config(BaseSettings):
    """Base config."""
    SERVICE_NAME: str = "Auth api"

    SECRET_KEY: Optional[str] = 'app top secret'
    SESSION_COOKIE_NAME: Optional[str] = 'session cookie name'

    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False
    SQLALCHEMY_DATABASE_URI: str = Field(
        default="postgresql://app:123qwe@127.0.0.1:5432/auth_database",
        env="DATABASE_URI"
    )

    JWT_SECRET_KEY: str = "super-secret"
    JWT_ACCESS_TOKEN_EXPIRES: int = 3600
    JWT_REFRESH_TOKEN_EXPIRES: int = 30  # sec
    JWT_REFRESH_TOKEN_EXPIRES: int = 864000  # sec

    REQUESTS_LIMITER: list = Field(
        default=["4000 per day", "300/hour"],
        env="REQUESTS_LIMITER"
    )

    JAEGER_PORT: int = 6831
    JAEGER_HOST: str = "localhost"

    # Хранилище логов
    LOGSTASH_HOST: str = "127.0.0.1"
    LOGSTASH_PORT: int = 5044

    # Sentry
    AUTH_SENTRY_SDK: str = "https://024df985bfe341f381b2108e554d978d@o1336827.ingest.sentry.io/6613119"

    class Config:
        env_prefix = ""
        case_sensitive = False


class ProdConfig(Config):
    ENV: str = "production"
    DEBUG: bool = False
    TESTING: bool = False


class DevConfig(Config):
    ENV: str = "development"
    DEBUG: bool = True
    TESTING: bool = True


class TestConfig(Config):
    ENV: str = "test"
    DEBUG: bool = True
    TESTING: bool = True

    SQLALCHEMY_DATABASE_URI: str = Field(
        default="postgresql://app:123qwe@127.0.0.1:5432/auth_database_test",
        env="TEST_DATABASE_URI"
    )


config = {
    'dev': DevConfig(),
    'prod': ProdConfig(),
    'test': TestConfig(),
    'default': DevConfig(),
}
