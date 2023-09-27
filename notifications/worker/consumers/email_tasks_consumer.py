import json
import logging

import aio_pika

from consumers.abs_consumer import ABCConsumer
from services_clients.templates_getter import get_templates_getter
from services_clients.auth_client import get_auth_service

from notifiers.email_notifier import get_email_service

logger = logging.getLogger(__name__)


class EmailTasksConsumer(ABCConsumer):

    def __init__(self):
        self.templates_getter = get_templates_getter()
        self.auth_service = get_auth_service()
        self.email_service = get_email_service()

    async def process_message(
            self,
            message: aio_pika.abc.AbstractIncomingMessage,
    ) -> None:
        logger.info("Task processing started.")
        async with message.process(ignore_processed=True):
            json_body = json.loads(message.body)
            logger.info(f"Trying to process notifications task: {json_body}")
            template = await self.templates_getter.get_template_by_name(json_body.get("template_name"))

            if not json_body.get('users_id') and json_body.get('users_group'):
                logger.info(
                    f"Notification task for users group {json_body.get('users_group')} has been started."
                )
                async for users in self.auth_service.get_users_by_roles(json_body.get('users_group')):
                    await self.email_service.send_mass_email(
                        [user for user in users.get('login')],
                        None,
                        template=template
                    )

            elif json_body.get('users_id'):
                logger.info(
                    f"Notification task for users {json_body.get('users_id')} has been started."
                )
                async for users in self.auth_service.get_users_by_ids(json_body.get('users_id')):
                    for user in users:
                        rendered_template = await self.email_service.template_render(
                            template_content=self._get_template_personal(
                                json_body.get("template_name"),
                                user.get('id')
                            ),
                            template=template
                        )
                        await self.email_service.send_personal_email(
                            user.get('login'),
                            'Hello ' + user.get('login'),
                            rendered_template
                        )

            await message.ack()

    def _send_to_user(self):
        raise NotImplementedError

    def _get_template_personal(self, template_name: str, user_id: str) -> dict:
        """Get personal parameters for user by template name"""
        logger.info(f"Getting params for {template_name} for user: {user_id}.")
        return {}
