from http import HTTPStatus

from fastapi import HTTPException

StorageInternalError = HTTPException(
    status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
    detail='Rabbit storage error.',
)

QueueNotFoundException = HTTPException(
    status_code=HTTPStatus.NOT_FOUND,
    detail='Queue is not found in Rabbit storage.',
)

