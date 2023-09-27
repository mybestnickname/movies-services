import logging
from email.message import EmailMessage
from functools import lru_cache

import backoff
from jinja2 import Template

from config import Settings
from notifiers.notifier import AbstractNotifier
from notifiers.smtp_connection import get_smtp_connection, smtp_connection, smtp_connect, back_off_hdlr

logger = logging.getLogger(__name__)


class EmailService(AbstractNotifier):

    def __init__(self):
        self.server = get_smtp_connection()

    @backoff.on_exception(
        backoff.fibo,
        ConnectionAbortedError,
        max_time=150,
        max_tries=100,
        on_backoff=back_off_hdlr,
    )
    async def send_mass_email(
            self,
            recipients: list,
            subject_text: str,
            template: str
    ):
        message = EmailMessage()
        message["From"] = self.server.user
        message["Subject"] = subject_text if subject_text else "YaNetflix message"

        message.add_alternative(template, subtype='html')
        try:
            self.server.sendmail(self.server.user, [*recipients], message.as_string())
        except Exception as ex:
            logger.error(f'Error sending email lost connection to mail server {ex}.')
            smtp_connection.smtp_connection = smtp_connect(
                Settings().SENDER_USER,
                Settings().SENDER_PASSWORD,
                Settings().SENDER_EMAIL_SERVER)
            raise ConnectionAbortedError

    @backoff.on_exception(
        backoff.fibo,
        ConnectionAbortedError,
        max_time=150,
        max_tries=100,
        on_backoff=back_off_hdlr,
    )
    async def send_personal_email(
            self,
            recipient: str,
            subject_text: str,
            template: str
    ):
        message = EmailMessage()
        message["From"] = self.server.user
        message["To"] = ",".join([recipient])
        message["Subject"] = subject_text
        message.add_alternative(template, subtype='html')
        try:
            self.server.sendmail(self.server.user, [recipient], message.as_string())
        except Exception as ex:
            logger.error(f'Error sending email lost connection to mail server {ex}.')
            smtp_connection.smtp_connection = smtp_connect(
                Settings().SENDER_USER,
                Settings().SENDER_PASSWORD,
                Settings().SENDER_EMAIL_SERVER)
            raise ConnectionAbortedError

    async def template_render(
            self,
            template_content: dict,
            template: str,
    ) -> str:
        jinja_template = Template(template, enable_async=True)
        rendered_template = await jinja_template.render_async(**template_content)
        return rendered_template


@lru_cache()
def get_email_service(
) -> EmailService:
    return EmailService()
