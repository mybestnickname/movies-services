import asyncio
import os
import logging
import sys
import aio_pika

from consumers.email_tasks_consumer import EmailTasksConsumer
from consumers.sms_tasks_consumer import SmsTasksConsumer

from config import Settings
from notifiers.smtp_connection import smtp_connection, smtp_connect

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

consumers = {
    'email': EmailTasksConsumer,
    'sms': SmsTasksConsumer,
}


class ConsumerException(Exception):
    pass


async def main() -> None:
    smtp_connection.smtp_connection = smtp_connect(
        Settings().SENDER_USER,
        Settings().SENDER_PASSWORD,
        Settings().SENDER_EMAIL_SERVER)

    rabbit_uri = f"amqp://{Settings().RABBIT_USER}:{Settings().RABBIT_PASSWORD}@{Settings().RABBIT_HOST}:{Settings().RABBIT_PORT}/"
    logger.info(f"Connection to rabbit brokker on {rabbit_uri}")
    connection = await aio_pika.connect_robust(rabbit_uri)

    logger.info("Creating channel")
    channel = await connection.channel()

    # Maximum message count which will be processing at the same time.
    await channel.set_qos(prefetch_count=100)

    # Declaring queue(one worker for one queue)
    queue = await channel.declare_queue(Settings().QUEUE_NAME, durable=True)

    consumer = consumers.get(Settings().QUEUE_NAME)

    if not consumer:
        raise ConsumerException(f"Consumer for queue:{Settings().QUEUE_NAME} not found.")

    await queue.consume(consumer().process_message)

    try:
        # Wait until terminate
        await asyncio.Future()
    finally:
        await connection.close()


if __name__ == "__main__":
    asyncio.run(main())
