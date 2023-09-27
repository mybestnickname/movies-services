from functools import lru_cache
from typing import Dict, List

from pymongo import InsertOne, MongoClient

from core.settings import Settings, get_settings


class MongoLoader:
    def __init__(self, settings: Settings) -> None:
        self.client = MongoClient(settings.mongo.host, settings.mongo.port)

    def insert_data_batched(self, db: str, collection: str, data: List[Dict]) -> None:
        mongo_collection = self.client[f'{db}'][f'{collection}']
        query = [InsertOne(sample) for sample in data]
        result = mongo_collection.bulk_write(query)
        return result


@lru_cache()
def get_mongo_loader() -> MongoLoader:
    return MongoLoader(settings=get_settings())
