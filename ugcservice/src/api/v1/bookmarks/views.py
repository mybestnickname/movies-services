import logging
from uuid import UUID

from api.v1.bookmarks.models import ListFilmBookmarkResponseModel
from api.views_decorators import auth_required
from fastapi import APIRouter, Depends, Header, Query, status
from fastapi_limiter.depends import RateLimiter
from pkg.pagination.pagination import Paginator
from services.bookmarks.service import BookmarksService, get_bookmarks_service

RATE_LIMITER_TIMES = 20
RATE_LIMITER_SEC = 10

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix='/bookmarks',
    tags=["Film Bookmarks"]
)


@router.post(
    "/",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: {
            "description": "Film has been added to bookmarks.",
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "description": "Internal server error",
            "content": {
                "application/json": {
                    "example": {"detail": "Error occurred while trying to add film to bookmarks."},
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
        status.HTTP_404_NOT_FOUND: {
            "description": "Can't found film by id.",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Can't found film.",
                    },
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
    },
    dependencies=[Depends(RateLimiter(times=RATE_LIMITER_TIMES, seconds=RATE_LIMITER_SEC))],
)
@auth_required
async def add_film_to_bookmarks(
    film_id: UUID = Query(
        description="Film id to add in bookmarks.",
        example="17c25cdd-b5bd-4878-a0f5-5973e71e8adb"
    ),
    film_name: str = Query(
        description="Film name to add in bookmarks.",
        example="Star Wars: Episode V - The Empire Strikes Back"
    ),
    token: str = Header(description="Jwt access token"),
    bookmarks_service: BookmarksService = Depends(
        get_bookmarks_service,
    ),
    user_id=Depends(),
    user_name=Depends(),
) -> None:
    """Add film to bookmarks."""
    await bookmarks_service.save_film_in_bookmarks(
        film_id=film_id,
        film_name=film_name,
        user_id=user_id,
        user_name=user_name,
    )
    return None


@router.get(
    "/get_bookmarks",
    status_code=status.HTTP_200_OK,
    response_model=ListFilmBookmarkResponseModel,
    responses={
        status.HTTP_200_OK: {
            "description": "User bookmarks.",
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "description": "Internal server error",
            "content": {
                "application/json": {
                    "example": {"detail": "Error occurred while trying to get bookmarks."},
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
        status.HTTP_404_NOT_FOUND: {
            "description": "Can't found film by id.",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Can't found film.",
                    },
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
    },
    dependencies=[Depends(RateLimiter(times=RATE_LIMITER_TIMES, seconds=RATE_LIMITER_SEC))],
)
@auth_required
async def get_user_bookmarks(
    token: str = Header(description="Jwt access token"),
    bookmarks_service: BookmarksService = Depends(
        get_bookmarks_service,
    ),
    paginator: Paginator = Depends(),
    user_id=Depends(),
    user_name=Depends()
) -> ListFilmBookmarkResponseModel:
    """get user bookmarks."""
    result = await bookmarks_service.get_bookmarks(
        user_id=user_id,
        page_number=paginator.page_number,
        page_size=paginator.page_size
    )
    return result


@router.delete(
    "/delete_bookmark",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: {
            "description": "Bookmark has been deleted.",
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "description": "Internal server error",
            "content": {
                "application/json": {
                    "example": {"detail": "Error occurred while trying to delete bookmarks."},
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
        status.HTTP_404_NOT_FOUND: {
            "description": "Can't found bookmark by mongo id.",
            "content": {
                "application/json": {
                    "example": {
                        "detail": 'Bookmarks not found.',
                    },
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
    },
    dependencies=[Depends(RateLimiter(times=RATE_LIMITER_TIMES, seconds=RATE_LIMITER_SEC))],
)
@auth_required
async def delete_bookmark(
    film_id: UUID = Query(
        description="Film id to add in bookmarks.",
        example="17c25cdd-b5bd-4878-a0f5-5973e71e8adb"
    ),
    bookmark_id: str = Query(
        description="id in mongo.",
        example="62f2bc1119beaebc9bd997fe"
    ),
    token: str = Header(description="Jwt access token"),
    bookmarks_service: BookmarksService = Depends(
        get_bookmarks_service,
    ),
    user_id=Depends(),
    user_name=Depends()
) -> None:
    """delete bookmark."""
    await bookmarks_service.delete_bookmark(
        film_id=str(film_id),
        bookmark_id=bookmark_id,
        user_id=user_id
    )
    return None

