import datetime
from uuid import UUID

from api.errors.httperrors import StorageInternalError
from fastapi import APIRouter, Depends, status
from fastapi_limiter.depends import RateLimiter
from pydantic import BaseModel, Field
from services.moviewatchmark import (MovieWatchMarkService,
                                     get_watchmark_service)

router = APIRouter()

RATE_LIMITER_TIMES = 20
RATE_LIMITER_SEC = 10


class PostMovieWatchMarkReqBody(BaseModel):
    film_id: UUID = Field(example="4f91f972-f071-4ac9-9c31-55f7ee3bc8aa")
    user_id: UUID = Field(example="75c89c44-e146-4918-8368-9cc78c48f491", default=None)
    timestamp: datetime.time = Field(
        description="Time in ISO 8601 format",
        example="01:23:55.003",
    )


@router.post(
    '/viewlabel',
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "description": "Internal server error",
            "content": {
                "application/json": {
                    "example": {"detail": "Error occurred while trying to save movie watch mark."},
                },
            },
        },
        status.HTTP_429_TOO_MANY_REQUESTS: {
            "content": {
                "application/json": {
                    "example": {"detail": "Too Many Requests"},
                },
            },
        },
    },
    tags=["Movie Watch Mark"],
    dependencies=[Depends(RateLimiter(times=RATE_LIMITER_TIMES, seconds=RATE_LIMITER_SEC))],
)
async def save_movie_watchmark(
        body_req: PostMovieWatchMarkReqBody,
        movies_watchmark_service: MovieWatchMarkService = Depends(
            get_watchmark_service,
        ),
) -> None:
    """Send movie view label(timestamp) to UGC store."""
    if await movies_watchmark_service.save_watchmark(
            film_id=body_req.film_id,
            user_id=body_req.user_id,
            timestamp=body_req.timestamp,
    ):
        return
    raise StorageInternalError
