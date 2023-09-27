import datetime
import logging
from functools import lru_cache
import math
from typing import List
from fastapi import Depends

from api.errors.httperrors import (
    StorageInternalError,
    UserLikeHTTPNotFoundError
)
from api.v1.likes.models import GetUserLikeRespModel, GetLikesResponseModel
from pkg.cache_storage.redis_storage import get_redis_storage_service
from pkg.cache_storage.storage import ABSCacheStorage
from pkg.storage.mongo_storage import get_mongo_storage_service
from pkg.storage.storage import ABSStorage
from core.config import Settings

logger = logging.getLogger(__name__)

DATABASE = 'UGC_DB'
COLLECTION = 'FILM_RATINGS'


class LikesService:
    def __init__(self, mongo_storage: ABSStorage, cache_storage: ABSCacheStorage):
        self.mongo_storage = mongo_storage
        self.cache_storage = cache_storage

    async def save_user_like(
            self,
            movie_id: str,
            user_id: str,
            user_name: str,
            score: int
    ) -> None:
        """Send user like to storage."""
        try:
            logger.info(
                f"trying to save a user's rating for a movie, user: {user_id},film_id: {movie_id} from mongo db.")
            if await self.mongo_storage.create_or_update_in_ugc_storage(
                    database=Settings().MONGO_DB,
                    collection=COLLECTION,
                    filter_query={'user_id': user_id, 'movie_id': movie_id},
                    ugc_data={
                        'movie_id': movie_id,
                        'user_id': user_id,
                        'user_name': user_name,
                        'score': score,
                        'time_stamp': datetime.datetime.now(datetime.timezone.utc).isoformat()
                    }
            ):
                await self.cache_storage.delete_data(
                    key=f"user_likes_{user_id}_{movie_id}"
                )
                logger.info(
                    f"Successful to save a user's rating for a movie, user: {user_id},film_id: {movie_id} from mongo db.")
        except:
            logger.exception(
                f"Error to save a user's rating for a movie, user: {user_id},film_id: {movie_id} from mongo db.")
            raise StorageInternalError

    async def get_user_like(
            self,
            user_id: str,
            movie_id: str,
    ) -> GetUserLikeRespModel:
        """get user like from storage."""
        logger.info(
            f"Trying to get a user's rating for a movie, user: {user_id},film_id: {movie_id} from mongo db.")
        cashed_key = f"user_likes_{user_id}_{movie_id}"
        cashed_data = await self.cache_storage.get_data(key=cashed_key)
        if cashed_data:
            logger.info(
                f"like retrieved from cache movie_id: {movie_id}, user_id: {user_id}.")
            result = GetUserLikeRespModel.parse_raw(cashed_data)
            return result

        result = await self.mongo_storage.get_ugc_from_storage(
            database=Settings().MONGO_DB,
            collection=COLLECTION,
            query={
                'movie_id': movie_id,
                'user_id': user_id
            }
        )
        if result:
            user_like = GetUserLikeRespModel(**result)
            await self.cache_storage.set_data(
                key=cashed_key,
                data=user_like.json()
            )
            logger.info(
                f"like added to cache movie_id: {movie_id} user_id: {user_id}.")
            logger.info(
                f"Get a user's rating for a movie, user: {user_id},film_id: {movie_id} from mongo db.")
            return user_like
        logger.info(
            f"Error get a user's rating for a movie, user: {user_id},film_id: {movie_id} from mongo db.")
        raise UserLikeHTTPNotFoundError

    async def delete_user_like(
            self,
            user_id: str,
            movie_id: str,
    ) -> None:
        """get user like from storage."""
        logger.info(
            f"Trying to delete a user's rating for a movie, user: {user_id},film_id: {movie_id} from mongo db.")
        if await self.mongo_storage.delete_ugc_from_storage(
                database=Settings().MONGO_DB,
                collection=COLLECTION,
                query={
                    'user_id': str(user_id),
                    'movie_id': str(movie_id)
                }
        ):
            logger.info(
                f"Successful to delete a user's rating for a movie, user: {user_id},film_id: {movie_id} from mongo db.")
            await self.cache_storage.delete_data(
                key=f"user_likes_{user_id}_{movie_id}"
            )
            return
        logger.info(
            f"Error to delete a user's rating for a movie, user: {user_id},film_id: {movie_id} from mongo db.")
        raise UserLikeHTTPNotFoundError

    async def get_likes(
            self,
            start_date: str,
            end_date: str,
            page_number: int,
            page_size: int,
    ) -> List[GetUserLikeRespModel]:
        """Get paginted likes list from storage from start to end dates"""
        logger.info(f"Trying to get users likes from {start_date} to {end_date}")
        filter_query = {}
        try:
            result = await self.mongo_storage.get_ugc_data_chunks(
                database=Settings().MONGO_DB,
                collection=COLLECTION,
                query=filter_query,
                per_page=page_size,
                offset=(page_number - 1) * page_size,
            )
            total_docs_count = await self.mongo_storage.get_ugc_count_in_storage(
                database=Settings().MONGO_DB,
                collection=COLLECTION,
                filter_query=filter_query
            )
        except:
            logger.exception(f"Error when trying to get user likes.")
            raise StorageInternalError

        result_list = []
        if result:
            for row in result:
                row['mongo_object_id'] = str(row['_id'])
                result_list.append(GetUserLikeRespModel(**row))

        likes = GetLikesResponseModel(
            records=result_list,
            current_page=page_number,
            page_size=page_size,
            total_docs_count=total_docs_count,
            total_page_count=math.ceil(total_docs_count / page_size),
        )
        return likes


@lru_cache()
def get_user_like_service(
        mongo_storage: ABSStorage = Depends(get_mongo_storage_service),
        cashed_storage: ABSCacheStorage = Depends(get_redis_storage_service)
) -> LikesService:
    return LikesService(mongo_storage=mongo_storage, cache_storage=cashed_storage)
