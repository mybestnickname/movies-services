from datetime import datetime

import pandas as pd
from faker import Faker
from tqdm.auto import tqdm

from core.settings import get_settings
from core.logger import logger
from pkg.mongo_loader import get_mongo_loader
from pkg.elastic_loader import get_es_loader

settings = get_settings()


def from_csv_data_generator(csv_path: str, batch_size: int = 10000):
    df = prepare_dataframe(csv_path)
    start_idx = 0
    end_idx = start_idx + batch_size
    while True:
        batch = df[start_idx:end_idx].T.to_dict().values()
        if len(batch) == 0:
            raise StopIteration
        yield batch
        start_idx = end_idx
        end_idx = start_idx + batch_size


def prepare_dataframe(csv_path: str) -> pd.DataFrame:
    logger.info('Start reading csv file...')
    df = pd.read_csv(csv_path)[:1000000]
    logger.info('Start dataframe preprocessing...')
    df['date'] = df['date'].apply(lambda x: datetime.strptime(x, '%Y-%m-%d'))
    df = df.rename(columns={'date': 'time_stamp'})
    faker = Faker()
    user_names = [faker.email() for _ in range(len(df))]
    df['user_name'] = user_names
    del user_names
    return df


def load_scores_to_mongo():
    data_generator = from_csv_data_generator(csv_path=settings.data.scores_csv_path)
    mongo_loader = get_mongo_loader()
    logger.info('Start loading netflix score data to UGC Mongo')
    try:
        while True:
            batch = next(data_generator)
            mongo_loader.insert_data_batched(
                db=settings.mongo.db_name,
                collection=settings.mongo.scores_collection,
                data=batch
            )
            logger.info('Batch of data loaded in mongo')
    except:
        pass


def load_movies_to_elastic():
    logger.info('Start loading netflix data to elasticsearch')
    df = pd.read_csv(settings.data.movies_csv_path, encoding="ISO-8859-1",
                     header=None, names=['movie_id', 'year', 'title'])
    es_loader = get_es_loader()
    for _, row in tqdm(df.iterrows()):
        document = {
            'id': row['movie_id'],
            'title': row['title'],
            'imdb_rating': 7.7777777,
            'genre': [],
            'description': '',
            'director': 'Super director',
            'actors_names': [],
            'writers_names': [],
            'actors': [],
            'writers': []
        }
        es_loader.save_documents('movies', [document])


def main():
    load_scores_to_mongo()
    load_movies_to_elastic()


if __name__ == '__main__':
    main()
