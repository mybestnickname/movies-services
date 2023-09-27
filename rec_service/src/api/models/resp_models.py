from typing import List, Optional, Union
from pydantic import BaseModel, Field


class PersonFilmWork(BaseModel):
    id: str
    name: str


class FilmRespModel(BaseModel):
    id: str
    imdb_rating: float
    genres: Optional[list] = Field(None, alias='genre')
    title: str
    description: Optional[str] = None
    director: Union[str, List[str]]
    actors: Optional[List[PersonFilmWork]] = None
    writers: Optional[List[PersonFilmWork]] = None
    rec_score: Optional[float]
