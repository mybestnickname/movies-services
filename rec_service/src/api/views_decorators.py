import logging
from functools import wraps

from api.errors.httperrors import InnerTokenError, NotAuthorizeException
from core.config import Settings
from services.auth import get_auth_service

logger = logging.getLogger(__name__)


def check_roles():
    def wrapper(fn):
        @wraps(fn)
        async def decorator(*args, **kwargs):
            logger.info(f"Trying to get a response from the auth service.")
            try:
                auth_service = get_auth_service()
                result = await auth_service.validate(kwargs['token'])
                user_roles = result.get('user_roles')
                if not user_roles:
                    raise NotAuthorizeException

                kwargs['user_roles'] = user_roles
                kwargs['user_id'] = result.get('user_id')
                kwargs['user_name'] = result.get('user_name')
                logger.info(f"Token verified.")
            except Exception as ex:
                logger.info(f"Authorization service unavailable. {ex}")
                raise NotAuthorizeException

            if Settings().ENV == 'test':
                kwargs['user_roles'] = ['subscription']

            return await fn(*args, **kwargs)
        return decorator
    return wrapper


def inner_token_required(func):
    @wraps(func)
    async def wrapped(*args, **kwargs):
        logger.info(f"Trying to verify internal token.")
        if kwargs.get('internal_token') != Settings().INNER_KEY:
            raise InnerTokenError
        logger.info(f"Token has been verified.")
        return await func(*args, **kwargs)
    return wrapped
