import json
import logging
from functools import lru_cache

from fastapi import Depends
from pkg.broker.rabbit_broker import get_rabbit_broker_service
from pkg.broker.broker import AbstractBroker

logger = logging.getLogger(__name__)


class TaskService:
    def __init__(self, rabbit_broker: AbstractBroker):
        self.rabbit = rabbit_broker

    async def send_to_queue(
            self,
            queue: str,
            data: dict
    ) -> None:
        """Add task to rabbit mq"""
        logger.info(
            "Trying to add task into rabbit."
        )
        await self.rabbit.send_to_broker(
            data=json.dumps(data).encode('UTF-8'),
            routing_key=queue)
        logger.info("Success to add in Rabbit.")


@lru_cache()
def get_task_service(
        rabbit: AbstractBroker = Depends(get_rabbit_broker_service)
) -> TaskService:
    return TaskService(rabbit_broker=rabbit)
