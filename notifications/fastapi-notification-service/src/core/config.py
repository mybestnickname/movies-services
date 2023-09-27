import os

from pydantic import BaseSettings


class Settings(BaseSettings):
    """Base config."""

    SERVICE_NAME: str = "Notification Service"

    RABBIT_HOST: str = 'rabbit1'
    RABBIT_PORT: int = 5672
    RABBIT_USER: str = "guest"
    RABBIT_PASSWORD: str = "guest"

    ENV: str = "test"
    # Хранилище логов
    LOGSTASH_HOST: str = "127.0.0.1"
    LOGSTASH_PORT: int = 5044

    # Sentry
    UGC_SENTRY_SDK: str = "https://23bffcc868094cddaddc0c49a836bce7@o1336827.ingest.sentry.io/6613121"

    ENV: str = "dev"

    class Config:
        """Settings config."""

        env_prefix = ""
        case_sensitive = False
