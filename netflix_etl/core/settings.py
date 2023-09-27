from functools import lru_cache

from pydantic import BaseSettings


class MongoSettings(BaseSettings):
    host: str = 'localhost'
    port: int = 27017
    db_name: str = 'UGC_DB'
    scores_collection: str = 'FILM_RATINGS'

    class Config:
        env_prefix = 'MONGO_'


class DataSettings(BaseSettings):
    scores_csv_path: str
    movies_csv_path: str
    batch_size: int = 10000


class ElasticSearchSettings(BaseException):
    host: str = 'localhost'
    port: int = 9200
    movies_index = 'movies'

    class Config:
        env_prefix = 'ES_'


class Settings(BaseSettings):
    mongo: MongoSettings = MongoSettings()
    es: ElasticSearchSettings = ElasticSearchSettings()
    data: DataSettings = DataSettings()


@lru_cache()
def get_settings() -> Settings:
    return Settings()
