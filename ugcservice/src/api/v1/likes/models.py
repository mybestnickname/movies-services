from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field

from pkg.pagination.pagination import PaginatedResponseModel


class GetUserLikeRespModel(BaseModel):
    movie_id: str
    user_id: str
    user_name: str
    score: Optional[int] = Field(
        ge=0,
        le=10,
    )
    time_stamp: datetime


class GetLikesResponseModel(PaginatedResponseModel):
    records: List[GetUserLikeRespModel]
