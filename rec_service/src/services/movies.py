from functools import lru_cache
from typing import List
import aiohttp
from core.config import Settings


class MoviesService:
    def __init__(self):
        self.movies_service_url = Settings().MOVIES_SERVICE

    async def get_films_by_id(self, film_ids: List[str]):
        url = f"{self.movies_service_url}{'inner/films_by_id/'}"
        headers = {"internal-token": Settings().INNER_KEY}
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.post(url, json={"ids": film_ids}) as response:
                return await response.json()


@lru_cache()
def get_movies_service() -> MoviesService:
    return MoviesService()
