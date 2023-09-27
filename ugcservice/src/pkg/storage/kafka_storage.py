import logging
from functools import lru_cache

from aiokafka import AIOKafkaProducer
from db.kafka import get_kafka
from fastapi import Depends
from pkg.storage.storage import ABSStorage

logger = logging.getLogger(__name__)


class KafkaService(ABSStorage):
    def __init__(self, kafka: AIOKafkaProducer) -> None:
        self.kafka = kafka

    async def send_to_ugc_storage(
            self,
            topic: str,
            ugc_data: str,
            key: str,
    ) -> bool:
        """Send ugc data to kafka topic."""
        try:
            await self.kafka.send_and_wait(
                topic=topic,
                value=str.encode(ugc_data),
                key=str.encode(key),
            )
        except Exception:
            logger.exception(f"Failed to send message to Kafka {topic} {ugc_data} {key}.")
            return False
        return True

    def get_ugc_from_storage(self):
        raise NotImplementedError

    def delete_ugc_from_storage(self):
        raise NotImplementedError

    def create_or_update_in_ugc_storage(self):
        raise NotImplementedError

    def get_ugc_count_in_storage(self):
        raise NotImplementedError

    def get_ugc_data_chunks(self):
        raise NotImplementedError

    def get_avg_ugc_data(self):
        raise NotImplementedError


@lru_cache()
def get_kafka_storage_service(
        kafka: AIOKafkaProducer = Depends(get_kafka),
) -> KafkaService:
    return KafkaService(kafka)
