from pydantic import BaseSettings


class Settings(BaseSettings):

    # Rabbit
    RABBIT_HOST: str = "127.0.0.1"
    RABBIT_PORT: int = 5672
    RABBIT_USER: str = "guest"
    RABBIT_PASSWORD: str = "guest"
    QUEUE_NAME: str = "email"

    # Auth service
    AUTH_SERVICE: str = "http://127.0.0.1:8001/auth_api/v1"

    # Templates service
    TEMPLATES_SERVICE: str = "http://127.0.0.1:8000/tasks_admin_api/v1"

    INNER_KEY: str = "0278de20ad6c15ea833ee44325de905d9f7c0de8"

    # Email confid
    SENDER_USER: str = "practixtestaccount@yandex.ru"
    SENDER_PASSWORD: str = 'rvwecqspkzsydvsx'
    SENDER_EMAIL_SERVER: str = 'smtp.yandex.com:465'

    ENV: str = 'dev'

    class Config:
        """Settings config."""

        env_prefix = ""
        case_sensitive = False
