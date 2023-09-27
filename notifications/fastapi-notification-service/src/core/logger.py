import logging
from logging import Logger

import logstash
from api.middlewares import get_request_id
from core.config import Settings
from core.logger_settings import LOGGING


class RequestIdFilter(logging.Filter):
    def filter(self, record):
        record.request_id = get_request_id()
        record.service_name = Settings().SERVICE_NAME
        record.tags = ["notification-fastapi-app"]
        return True


def setup_logging(logger: Logger):
    if Settings().ENV == "dev":
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)

    logging.config.dictConfig(LOGGING)
    logger.info(f"Trying to add logstash handler: {Settings().LOGSTASH_HOST}:{Settings().LOGSTASH_PORT}")
    logstash_handler = logstash.LogstashHandler(Settings().LOGSTASH_HOST, Settings().LOGSTASH_PORT, version=1)
    logstash_handler.addFilter(RequestIdFilter())
    logger.addHandler(logstash_handler)