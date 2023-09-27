import logging
from functools import lru_cache
from http import HTTPStatus

import aiohttp
from config import Settings

logger = logging.getLogger(__name__)


class GetTemplateError(Exception):
    pass


class TemplatesGetter:
    def __init__(self):
        self.templates_admin_url = Settings().TEMPLATES_SERVICE

    async def get_template_by_name(self, template_name: str) -> str:
        """
        Get notification template from templates/tasks admin service
        """
        get_templates_url = f"{self.templates_admin_url}/email_templates/{template_name}"
        logger.info(f"Trying to get {template_name} template from {get_templates_url}")

        tmp_res = await self.do(
            url=get_templates_url,
            method="get"
        )
        return tmp_res.get('template')

    async def do(self, url: str, method: str):
        """
        Send get request to notifications admin panel
        """
        async with aiohttp.ClientSession() as session:
            if method == "get":
                async with session.get(url) as resp:
                    if resp.status != HTTPStatus.OK:
                        raise GetTemplateError("Failed to get template from template service")
                    return await resp.json()


@lru_cache()
def get_templates_getter() -> TemplatesGetter:
    return TemplatesGetter()
