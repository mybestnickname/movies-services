from functools import lru_cache

import pandas as pd

from pkg.storage.base_storage import BaseScoresStorage
from core.settings import Settings, get_settings


class FileScoresStorage(BaseScoresStorage):
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def get_all_scores(self) -> pd.DataFrame:
        return pd.read_csv(self.settings.storage.file_storage_path)


@lru_cache()
def get_file_scores_storage() -> FileScoresStorage:
    return FileScoresStorage(settings=get_settings())
