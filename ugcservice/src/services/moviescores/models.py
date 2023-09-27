from datetime import datetime
from typing import Optional
from core.model_config import Base
from pydantic import Field


class UserLike(Base):
    movie_id: str
    user_id: str
    user_name: str
    score: Optional[int] = Field(
        ge=0,
        le=10,
    )
    time_stamp: datetime
