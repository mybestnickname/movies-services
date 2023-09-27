from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, Header
from pydantic import BaseModel

from api.views_decorators import inner_token_required
from services.films import FilmService, get_film_service
from api.models.resp_models import FilmRespModel

router = APIRouter()


class GetFilmsByIdReqModel(BaseModel):
    ids: List[UUID]

    class Config:
        schema_extra = {
            "example": {
                "ids": [
                    "11b75468-afb6-4721-bd4f-2eccffc546c2",
                    "3f1dcb88-ebba-4b45-acb5-e6ddc723b632",
                    "19c21be1-3c42-448d-a088-cd5d61e26710"
                ],
            }
        }


@router.post(
    '/films_by_id/',
    response_model=List[FilmRespModel],
    tags=["inner"],
    responses={
        200: {
            "description": "Paginated filtered films array.",
        },
    }
)
@inner_token_required
async def get_films_list(
        req: GetFilmsByIdReqModel,
        internal_token=Header(
            description="Internal token for communicating between services"
        ),
        film_service: FilmService = Depends(get_film_service)
) -> List[FilmRespModel]:
    """
    Get filtered films list with pagination.
    """
    return await film_service.get_films_by_id(req.ids)
