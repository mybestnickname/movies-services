import logging
import math
from functools import lru_cache

from api.errors.httperrors import (MovieScoreHTTPNotFoundError,
                                   StorageInternalError)
from api.v1.moviescores.models import GetAvgMovieScoreRespModel
from core.config import Settings
from fastapi import Depends
from pkg.cache_storage.redis_storage import get_redis_storage_service
from pkg.cache_storage.storage import ABSCacheStorage
from pkg.storage.mongo_storage import get_mongo_storage_service
from pkg.storage.storage import ABSStorage
from services.moviescores.models import UserLike

logger = logging.getLogger(__name__)

COLLECTION = 'FILM_RATINGS'


class MovieScoreService:
    def __init__(self, mongo_storage: ABSStorage, cache_storage: ABSCacheStorage):
        self.mongo_storage = mongo_storage
        self.cache_storage = cache_storage

    async def get_movie_likes(
            self,
            movie_id: str,
            page_number: int,
            page_size: int,
    ) -> dict:
        """get movie likes from storage."""
        logger.info(
            f"trying to get movie ratings, movie_id: {movie_id}, page_number: {page_number}, page_size:{page_size} from mongo db.")
        filter_query = {'movie_id': str(movie_id)}
        total_docs_count = await self.mongo_storage.get_ugc_count_in_storage(
            database=Settings().MONGO_DB,
            collection=COLLECTION,
            filter_query=filter_query
        )
        if not total_docs_count:
            raise MovieScoreHTTPNotFoundError

        offset_from = (page_number - 1) * page_size
        result = await self.mongo_storage.get_ugc_data_chunks(
            database=Settings().MONGO_DB,
            collection=COLLECTION,
            query=filter_query,
            per_page=page_size,
            offset=offset_from,
            sort_field='timestamp'
        )

        user_likes = {
            "records": [UserLike(**row) for row in result],
            "current_page": page_number,
            "page_size": page_size,
            "total_docs_count": total_docs_count,
            "total_page_count": math.ceil(total_docs_count / page_size)
        }
        logger.info("get movie likes from mongo.")
        logger.info(
            f"Successful to get movie ratings, movie_id: {movie_id}, page_number: {page_number}, page_size:{page_size} from mongo db.")
        return user_likes

    async def get_avg_movie_score(
            self,
            movie_id: str
    ) -> GetAvgMovieScoreRespModel:
        """get avg movie scores from storage."""
        logger.info(
            f"trying to get movie avg ratings, movie_id: {movie_id} from mongo db.")
        cashed_key = f"avg_movie_score_{movie_id}"
        cashed_data = await self.cache_storage.get_data(key=cashed_key)
        if cashed_data:
            result = GetAvgMovieScoreRespModel.parse_raw(cashed_data)
            logger.info(
                f"avg ratings, retrieved from cache movie_id: {movie_id}.")
            return result
        agg_query = [
            {
                "$match": {"movie_id": movie_id}
            },
            {
                "$group": {
                    "_id": "$movie_id",
                    "avg_movie_rating": {"$avg": "$score"}
                }
            }
        ]
        try:
            avg_score_value = await self.mongo_storage.get_avg_ugc_data(
                database=Settings().MONGO_DB,
                collection=COLLECTION,
                query=agg_query
            )
        except:
            raise StorageInternalError
        if not avg_score_value:
            raise MovieScoreHTTPNotFoundError
        logger.info("Get avg movie score from mongo.")
        result = GetAvgMovieScoreRespModel(movie_id=movie_id,
                                           avg_movie_rating=avg_score_value[0].get("avg_movie_rating"))
        await self.cache_storage.set_data(
            key=cashed_key,
            data=result.json())
        logger.info(
            f"avg ratings, added to cache movie_id: {movie_id}.")
        logger.info(
            f"Success to get movie avg ratings, movie_id: {movie_id} from mongo db.")
        return result


@lru_cache()
def get_movie_scores_service(
        mongo_storage: ABSStorage = Depends(get_mongo_storage_service),
        cashed_storage: ABSCacheStorage = Depends(get_redis_storage_service)
) -> MovieScoreService:
    return MovieScoreService(mongo_storage=mongo_storage, cache_storage=cashed_storage)
