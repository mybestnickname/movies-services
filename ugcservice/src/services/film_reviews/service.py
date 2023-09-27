import logging
import math
from datetime import datetime
from functools import lru_cache
from typing import Optional
from uuid import UUID

from api.errors.httperrors import (DifferentFilmIdsError,
                                   NotFoundDeletingReviewError,
                                   NotFoundFilmScoreToLinkError,
                                   NotFoundReviewToLikeError,
                                   ReviewDeleteError, ReviewNotFoundError,
                                   ReviewUpdateError, StorageInternalError)
from bson.objectid import ObjectId
from core.config import Settings
from fastapi import Depends
from pkg.storage.mongo_storage import get_mongo_storage_service
from pkg.storage.storage import ABSStorage
from pydantic import ValidationError
from services.film_reviews.models import (FilmReview, FilmReviewScore,
                                          FilmReviewToScore)

logger = logging.getLogger(__name__)

REVIEWS_COLLECTION = "REVIEWS"
REVIEW_SCORES_COLLECTION = "REVIEW_SCORES"
FILM_SCORES_COLLECTION = "FILM_RATINGS"
REVIEW_FILMC_SCORE_COLLECTON = "REVIEW_TO_FILM_SCORE"


class ReviewsService:
    def __init__(self, mongo_storage: ABSStorage):
        self.mongo_storage = mongo_storage

    async def save_film_review(
            self,
            user_id: str,
            data: dict,
    ) -> None:
        """Send film review data to storage."""
        data['author']['user_id'] = user_id
        data['timestamp'] = datetime.utcnow().isoformat()
        data['film_id'] = str(data['film_id'])

        logger.info(f"User:{data['author']} is trying to add review to film_id{data['film_id']}")
        try:
            validated_data = FilmReview(**data)
        except ValidationError:
            logger.exception(f"Validation error of user review dict. {data}")
            raise StorageInternalError

        new_doc_id = await self.mongo_storage.send_to_ugc_storage(
            database=Settings().MONGO_DB,
            collection=REVIEWS_COLLECTION,
            ugc_data=validated_data.dict(),
        )
        validated_data.mongo_object_id = str(new_doc_id)

        logger.info(f"New review has been added successfully. film_id:{data['film_id']}")
        return validated_data.dict()

    async def upgrade_film_review(
        self,
        user_id: str,
        review_id: str,
        new_text: str,
    ) -> Optional[dict]:
        """Upgrade film review data in storage by _id."""
        logger.info(f"User:{user_id} is trying to update film review:{review_id}")

        film_review = await self._get_film_review_by_id(review_id)
        if not film_review:
            raise ReviewNotFoundError
        if film_review.author.user_id != user_id:
            raise ReviewUpdateError
        if film_review.text == new_text:
            film_review.mongo_object_id = review_id
            return film_review.dict()
        else:
            film_review.text = new_text

        film_review.update_timestamp = datetime.utcnow().isoformat()

        result_dict = await self.mongo_storage.create_or_update_in_ugc_storage(
            database=Settings().MONGO_DB,
            collection=REVIEWS_COLLECTION,
            filter_query={'_id': ObjectId(review_id), 'film_id': film_review.film_id},
            ugc_data=film_review.dict(),
        )
        logger.info(f"Review:{review_id} has been updated successfully.")

        result_dict['mongo_object_id'] = str(result_dict['_id'])
        return result_dict

    async def remove_film_review(
        self,
        user_id: str,
        review_id: str,
    ) -> None:
        """Remove film review from storage by _id."""
        logger.info(f"User:{user_id} is trying to remove film review:{review_id}")

        film_review = await self._get_film_review_by_id(review_id)
        if not film_review:
            raise NotFoundDeletingReviewError
        if film_review.author.user_id != user_id:
            raise ReviewDeleteError

        await self.mongo_storage.delete_ugc_from_storage(
            database=Settings().MONGO_DB,
            collection=REVIEWS_COLLECTION,
            query={'_id': ObjectId(review_id), 'film_id': film_review.film_id}
        )
        logger.info(f"Review:{review_id} has been deleted successfully.")

    async def _get_film_review_by_id(self, review_id: str) -> Optional[FilmReview]:
        doc_dict = await self.mongo_storage.get_ugc_from_storage(
            database=Settings().MONGO_DB,
            collection=REVIEWS_COLLECTION,
            query={'_id': ObjectId(review_id)}
        )
        if not doc_dict:
            return

        try:
            validated_data = FilmReview(**doc_dict)
        except ValidationError:
            logger.exception(f"Validation error of user review dict. {doc_dict}")
            raise StorageInternalError
        return validated_data

    async def get_film_reviews(
        self,
        film_id: UUID,
        docs_count_to_skip: int,
        page_size: int,
    ) -> Optional[dict]:
        """Get paginated film reviews list."""
        logger.info(f"Trying to get film review list for film:{film_id}")

        filter_query = {'film_id': str(film_id)}
        total_count = await self.mongo_storage.get_ugc_count_in_storage(
            database=Settings().MONGO_DB,
            collection=REVIEWS_COLLECTION,
            filter_query=filter_query
        )

        film_reviews = []
        if total_count:
            film_reviews = await self.mongo_storage.get_ugc_data_chunks(
                database=Settings().MONGO_DB,
                collection=REVIEWS_COLLECTION,
                per_page=page_size,
                offset=docs_count_to_skip,
                query=filter_query,
                sort_field="timestamp",
            )

        records = []
        for review_dict in film_reviews:
            review = FilmReview(**review_dict)
            review.mongo_object_id = str(review_dict.get('_id'))
            records.append(review)
        return {
            'total_count': total_count,
            'page_count': math.ceil(total_count / page_size),
            'records': records,
        }

    async def set_film_review_score(
        self,
        review_id: str,
        user_id: str,
        user_name: str,
        score: int,
    ) -> Optional[int]:
        """Set user score to review """
        logger.info(f"User:{user_id} is trying to set score to film review:{review_id}")

        # Validate inserting data
        try:
            validated_data = FilmReviewScore(
                review_id=review_id,
                author={'user_name': user_name, 'user_id': user_id},
                score=score,
                timestamp=datetime.utcnow().isoformat()
            )
        except ValidationError:
            raise StorageInternalError

        # check, that the review exists
        film_review = await self._get_film_review_by_id(review_id)
        if not film_review:
            raise NotFoundReviewToLikeError

        # create or update review score
        res_dict = await self.mongo_storage.create_or_update_in_ugc_storage(
            database=Settings().MONGO_DB,
            collection=REVIEW_SCORES_COLLECTION,
            filter_query={
                'user_id': validated_data.author.user_id,
                'review_id': validated_data.review_id
            },
            ugc_data=validated_data.dict()
        )
        res_dict['mongo_object_id'] = res_dict['_id']
        return res_dict

    async def link_film_score_to_review(
        self,
        review_id: str,
        film_score_id: str,
        user_id: str,
        user_name: str,
    ) -> Optional[int]:
        """Set user score to review """
        logger.info(f"User:{user_name}:{user_id} is trying to link film score to film review:{review_id}")

        # Validate inserting data
        try:
            validated_data = FilmReviewToScore(
                review_id=review_id,
                film_score_id=film_score_id,
            )
        except ValidationError:
            raise StorageInternalError

        # check, that review exists
        film_review = await self._get_film_review_by_id(review_id)
        if not film_review:
            raise NotFoundReviewToLikeError

        # check, that score exists
        film_score_dict = await self.mongo_storage.get_ugc_from_storage(
            database=Settings().MONGO_DB,
            collection=FILM_SCORES_COLLECTION,
            query={'_id': ObjectId(film_score_id)}
        )
        if not film_score_dict:
            raise NotFoundFilmScoreToLinkError

        if film_review.film_id != film_score_dict['movie_id']:
            raise DifferentFilmIdsError

        # create or update review score
        await self.mongo_storage.create_or_update_in_ugc_storage(
            database=Settings().MONGO_DB,
            collection=REVIEW_FILMC_SCORE_COLLECTON,
            filter_query={
                'review_id': validated_data.review_id,
                'film_score_id': validated_data.film_score_id
            },
            ugc_data=validated_data.dict()
        )


@ lru_cache()
def get_reviews_service(
        mongo_storage: ABSStorage = Depends(get_mongo_storage_service),
) -> ReviewsService:
    return ReviewsService(mongo_storage=mongo_storage)
