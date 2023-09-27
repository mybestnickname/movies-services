from datetime import datetime
from typing import Optional
from uuid import UUID
from core.model_config import Base
from pydantic import Field


class FilmBookmark(Base):
    mongo_object_id: Optional[str]
    film_id: UUID
    user_id: UUID
    film_name: str = Field(min_length=3)
    timestamp: datetime = Field(
        description="Datetime in ISO 8601 format",
        example="2018-06-13T12:11:13+05:30",
    )
