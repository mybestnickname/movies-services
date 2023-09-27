from pydantic import BaseSettings


class Settings(BaseSettings):
    """Base config."""

    SERVICE_NAME: str = "Rec service api"

    # Настройки Redis
    REC_REDIS_HOST: str = "127.0.0.1"
    REC_REDIS_PORT: int = 6379

    # Auth endpoint
    AUTH_SERVICE: str = "http://127.0.0.1:8000/auth_api/v1/auth/check_roles"

    ENV: str = 'dev'

    INNER_KEY: str = "0278de20ad6c15ea833ee44325de905d9f7c0de8"

    # Movies endpoint
    MOVIES_SERVICE: str = "http://127.0.0.1:8001/movies_api/v1/"

    class Config:
        """Settings config."""

        env_prefix = ""
        case_sensitive = False
