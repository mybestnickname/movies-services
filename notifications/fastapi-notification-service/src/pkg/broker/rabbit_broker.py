import logging
from asyncio.log import logger
from functools import lru_cache
from aio_pika import Channel
from fastapi import Depends

from api.errors.httperrors import StorageInternalError, QueueNotFoundException
from broker.rabbit import get_rabbit_chanel
from pkg.broker.broker import AbstractBroker

logger = logging.getLogger(__name__)


class RabbitService(AbstractBroker):
    def __init__(self, rabbit: Channel) -> None:
        self.rabbit = rabbit

    async def send_to_broker(
            self,
            routing_key: str,
            data: bytes,
            exchange: str = ''
    ) -> None:
        """Send task data to rabbit query."""
        try:
            res = await self.rabbit.channel.basic_publish(
                exchange=exchange,
                routing_key=routing_key,
                body=data,
                mandatory=True)
        except Exception:
            logger.exception(f"Failed to send data to rabbit {routing_key}.")
            raise StorageInternalError
        if not res.delivery_tag:
            logger.exception(f"Failed to send data to rabbit queue {routing_key} is not found.")
            raise QueueNotFoundException

    def get_from_broker(self):
        raise NotImplementedError


@lru_cache()
def get_rabbit_broker_service(
        rabbit: Channel = Depends(get_rabbit_chanel),
) -> RabbitService:
    return RabbitService(rabbit)
