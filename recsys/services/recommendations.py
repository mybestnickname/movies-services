from functools import lru_cache
from typing import Dict

import pandas as pd
from surprise import Reader, Dataset, SVD
from tqdm.auto import tqdm
import requests

from core.settings import Settings, get_settings
from core.logger import logger


class RecommendationsService:
    def __init__(self, settings: Settings):
        self.settings = settings
        self._reader = Reader()
        self._model = None

    def make_recommendations(self, data: pd.DataFrame) -> None:
        logger.info('Start model training')
        self._train_model(data)
        logger.info('Model successfully trained')
        logger.info('Start predicting recommendations')
        self._predict_recommendations_model(data)

    def _predict_recommendations_model(self, data: pd.DataFrame) -> None:
        user_ids = data['user_id'].unique()
        movie_ids = data['movie_id'].unique()
        for user_id in tqdm(user_ids):

            already_watched_movies_for_user = data.loc[data['user_id'] == user_id]['movie_id'].values
            user_preds = []
            for movie_id in movie_ids:
                if movie_id in already_watched_movies_for_user:
                    continue
                score = self._model.predict(user_id, movie_id).est
                user_preds.append({'movie_id': movie_id, 'rec_score': score})

            user_preds = sorted(user_preds, key=lambda d: d['rec_score'], reverse=True)[
                :self.settings.recsys.n_recommendations_predict]
            recommendations = {'user_id': user_id, 'recommendations': user_preds}
            self._send_recommendations_to_external_service(recommendations)

    def _train_model(self, data: pd.DataFrame):
        dataset = Dataset.load_from_df(data[['user_id', 'movie_id', 'score']][:], self._reader)
        trainset = dataset.build_full_trainset()
        svd = SVD(n_epochs=self.settings.recsys.train_n_epochs)
        svd.fit(trainset)
        self._model = svd
        del dataset
        del trainset

    def _send_recommendations_to_external_service(self, data: Dict) -> None:
        link = f'http://{self.settings.recapi.host}:{self.settings.recapi.port}/{self.settings.recapi.recs_endpoint}'
        headers = {'internal-token': self.settings.inner_key}
        response = requests.post(
            url=link,
            headers=headers,
            json=data
        )
        return response


@lru_cache()
def get_recommendations_service() -> RecommendationsService:
    return RecommendationsService(settings=get_settings())
