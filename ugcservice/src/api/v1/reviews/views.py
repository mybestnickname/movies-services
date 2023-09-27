import logging
from uuid import UUID

from api.v1.reviews.models import (GetFilmReviewsRespBody,
                                   PostFilmReviewReqBody,
                                   PostFilmReviewRespBody,
                                   PostReviewLikeRespBody,
                                   PutFilmReviewReqBody, PutFilmReviewRespBody)
from api.views_decorators import auth_required
from fastapi import APIRouter, Depends, Header, Query, status
from fastapi_limiter.depends import RateLimiter
from pkg.pagination.pagination import Paginator
from services.film_reviews.service import ReviewsService, get_reviews_service

RATE_LIMITER_TIMES = 20
RATE_LIMITER_SEC = 10

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix='/reviews',
    tags=["Film Reviews"]
)


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_201_CREATED: {
            "description": "OK",
            "content": {
                "application/json": {
                    "example": {
                        "mongo_object_id": "62ed2f91bde5d5f330a1f5ce",
                        "film_id": "4f91f972-f071-4ac9-9c31-55f7ee3bc8aa",
                        "text": "Blah blah blah the film was so cool.",
                        "author": {
                                "user_name": "squirrelmail@gmail.com",
                                "user_id": "e1c894ea-8ccd-4189-a9ed-bf387222ea07"
                        },
                        "timestamp": "2022-08-05T14:56:17.668000",
                        "update_timestamp": "2022-08-05T16:01:25.720304"
                    },
                },
            },
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "description": "Internal server error",
            "content": {
                "application/json": {
                    "example": {"detail": "Error occurred while trying to add new film review."},
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
        status.HTTP_422_UNPROCESSABLE_ENTITY: {
            "content": {
                "application/json": {
                    "example": {
                        "detail": [
                            {
                                "loc": [
                                    "body",
                                    "text"
                                ],
                                "msg": "ensure this value has at least 5 characters",
                                "type": "value_error.any_str.min_length",
                                "ctx": {
                                    "limit_value": 5
                                }
                            }
                        ]
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
async def add_new_film_review(
        body_req: PostFilmReviewReqBody,
        token: str = Header(description="Jwt access token"),
        reviews_service: ReviewsService = Depends(
            get_reviews_service,
        ),
        user_name=Depends(),
        user_id=Depends()
) -> PostFilmReviewRespBody:
    """Add new film review."""
    result_dict = await reviews_service.save_film_review(user_id, body_req.dict())
    return PostFilmReviewRespBody(**result_dict)


@router.put(
    "/",
    responses={
        status.HTTP_200_OK: {
            "description": "OK",
            "content": {
                "application/json": {
                    "example": {
                        "mongo_object_id": "62ed2f91bde5d5f330a1f5ce",
                        "film_id": "4f91f972-f071-4ac9-9c31-55f7ee3bc8aa",
                        "text": "Blah blah blah the film was so cool.",
                        "author": {
                            "user_name": "squirrelmail@gmail.com",
                            "user_id": "e1c894ea-8ccd-4189-a9ed-bf387222ea07"
                        },
                        "timestamp": "2022-08-05T14:56:17.668000",
                        "update_timestamp": "2022-08-05T16:01:25.720304"
                    },
                },
            },
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "description": "Internal server error",
            "content": {
                "application/json": {
                    "example": {"detail": "Error occurred while trying to update film review."},
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
        status.HTTP_422_UNPROCESSABLE_ENTITY: {
            "content": {
                "application/json": {
                    "example": {
                        "detail": [
                            {
                                "loc": [
                                    "body",
                                    "text"
                                ],
                                "msg": "ensure this value has at least 5 characters",
                                "type": "value_error.any_str.min_length",
                                "ctx": {
                                    "limit_value": 5
                                }
                            }
                        ],
                        "detail_2": "Review not found.",
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
async def update_film_review(
        body_req: PutFilmReviewReqBody,
        token: str = Header(description="Jwt access token"),
        reviews_service: ReviewsService = Depends(
            get_reviews_service,
        ),
        user_name=Depends(),
        user_id=Depends()
) -> PutFilmReviewRespBody:
    """Update film review by review_id"""
    result_dict = await reviews_service.upgrade_film_review(
        user_id=user_id,
        review_id=body_req.review_id,
        new_text=body_req.new_text
    )
    return PutFilmReviewRespBody(**result_dict)


@router.delete(
    "/",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_404_NOT_FOUND: {
            "description": "Can't found review to delete.",
            "content": {
                "application/json": {
                    "example": {"detail": "Can't found review to delete."},
                },
            },
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "description": "Internal server error",
            "content": {
                "application/json": {
                    "example": {"detail": "Error occurred while trying to remove film review."},
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
        status.HTTP_422_UNPROCESSABLE_ENTITY: {
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Can't remove someone else's review",
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
async def remove_film_review(
    review_id: str = Query(
        description="Review id for delete",
        example="22ed3c1e4452b84aa5a6f089"
    ),
    token: str = Header(description="Jwt access token"),
    reviews_service: ReviewsService = Depends(
        get_reviews_service,
    ),
    user_name=Depends(),
    user_id=Depends()
) -> None:
    """Remove film review by review_id"""
    await reviews_service.remove_film_review(
        user_id=user_id,
        review_id=review_id,
    )


@router.get(
    "/film_reviews/",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "description": "Internal server error",
            "content": {
                "application/json": {
                    "example": {"detail": "Error occurred while trying to get film reviews."},
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
    dependencies=[Depends(RateLimiter(times=RATE_LIMITER_TIMES, seconds=RATE_LIMITER_SEC))],
)
async def get_film_reviews(
    film_id: UUID = Query(
        description="Film id to show review list.",
        example="17c25cdd-b5bd-4878-a0f5-5973e71e8adb"
    ),
    paginator: Paginator = Depends(),
    reviews_service: ReviewsService = Depends(
        get_reviews_service,
    ),
) -> GetFilmReviewsRespBody:
    """Get paginated film review list by film_id"""
    docs_count_to_skip = (paginator.page_number - 1) * paginator.page_size
    result_dict = await reviews_service.get_film_reviews(
        film_id=film_id,
        docs_count_to_skip=docs_count_to_skip,
        page_size=paginator.page_size,
    )
    result_dict['page_number'] = paginator.page_number
    result_dict['page_size'] = paginator.page_size

    return GetFilmReviewsRespBody(**result_dict)


@router.post(
    "/review_score/",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: {
            "description": "Review score has been added.",
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "description": "Internal server error",
            "content": {
                "application/json": {
                    "example": {"detail": "Error occurred while trying to like film review."},
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
            "description": "Can't found review to set score.",
            "content": {
                "application/json": {
                    "example": {"detail": "Can't found review to set score."},
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
async def set_film_review_score(
    review_id: str = Query(
        description="Review id for score set",
        example="22ed3c1e4452b84aa5a6f089"
    ),
    score: int = Query(example=7, ge=0, le=10),
    token: str = Header(description="Jwt access token"),
    reviews_service: ReviewsService = Depends(
        get_reviews_service,
    ),
    user_id=Depends(),
    user_name=Depends(),
) -> PostReviewLikeRespBody:
    """Set user score for film review"""
    review_score_dict = await reviews_service.set_film_review_score(
        review_id=review_id,
        user_id=user_id,
        user_name=user_name,
        score=score,
    )
    review_score_dict['mongo_object_id'] = str(review_score_dict['_id'])
    return PostReviewLikeRespBody(**review_score_dict)


@router.post(
    "/link_film_score/",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: {
            "description": "Film score has been linked to review.",
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "description": "Internal server error",
            "content": {
                "application/json": {
                    "example": {"detail": "Error occurred while trying to link film score to review."},
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
        status.HTTP_422_UNPROCESSABLE_ENTITY: {
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Film id in review is different that id in film score.",
                    },
                },
            },
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Can't found review/film_score",
            "content": {
                "application/json": {
                    "example": {
                        "detail_1": "Can't found film review to link film score.",
                        "detail_2": "Can't found film score to link film review."
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
async def link_film_score_to_review(
    review_id: str = Query(
        description="Film review _id",
        example="22ed3c1e4452b84aa5a6f089"
    ),
    film_score_id: str = Query(
        description="Film score _id",
        example="33fd3c5e4452b24ab4a6f029"
    ),
    token: str = Header(description="Jwt access token"),
    reviews_service: ReviewsService = Depends(
        get_reviews_service,
    ),
    user_id=Depends(),
    user_name=Depends(),
) -> None:
    """Link user film score to review"""
    await reviews_service.link_film_score_to_review(
        review_id=review_id,
        film_score_id=film_score_id,
        user_id=user_id,
        user_name=user_name,
    )
