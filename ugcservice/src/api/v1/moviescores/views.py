import logging
from uuid import UUID

from api.v1.moviescores.models import (GetAvgMovieScoreRespModel,
                                       ListMoviesLikeResponseModel)
from api.views_decorators import check_roles
from fastapi import APIRouter, Depends, Header, Query, status
from fastapi_limiter.depends import RateLimiter
from pkg.pagination.pagination import Paginator
from services.moviescores.service import (MovieScoreService,
                                          get_movie_scores_service)

logger = logging.getLogger(__name__)

router = APIRouter()

RATE_LIMITER_TIMES = 20
RATE_LIMITER_SEC = 10

responses = {
    status.HTTP_500_INTERNAL_SERVER_ERROR: {
        "description": "UGC storage error.",
        "content": {
            "application/json": {
                "example": {"detail": "UGC storage error."},
            },
        },
    },
    status.HTTP_404_NOT_FOUND: {
        "description": "Movie not found.",
        "content": {
            "application/json": {
                "example": {"detail": "Movie not found."},
            },
        },
    },
    status.HTTP_401_UNAUTHORIZED: {
        "content": {
            "application/json": {
                "example": {
                    "detail": "Action only for authorized users."
                },
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
}


@router.get(
    '/get_movie_scores',
    response_model=ListMoviesLikeResponseModel,
    status_code=status.HTTP_200_OK,
    responses=responses,
    tags=["Movie Scores"],
    dependencies=[Depends(RateLimiter(times=RATE_LIMITER_TIMES, seconds=RATE_LIMITER_SEC))],
)
@check_roles()
async def get_movie_likes(
        token=Header(
            default=None,
            description="JWT token"),
        film_id: UUID = Query(example="4f91f972-f071-4ac9-9c31-55f7ee3bc8aa"),
        paginator: Paginator = Depends(),
        user_roles=Depends(),
        user_id=Depends(),
        user_name=Depends(),
        ugc_service: MovieScoreService = Depends(
            get_movie_scores_service
        ),
) -> ListMoviesLikeResponseModel:
    """Get movie likes from UGC store."""

    result = await ugc_service.get_movie_likes(
        movie_id=str(film_id),
        page_number=paginator.page_number,
        page_size=paginator.page_size
    )
    return ListMoviesLikeResponseModel(**result)


@router.get(
    '/get_avg_movie_scores',
    response_model=GetAvgMovieScoreRespModel,
    status_code=status.HTTP_200_OK,
    responses=responses,
    tags=["Movie Scores"],
    dependencies=[Depends(RateLimiter(times=RATE_LIMITER_TIMES, seconds=RATE_LIMITER_SEC))],
)
async def get_avg_movie_scores(
        film_id: UUID = Query(example="4f91f972-f071-4ac9-9c31-55f7ee3bc8aa"),
        user_name=Depends(),
        ugc_service: MovieScoreService = Depends(
            get_movie_scores_service
        ),
) -> GetAvgMovieScoreRespModel:
    """Get avg movie score from UGC store."""
    result = await ugc_service.get_avg_movie_score(movie_id=str(film_id))
    return result
