import logging
from functools import lru_cache
from http import HTTPStatus
from typing import List

import aiohttp
from config import Settings

logger = logging.getLogger(__name__)

COUNT_PER_PAGE = 100


class GetUsersError(Exception):
    pass


class AuthServiceClient:
    def __init__(self):
        self.auth_url = Settings().AUTH_SERVICE

    async def get_users_by_roles(self, roles: str = None) -> List[dict]:
        """
        Get users by roles from <auth service> paginated endpoint 
        """
        users_url = f"{self.auth_url}/users/"
        params = {'count_per_page': COUNT_PER_PAGE, 'page_number': '1'}
        if roles:
            params['roles'] = roles
        logger.info(f"Trying to get users from {users_url} with params: {params}")

        first_page_res = await self.do(
            url=users_url,
            method="get",
            params=params,
        )

        if not first_page_res.get('total_count'):
            logger.info(f"Failed to get users with roles: {roles}")

        yield first_page_res.get('users')

        page_count = first_page_res.get('page_count')
        if page_count > 1:
            for page_number in range(2, page_count + 1):
                params['page_number'] = page_number
                logger.info(f"Trying to get users from {users_url} with params: {params}")
                page_res = await self.do(
                    url=users_url,
                    method="get",
                    params=params,
                )
                yield page_res.get('users')

    async def get_users_by_ids(self, ids: List[str]) -> List[dict]:
        """
        Get users by ids from <auth service> 
        """
        users_url = f"{self.auth_url}/users/get_by_ids"
        for n_users_chunk in range(0, len(ids), COUNT_PER_PAGE):
            ids_chunk = ids[n_users_chunk:n_users_chunk + COUNT_PER_PAGE]
            logger.info(f"Trying to get users from {users_url} with id(s): {ids}")
            users_resp = await self.do(
                url=users_url,
                method="get",
                params={'user_ids': ','.join(ids_chunk)},
            )
            if len(ids_chunk) != len(users_resp.get('users')):
                ids_in_res = set(user['id'] for user in users_resp.get('users'))
                logger.error(f"Failed to get users with id(s): {set(ids_chunk) - ids_in_res}")
                raise GetUsersError("Failed to get users from auth service")
            yield users_resp.get('users')

    async def do(self, url: str, method: str, params: dict):
        """
        Send get request to auth service
        """
        headers = {"Innertoken": Settings().INNER_KEY}
        async with aiohttp.ClientSession(headers=headers) as session:
            if method == "get":
                async with session.get(url, params=params) as resp:
                    if resp.status != HTTPStatus.OK:
                        raise GetUsersError("Failed to get users from auth service")
                    return await resp.json()


@lru_cache()
def get_auth_service() -> AuthServiceClient:
    return AuthServiceClient()
