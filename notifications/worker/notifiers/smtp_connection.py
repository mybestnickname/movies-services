import logging
from smtplib import SMTP_SSL, SMTPAuthenticationError
from typing import Optional
from core.req_handler import create_backoff_hdlr
import backoff

smtp_connection: Optional[SMTP_SSL] = None


def get_smtp_connection() -> smtp_connection:
    return smtp_connection


logger = logging.getLogger(__name__)
back_off_hdlr = create_backoff_hdlr(logger)


@backoff.on_exception(
    backoff.fibo,
    (Exception),

    max_time=150,
    max_tries=100,
    on_backoff=back_off_hdlr,
)
def smtp_connect(
        sender_user: str,
        sender_password: str,
        sender_email_server: str) -> SMTP_SSL:
    try:
        server = SMTP_SSL(sender_email_server)
        server.login(sender_user, sender_password)
        return server

    except SMTPAuthenticationError as es:
        raise ConnectionError
    except Exception as ex:
        logger.error(f'Failed authorization attempt to the mail server {ex}.')
