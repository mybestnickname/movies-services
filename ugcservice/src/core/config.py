import os

from pydantic import BaseSettings


class Settings(BaseSettings):
    """Base config."""

    SERVICE_NAME: str = "UGC Service"

    KAFKA_HOST: str = "host.docker.internal"
    KAFKA_PORT: str = "9092"

    MONGO_HOST: str = os.getenv('MONGO_HOST', 'localhost')
    MONGO_PORT: int = os.getenv('MONGO_PORT', 27017)
    MONGO_DB: str = os.getenv('MONGO_DB', "UGC_DB")

    REDIS_LIMITER_HOST: str = os.getenv('REDIS_LIMITER_HOST', '127.0.0.1')
    REDIS_LIMITER_PORT: str = os.getenv('REDIS_LIMITER_PORT', '6379')

    AUTH_SERVICE = os.getenv('AUTH_SERVICE', 'http://127.0.0.1:8000/auth_api/v1/auth/check_roles')

    ENV: str = "test"
    # Хранилище логов
    LOGSTASH_HOST: str = "127.0.0.1"
    LOGSTASH_PORT: int = 5044

    # Sentry
    UGC_SENTRY_SDK: str = "https://23bffcc868094cddaddc0c49a836bce7@o1336827.ingest.sentry.io/6613121"

    ENV: str = "dev"

    # Общение внутр. сервисов.
    INNER_KEY: str = "0278de20ad6c15ea833ee44325de905d9f7c0de8"

    class Config:
        """Settings config."""

        env_prefix = ""
        case_sensitive = False
