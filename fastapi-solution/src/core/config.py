from pydantic import BaseSettings


class Settings(BaseSettings):
    """Base config."""

    SERVICE_NAME: str = "Movies api"

    # Настройки Redis
    REDIS_HOST: str = "127.0.0.1"
    REDIS_PORT: int = 6379

    # Настройки Elasticsearch
    ELASTIC_HOST: str = "127.0.0.1"
    ELASTIC_PORT: int = 9200

    # Хранилище логов
    LOGSTASH_HOST: str = "127.0.0.1"
    LOGSTASH_PORT: int = 5044

    # Auth endpoint
    AUTH_SERVICE: str = "http://127.0.0.1:8000/auth_api/v1/auth/check_roles"

    # Sentry
    MOVIES_SENTRY_SDK: str = "https://82ccca49e570413f8cb6aa3424d2af34@o1336827.ingest.sentry.io/6613101"

    ENV: str = 'dev'

    INNER_KEY: str = "0278de20ad6c15ea833ee44325de905d9f7c0de8"

    class Config:
        """Settings config."""

        env_prefix = ""
        case_sensitive = False
