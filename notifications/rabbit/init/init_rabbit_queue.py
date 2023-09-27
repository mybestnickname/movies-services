import time
import pika
import logging
from logging import config as logger_conf
from logger import log_conf

logger_conf.dictConfig(log_conf)
logger = logging.getLogger(__name__)

queues = ["sms", "email"]
RABBIT_URL_CONNECTION = "amqp://guest:guest@rabbit1/"

while True:
    try:
        rmq_parameters = pika.URLParameters(RABBIT_URL_CONNECTION)
        rmq_connection = pika.BlockingConnection(rmq_parameters)
        rmq_channel = rmq_connection.channel()
        for name in queues:
            rmq_channel.queue_declare(name, durable=True)
        break
    except Exception as ex:
        logger.info(f"Unsuccessful attempt to connect to rabbit {RABBIT_URL_CONNECTION} {ex}")
        time.sleep(10)

