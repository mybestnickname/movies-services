from functools import lru_cache

from typing import Any, Dict, Iterator, List

from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk

from core.settings import Settings, get_settings


class ElasticLoader:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.es_client = Elasticsearch(hosts=[{"host": self.settings.es.host, "port": self.settings.es.port}])

    def _documents_data_generator(self, index: str, documents: List[Any]) -> Iterator[Dict[Any, Any]]:
        for document in documents:
            yield {
                '_id': document['id'],
                '_index': index,
                '_op_type': 'index',
                **document
            }

    def save_documents(self, index: str, documents: Any) -> None:
        data_generator = self._documents_data_generator(index, documents)
        bulk(self.es_client, data_generator)


@lru_cache()
def get_es_loader() -> ElasticLoader:
    return ElasticLoader(settings=get_settings())
