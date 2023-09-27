import json
from logging import getLogger
from typing import List

from fastapi import APIRouter, Depends, Header

from api.views_decorators import check_roles, inner_token_required
from pkg.storage.redis_storage import get_redis_storage_service, RedisService
from api.models.resp_models import FilmRespModel
from api.models.req_models import NewRecReqModel
from api.errors.httperrors import RecHTTPNotFoundError, StorageInternalError
from services.movies import MoviesService, get_movies_service

logger = getLogger(__name__)

router = APIRouter()


@router.post(
    '/new_rec/',
    tags=["inner"],
    responses={
        201: {
            "description": "Recommendations have been successfully saved",
        },
        500: {
            "description": "Storage error.",
        },
    }
)
@inner_token_required
async def save_rec_list(
        req: NewRecReqModel,
        internal_token=Header(
            description="Internal token for communicating between services"
        ),
        redis_service: RedisService = Depends(get_redis_storage_service)
) -> None:
    """
    Get filtered films list with pagination.
    """
    logger.info(f"Trying to save new reccomendation for user {req.user_id}.")
    if not await redis_service.set_data(
        key=req.user_id,
        data=json.dumps({"recommendations": req.dict()["recommendations"]})
    ):
        raise StorageInternalError
    logger.info(f"New recommendation for user:{req.user_id} have been saved.")


@router.get(
    '/get_rec/',
    response_model=List[FilmRespModel],
    tags=["User's recomendations"],
    responses={
        200: {
            "description": "Array of recommended films.",
        },
        404: {
            "description": "Recommendations not found.",
        },
        500: {
            "description": "Storage error.",
        },
    }
)
@check_roles()
async def get_rec_list(
        token=Header(
            default=None,
            description="JWT token"
        ),
        user_roles=Depends(),
        user_name=Depends(),
        user_id=Depends(),
        redis_service: RedisService = Depends(get_redis_storage_service),
        movies_service: MoviesService = Depends(get_movies_service)
) -> List[FilmRespModel]:
    user_rec = await redis_service.get_data(user_id)
    if not user_rec:
        raise RecHTTPNotFoundError

    movies_rec_result = json.loads(user_rec)
    scores_dict = {movie['movie_id']: movie['rec_score'] for movie in movies_rec_result['recommendations']}

    films = await movies_service.get_films_by_id(list(scores_dict.keys()))

    films_resp = []
    for film in films:
        film_res = FilmRespModel(**film)
        film_res.rec_score = float(scores_dict.get(film_res.id))
        films_resp.append(film_res)

    return films_resp
