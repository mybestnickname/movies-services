from datetime import datetime, timezone, timedelta
import logging
from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, Header, Query, status
from fastapi_limiter.depends import RateLimiter

from api.v1.likes.models import GetLikesResponseModel, GetUserLikeRespModel
from api.views_decorators import check_roles, inner_token_required
from api.errors.httperrors import WrongTimestamps
from services.likes.service import LikesService, get_user_like_service
from pkg.pagination.pagination import Paginator

logger = logging.getLogger(__name__)

router = APIRouter()

RATE_LIMITER_TIMES = 20
RATE_LIMITER_SEC = 10


@router.get(
    '/get_users_like',
    response_model=GetUserLikeRespModel,
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "description": "Internal server error",
            "content": {
                "application/json": {
                    "example": {"detail": "Error occurred while trying to get user like."},
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
            "description": "Like not found",
            "content": {
                "application/json": {
                    "example": {"detail": "Like not found"}
                }
            },
        },
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Not found",
            "content": {
                "application/json": {
                    "example": {"detail": "Like not found"}
                }
            },
        },
    },
    tags=["User Likes"],
    dependencies=[Depends(RateLimiter(times=RATE_LIMITER_TIMES, seconds=RATE_LIMITER_SEC))],
)
@check_roles()
async def get_users_like(
        token=Header(
            default=None,
            description="JWT token"),
        film_id: UUID = Query(example="4f91f972-f071-4ac9-9c31-55f7ee3bc8aa"),
        user_roles=Depends(),
        user_name=Depends(),
        user_id=Depends(),
        ugc_service: LikesService = Depends(
            get_user_like_service,
        ),
) -> GetUserLikeRespModel:
    """Get like to UGC store."""
    result = await ugc_service.get_user_like(user_id=str(user_id), movie_id=str(film_id))
    return result


@router.put(
    '/update_user_like',
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "description": "Internal server error",
            "content": {
                "application/json": {
                    "example": {"detail": "Error occurred while trying to update movie watch mark."},
                },
            },
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "User like not found.",
            "content": {
                "application/json": {
                    "example": {"detail": "User like not found."},
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
    },
    tags=["User Likes"],
    dependencies=[Depends(RateLimiter(times=RATE_LIMITER_TIMES, seconds=RATE_LIMITER_SEC))],
)
@check_roles()
async def update_users_likes(
        token=Header(
            default=None,
            description="JWT token"),
        film_id: UUID = Query(example="4f91f972-f071-4ac9-9c31-55f7ee3bc8aa"),
        like=Query(
            default=0,
            title="Film like",
            description="User Likes 0/10."
        ),
        ugc_service: LikesService = Depends(
            get_user_like_service,
        ),
        user_roles=Depends(),
        user_name=Depends(),
        user_id=Depends()
) -> None:
    """Update like to UGC store."""
    await ugc_service.save_user_like(movie_id=str(film_id), user_id=str(user_id), user_name=user_name, score=like)


@router.post(
    '/add_users_like',
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "description": "Internal server error",
            "content": {
                "application/json": {
                    "example": {"detail": "Error occurred while trying to save user like."},
                },
            },
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Like not found",
            "content": {
                "application/json": {
                    "example": {"detail": "Like not found"}
                }
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
    },
    tags=["User Likes"],
    dependencies=[Depends(RateLimiter(times=RATE_LIMITER_TIMES, seconds=RATE_LIMITER_SEC))],
)
@check_roles()
async def add_users_likes(
        token=Header(
            default=None,
            description="JWT token"),
        film_id: UUID = Query(example="4f91f972-f071-4ac9-9c31-55f7ee3bc8aa"),
        like=Query(
            default=0,
            title="Film like",
            description="User Likes 0/10."
        ),
        ugc_service: LikesService = Depends(
            get_user_like_service,
        ),
        user_name=Depends(),
        user_roles=Depends(),
        user_id=Depends()
) -> None:
    """Add like to UGC store."""

    await ugc_service.save_user_like(
        movie_id=str(film_id),
        user_id=str(user_id),
        user_name=user_name,
        score=int(like))


@router.delete(
    '/delete_users_like',
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "description": "Internal server error",
            "content": {
                "application/json": {
                    "example": {"detail": "Error occurred while trying to delete user like."},
                },
            },
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Like not found",
            "content": {
                "application/json": {
                    "example": {"detail": "Like not found"}
                }
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
    },
    tags=["User Likes"],
    dependencies=[Depends(RateLimiter(times=RATE_LIMITER_TIMES, seconds=RATE_LIMITER_SEC))],
)
@check_roles()
async def delete_user_like(
        token=Header(
            default=None,
            description="JWT token"),
        film_id: UUID = Query(example="4f91f972-f071-4ac9-9c31-55f7ee3bc8aa"),
        user_roles=Depends(),
        user_id=Depends(),
        user_name=Depends(),
        ugc_service: LikesService = Depends(
            get_user_like_service,
        ),
) -> None:
    """Delete like to UGC store."""
    await ugc_service.delete_user_like(user_id=str(user_id), movie_id=str(film_id))


@router.get(
    '/get_likes',
    response_model=GetLikesResponseModel,
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "description": "Internal server error",
            "content": {
                "application/json": {
                    "example": {"detail": "Error occurred while trying to get user like."},
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
    tags=["User Likes"],
)
@inner_token_required
async def get_users_like(
        start_date: Optional[datetime] = Query(
            description="Timestamp in ISO format. Default: current utc datetime - 7days",
            default=None
        ),
        end_date: Optional[datetime] = Query(
            description="Timestamp in ISO format. Default: current utc datetime",
            default=None
        ),
        internal_token=Header(
            description="Internal token for communicating between services"
        ),
        like_service: LikesService = Depends(
            get_user_like_service,
        ),
        paginator: Paginator = Depends(),
):
    """Get likes from UGC store."""
    if not start_date:
        start_date = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()
    if not end_date:
        end_date = datetime.now(timezone.utc).isoformat()

    if start_date > end_date:
        raise WrongTimestamps

    result = await like_service.get_likes(
        start_date=start_date,
        end_date=end_date,
        page_number=paginator.page_number,
        page_size=paginator.page_size
    )
    return result
