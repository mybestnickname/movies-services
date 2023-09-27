import logging
from asyncio.log import logger
from functools import lru_cache
from typing import Optional, Union

from api.errors.httperrors import StorageInternalError
from db.mongo import get_mongo
from fastapi import Depends
from motor.motor_asyncio import AsyncIOMotorClient
from pkg.storage.storage import ABSStorage
from pymongo import ReturnDocument

logger = logging.getLogger(__name__)


class MongoService(ABSStorage):
    def __init__(self, mongo: AsyncIOMotorClient) -> None:
        self.mongo = mongo

    async def create_or_update_in_ugc_storage(
            self,
            database: str,
            collection: str,
            filter_query: dict,
            ugc_data: dict
    ) -> Optional[dict]:
        """Send ugc data to mongo collection."""
        collection = self.mongo[f"{database}"][f"{collection}"]
        try:
            result_doc = await collection.find_one_and_update(
                filter=filter_query,
                update={'$set': ugc_data},
                upsert=True,
                return_document=ReturnDocument.AFTER
            )
        except Exception:
            logger.exception(f"Failed to send data to Mongo {database} {collection} {ugc_data}.")
            raise StorageInternalError
        return result_doc

    async def get_ugc_from_storage(
            self,
            database: str,
            collection: str,
            query: dict
    ) -> Union[dict, None]:
        """Read ugc data from mongo collection."""
        try:
            collection = self.mongo[f"{database}"][f"{collection}"]
            result = await collection.find_one(query)
        except Exception:
            logger.exception(f"Failed to get data from Mongo {database} {collection} {query}.")
            return None
        return result

    async def delete_ugc_from_storage(
            self,
            database: str,
            collection: str,
            query: dict
    ) -> Optional[bool]:
        """Delete ugc data from mongo collection."""
        collection = self.mongo[f"{database}"][f"{collection}"]
        try:
            if await collection.find_one_and_delete(query):
                return True
            return False
        except Exception:
            logger.exception(f"Failed to get data from Mongo {database} {collection} {query}.")
            raise StorageInternalError

    async def send_to_ugc_storage(
            self,
            database: str,
            collection: str,
            ugc_data: dict
    ) -> Optional[str]:
        """Create new doc in mongo collection."""
        collection = self.mongo[f"{database}"][f"{collection}"]
        try:
            result = await collection.insert_one(ugc_data)
        except Exception:
            logger.exception(f"Failed to send data to Mongo {database} {collection} {ugc_data}.")
            raise StorageInternalError
        return result.inserted_id

    async def get_ugc_count_in_storage(
            self,
            database: str,
            collection: str,
            filter_query: dict
    ):
        """Get filtered documents count."""
        collection = self.mongo[f"{database}"][f"{collection}"]
        try:
            doc_count = await collection.count_documents(filter_query)
        except Exception:
            logger.exception(f"Failed to count docs to Mongo {database} {collection} {filter_query}.")
            raise StorageInternalError
        return doc_count

    async def get_ugc_data_chunks(
            self,
            database: str,
            collection: str,
            per_page: int,
            offset: int,
            query: dict,
            sort_field: Optional[str] = None,
    ) -> Optional[list]:
        """Read another ugc data chunk from mongo collection."""
        collection = self.mongo[f"{database}"][f"{collection}"]
        try:
            documents = (collection.find(filter=query, skip=offset, limit=per_page))
            if sort_field:
                documents = documents.sort(sort_field)
        except Exception:
            logger.exception(f"Failed to get data from Mongo {database} {collection} {query}.")
            raise StorageInternalError
        return [row async for row in documents]

    async def get_avg_ugc_data(
            self,
            database: str,
            collection: str,
            query: dict,
            per_page: int = 1,
            offset: int = 0
    ) -> Optional[list]:
        """Read avg value from mongo collection."""
        collection = self.mongo[f"{database}"][f"{collection}"]
        try:
            agg_res_list = [row async for row in collection.aggregate(query)]
        except Exception:
            logger.exception(f"Failed to get avg value from Mongo {database} {collection} {query}.")
            raise StorageInternalError
        return agg_res_list


@lru_cache()
def get_mongo_storage_service(
        mongo: AsyncIOMotorClient = Depends(get_mongo),
) -> MongoService:
    return MongoService(mongo)
