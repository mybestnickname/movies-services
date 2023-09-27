from abc import ABC, abstractmethod

import pandas as pd


class BaseScoresStorage(ABC):
    @abstractmethod
    def get_all_scores(self) -> pd.DataFrame:
        pass
