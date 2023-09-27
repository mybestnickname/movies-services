from contextvars import ContextVar
from typing import Optional

from starlette.middleware.base import (BaseHTTPMiddleware,
                                       RequestResponseEndpoint)
from starlette.requests import Request

REQUEST_ID_CTX_KEY = "request_id_ctx"

_request_id_ctx_var: ContextVar[str] = ContextVar(REQUEST_ID_CTX_KEY, default=None)


def get_request_id() -> Optional[str]:
    return _request_id_ctx_var.get()


class RequestContextMiddleware(BaseHTTPMiddleware):

    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint,
    ):
        req_id = request.headers.get('X-Request-Id')
        request_id_ctx = _request_id_ctx_var.set(req_id)
        response = await call_next(request)
        _request_id_ctx_var.reset(request_id_ctx)
        if req_id:
            response.headers["x-request-id"] = req_id
        return response
