from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class UserLike(BaseModel):
    movie_id: str
    user_id: str
    user_name: str
    score: Optional[int] = Field(
        ge=0,
        le=10,
    )
    time_stamp: datetime


class GetAvgMovieScoreRespModel(BaseModel):
    avg_movie_rating: float
    movie_id: UUID = Field(example="4f91f972-f071-4ac9-9c31-55f7ee3bc8aa")


class ListMoviesLikeResponseModel(BaseModel):
    records: List[UserLike]
    current_page: int
    page_size: int
    total_docs_count: int
    total_page_count: int
