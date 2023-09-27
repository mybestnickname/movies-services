from functools import lru_cache

import pandas as pd
import requests
from tqdm.auto import tqdm

from core.settings import Settings, get_settings
from pkg.storage.base_storage import BaseScoresStorage
from core.logger import logger

PAGINATION_PAGE_SIZE = 1000
PAGINATION_FIRST_PAGE_NUMBER = 1


class UGCServiceStorage(BaseScoresStorage):
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def get_all_scores(self) -> pd.DataFrame:
        logger.info('Start loading data from UGC API')
        data = []
        first_response = self._make_scores_request(
            page_number=PAGINATION_FIRST_PAGE_NUMBER,
            page_size=PAGINATION_PAGE_SIZE
        ).json()
        data += first_response['records']
        total_pages = first_response['total_page_count']
        for i in tqdm(range(2, total_pages + 1)):
            response = self._make_scores_request(page_number=i, page_size=PAGINATION_PAGE_SIZE).json()
            data += response['records']
        return pd.DataFrame(data)
        
    def _make_scores_request(self, page_number: int, page_size: int):
        link = f'http://{self.settings.ugc.host}:{self.settings.ugc.port}/{self.settings.ugc.scores_endpoint}'
        headers = {'internal-token': self.settings.inner_key}
        payload = {'page[size]': page_size, 'page[number]': page_number}
        response = requests.get(
            url=link,
            headers=headers,
            params=payload
        )
        return response


@lru_cache()
def get_ugc_service_storage() -> UGCServiceStorage:
    return UGCServiceStorage(settings=get_settings())
