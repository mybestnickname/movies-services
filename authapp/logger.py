import logging.config
from logging import Logger

from flask import request
import logstash

from config import Config


class RequestIdFilter(logging.Filter):
    def filter(self, record):
        try:
            record.request_id = request.headers.get('X-Request-Id')
        except RuntimeError:
            pass
        record.service_name = Config().SERVICE_NAME
        record.tags = ["auth-flask-api"]
        return True


def setup_logging(logger: Logger):
    logging.basicConfig(
        level=logging.INFO,
        format='[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
    )
    logger.info(f"Trying to add logstash handler: {Config().LOGSTASH_HOST}:{Config().LOGSTASH_PORT}")
    logstash_handler = logstash.LogstashHandler(Config().LOGSTASH_HOST, Config().LOGSTASH_PORT, version=1)
    logstash_handler.addFilter(RequestIdFilter())
    logger.addHandler(logstash_handler)
