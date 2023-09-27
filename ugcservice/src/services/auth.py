import logging
from functools import lru_cache

import aiohttp
from core.config import Settings

logger = logging.getLogger(__name__)


class AuthService:
    def __init__(self):
        self.auth_url = Settings().AUTH_SERVICE

    async def validate(self, token: str):
        headers = {"Authorization": f"Bearer {token}"}
        async with aiohttp.ClientSession(headers=headers) as session:
            logger.info(f"Trying to validate token:{token} at {self.auth_url}.")
            async with session.get(self.auth_url) as response:
                return await response.json()


@lru_cache()
def get_auth_service() -> AuthService:
    return AuthService()
