from datetime import datetime
from typing import Optional
from core.model_config import Base
from pydantic import Field


class ReviewAuthor(Base):
    user_name: str = Field(min_length=3)
    user_id: str


class FilmReview(Base):
    mongo_object_id: Optional[str]
    film_id: str
    text: str = Field(min_length=5)
    author: ReviewAuthor
    timestamp: datetime = Field(
        description="Datetime in ISO 8601 format",
        example="2018-06-13T12:11:13+05:30",
    )
    update_timestamp: Optional[datetime] = Field(
        description="Last updated timestamp in ISO 8601 format",
        example="2018-06-13T12:11:13+05:30",
    )


class ScoreAuthor(ReviewAuthor):
    pass


class FilmReviewScore(Base):
    review_id: str
    author: ScoreAuthor
    score: int = Field(
        ge=0,
        le=10,
    ),
    timestamp: datetime = Field(
        description="Datetime in ISO 8601 format",
        example="2018-06-13T12:11:13+05:30",
    )


class FilmReviewToScore(Base):
    review_id: str
    film_score_id: str
