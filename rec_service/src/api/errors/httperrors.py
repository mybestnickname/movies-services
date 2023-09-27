from http import HTTPStatus

from fastapi import HTTPException

RecHTTPNotFoundError = HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Can't find recommendation for user")

InnerTokenError = HTTPException(
    status_code=HTTPStatus.UNAUTHORIZED,
    detail="Wrong internal token."
)

StorageInternalError = HTTPException(
    status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
    detail='Storage error.',
)

NotAuthorizeException = HTTPException(
    status_code=HTTPStatus.UNAUTHORIZED,
    detail="Action only for authorized users."
)