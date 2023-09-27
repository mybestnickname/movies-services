
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field
from services.film_reviews.models import FilmReview, FilmReviewScore


# all requests with header which contains user_id
# POST
class ReviewAuthor(BaseModel):
    user_name: str = Field(example="squirrelmail@gmail.com", min_length=3)


class PostFilmReviewReqBody(BaseModel):
    film_id: UUID = Field(example="4f91f972-f071-4ac9-9c31-55f7ee3bc8aa")
    text: str = Field(example="Blah blah blah the film was so boring.", min_length=5)
    author: ReviewAuthor


class PostFilmReviewRespBody(FilmReview):
    pass


# PUT
class PutFilmReviewReqBody(BaseModel):
    review_id: str = Field(example="62ed1c1e4452a84ab5a9f089")
    new_text: str = Field(example="Blah blah blah the film was so cool.", min_length=5)


class PutFilmReviewRespBody(FilmReview):
    pass


# GET
class GetFilmReviewsRespBody(BaseModel):
    total_count: int
    page_count: int
    page_number: int
    page_size: int
    records: List[FilmReview]
    message: Optional[str]


# POST REVIEW SCORE
class PostReviewLikeRespBody(FilmReviewScore):
    mongo_object_id: Optional[str]
