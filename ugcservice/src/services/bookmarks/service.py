import logging
import math
from datetime import datetime
from functools import lru_cache
from typing import Optional
from uuid import UUID

from api.errors.httperrors import BookmarkNotFoundError, StorageInternalError
from api.v1.bookmarks.models import ListFilmBookmarkResponseModel
from bson import ObjectId
from core.config import Settings
from fastapi import Depends
from pkg.storage.mongo_storage import get_mongo_storage_service
from pkg.storage.storage import ABSStorage
from services.bookmarks.models import FilmBookmark

logger = logging.getLogger(__name__)

BOOKMARKS_COLLECTION = 'FILM_BOOKMARKS'


class BookmarksService:
    def __init__(self, mongo_storage: ABSStorage):
        self.mongo_storage = mongo_storage

    async def save_film_in_bookmarks(
            self,
            film_id: UUID,
            user_id: UUID,
            film_name: Optional[str] = None,
            user_name: Optional[str] = None,
    ) -> None:
        """Add film to users bookmarks"""
        logger.info(
            f"User:{user_id}:{user_name} is trying to add film:{film_id}:{film_name} into bookmarks."
        )
        try:
            await self.mongo_storage.create_or_update_in_ugc_storage(
                database=Settings().MONGO_DB,
                collection=BOOKMARKS_COLLECTION,
                filter_query={'film_id': str(film_id), 'user_id': str(user_id)},
                ugc_data={
                    'film_id': str(film_id),
                    'user_id': str(user_id),
                    'film_name': film_name,
                    'timestamp': datetime.utcnow().isoformat()
                }
            )
        except:
            raise StorageInternalError
        logger.info(f"Film:{film_id}:{film_name} has been successfully added to user:{user_id} bookmarks.")

    async def get_bookmarks(
            self,
            user_id: str,
            page_number: int,
            page_size: int
    ) -> ListFilmBookmarkResponseModel:
        """get bookmarks from storage."""
        filter_query = {'user_id': str(user_id)}
        offset_from = (page_number - 1) * page_size
        logger.info(f"trying to get a bookmark user: {user_id} from mongo db.")
        try:
            result = await self.mongo_storage.get_ugc_data_chunks(
                database=Settings().MONGO_DB,
                collection=BOOKMARKS_COLLECTION,
                query=filter_query,
                per_page=page_size,
                offset=offset_from,
                sort_field='timestamp'
            )
            total_docs_count = await self.mongo_storage.get_ugc_count_in_storage(
                database=Settings().MONGO_DB,
                collection=BOOKMARKS_COLLECTION,
                filter_query=filter_query
            )
        except:
            logger.exception(f"Error to get a bookmark user: {user_id} from mongo db.")
            raise StorageInternalError

        result_list = []
        if result:
            for row in result:
                row['mongo_object_id'] = str(row['_id'])
                result_list.append(FilmBookmark(**row))

        bookmarks = ListFilmBookmarkResponseModel(
            records=result_list,
            current_page=page_number,
            page_size=page_size,
            total_docs_count=total_docs_count,
            total_page_count=math.ceil(total_docs_count / page_size),
        )
        logger.info(f"get a bookmark user: {user_id} from mongo db.")
        return bookmarks

    async def delete_bookmark(
            self,
            bookmark_id: str,
            user_id: str,
            film_id: str,
    ) -> None:
        """delete bookmarks from storage."""
        logger.info(f"trying to delete a bookmark {bookmark_id}.")
        if await self.mongo_storage.delete_ugc_from_storage(
                database=Settings().MONGO_DB,
                collection=BOOKMARKS_COLLECTION,
                query={
                    '_id': ObjectId(bookmark_id),
                    'film_id': film_id,
                    'user_id': user_id}
        ):
            logger.info(f"bookmark: {bookmark_id}, user: {user_id}  has been deleted.")
            return
        logger.exception(
            f"error while deleting bookmark: {bookmark_id}, user:{user_id}, film_id:{film_id} from mongo db.")
        raise BookmarkNotFoundError


@lru_cache()
def get_bookmarks_service(
        mongo_storage: ABSStorage = Depends(get_mongo_storage_service)
) -> BookmarksService:
    return BookmarksService(mongo_storage=mongo_storage)
