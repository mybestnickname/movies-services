import datetime
import logging
from functools import lru_cache
from typing import Union
from uuid import UUID

from fastapi import Depends
from pkg.storage.kafka_storage import get_kafka_storage_service
from pkg.storage.storage import ABSStorage

AUTH_VIEWS_TOPIC = "auth_views_labels"
UNAUTH_VIEWS_TOPIC = "unauth_views_labels"
logger = logging.getLogger(__name__)


class MovieWatchMarkService:
    def __init__(self, storage: ABSStorage):
        self.storage = storage

    async def save_watchmark(
            self,
            film_id: Union[str, UUID],
            user_id: Union[str, UUID, None],
            timestamp: datetime.time,
    ) -> bool:
        """Send film watchmark to storage."""
        logger.info(
            "User:{user_str} is trying to send film:{film_id} watchmark timestamp{ts} into Kafka storage.".format(
                user_str=user_id if user_id else "unauthorized user",
                film_id=film_id,
                ts=timestamp,
            ),
        )

        if user_id:
            topic = AUTH_VIEWS_TOPIC
            key = f'{film_id}_{user_id}'
        else:
            topic = UNAUTH_VIEWS_TOPIC
            key = "{film_id}_{unauthuser_id}".format(
                film_id=str(film_id),
                unauthuser_id='00000000-0000-0000-0000-000000000000',
            )
        if await self.storage.send_to_ugc_storage(
                topic=topic,
                ugc_data=timestamp.isoformat(),
                key=key,
        ):
            logger.info("Watchmark has been saved.")
            return True
        logger.info("Watchmark hasn't been saved.")
        return False


@lru_cache()
def get_watchmark_service(
        storage: ABSStorage = Depends(get_kafka_storage_service)
) -> MovieWatchMarkService:
    return MovieWatchMarkService(storage=storage)
