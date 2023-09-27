from http import HTTPStatus

from fastapi import HTTPException

StorageInternalError = HTTPException(
    status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
    detail='UGC storage error.',
)
UserLikeHTTPNotFoundError = HTTPException(
    status_code=HTTPStatus.NOT_FOUND,
    detail='User like not found.',
)
MovieScoreHTTPNotFoundError = HTTPException(
    status_code=HTTPStatus.NOT_FOUND,
    detail='Movie not found.',
)
NotAuthorizeException = HTTPException(
    status_code=HTTPStatus.UNAUTHORIZED,
    detail="Action only for authorized users."
)
ReviewNotFoundError = HTTPException(
    status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
    detail='Review not found.',
)
ReviewUpdateError = HTTPException(
    status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
    detail="Can't edit someone else's review.",
)
ReviewDeleteError = HTTPException(
    status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
    detail="Can't remove someone else's review.",
)
NotFoundDeletingReviewError = HTTPException(
    status_code=HTTPStatus.NOT_FOUND,
    detail="Can't found review to delete.",
)

NotFoundReviewToLikeError = HTTPException(
    status_code=HTTPStatus.NOT_FOUND,
    detail="Can't found review to set score.",
)

NotFoundReviewToLinkError = HTTPException(
    status_code=HTTPStatus.NOT_FOUND,
    detail="Can't found film review to link film score.",
)

NotFoundFilmScoreToLinkError = HTTPException(
    status_code=HTTPStatus.NOT_FOUND,
    detail="Can't found film score to link film review.",
)

DifferentFilmIdsError = HTTPException(
    status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
    detail="Film id in review is different than id in film score.",
)
BookmarkNotFoundError = HTTPException(
    status_code=HTTPStatus.NOT_FOUND,
    detail='Bookmark not found.',
)

InnerTokenError = HTTPException(
    status_code=HTTPStatus.UNAUTHORIZED,
    detail="Wrong internal token."
)

WrongTimestamps = HTTPException(
    status_code=HTTPStatus.BAD_REQUEST,
    detail="Wrong start/end timestamps"
)
