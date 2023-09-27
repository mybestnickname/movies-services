from functools import lru_cache

from pydantic import BaseSettings


class RecsysSettings(BaseSettings):
    train_n_epochs: int = 10
    n_recommendations_predict: int = 10

    class Config:
        env_prefix = 'RECSYS_'


class StorageSettings(BaseSettings):
    file_storage_path: str = ''


class UGCSettings(BaseSettings):
    host: str = '127.0.0.1'
    port: int = 8000
    scores_endpoint: str = 'ugcservice_api/v1/users_likes/get_likes'

    class Config:
        env_prefix = 'UGC_'


class RecsysAPISettings(BaseSettings):
    host: str = '127.0.0.1'
    port: int = 8000
    recs_endpoint: str = 'recservice_api/v1/new_rec'


class Settings(BaseSettings):
    recsys: RecsysSettings = RecsysSettings()
    storage: StorageSettings = StorageSettings()
    ugc: UGCSettings = UGCSettings()
    recapi: RecsysAPISettings = RecsysAPISettings()
    inner_key: str 


@lru_cache()
def get_settings() -> Settings:
    return Settings()
