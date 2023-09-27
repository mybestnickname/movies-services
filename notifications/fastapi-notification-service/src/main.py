import logging

import backoff
import sentry_sdk
import uvicorn

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from fastapi.responses import ORJSONResponse

from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.starlette import StarletteIntegration

from api.middlewares import RequestContextMiddleware
from aio_pika import connect as rabbit_connect

from api.v1.task.views import router as send_to_rabbit_router
from core.config import Settings
from core.logger import setup_logging
from broker import rabbit
from core.req_handler import create_backoff_hdlr

logger = logging.getLogger()
back_off_hdlr = create_backoff_hdlr(logger)

setup_logging(logger)

sentry_sdk.init(
    dsn=Settings().UGC_SENTRY_SDK,
    integrations=[
        StarletteIntegration(),
        FastApiIntegration(),
    ],
    traces_sample_rate=1.0,
    send_default_pii=True,
)

app = FastAPI(
    docs_url='/notifications_service_api/openapi',
    openapi_url='/notifications_service_api/openapi.json',
    default_response_class=ORJSONResponse,
)
app.add_middleware(RequestContextMiddleware)


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Notification service api",
        version="1.0.0",
        description="This is the first version of notifications service api.",
        routes=app.routes,
    )
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


@app.on_event("startup")
@backoff.on_exception(
    backoff.fibo,
    ConnectionError,
    max_time=15,
    max_tries=100,
    on_backoff=back_off_hdlr,
)
async def startup():
    logger.info(f"Connecting to RABBIT MQ {Settings().RABBIT_HOST}:{Settings().RABBIT_PORT}")
    try:
        rabbit_connection = await rabbit_connect(
            host=Settings().RABBIT_HOST,
            port=Settings().RABBIT_PORT,
            login=Settings().RABBIT_USER,
            password=Settings().RABBIT_PASSWORD)
    except Exception as ex:
        logger.info(f"Error connecting to RABBßIT MQ {Settings().RABBIT_HOST}:{Settings().RABBIT_PORT} {ex}")
        raise ConnectionError
    rabbit.rabbit_channel = await rabbit_connection.channel()


@app.on_event("shutdown")
async def shutdown():
    await rabbit.rabbit_channel.close()


app.include_router(send_to_rabbit_router, prefix='/notifications_service_api/v1/send')

if __name__ == '__main__':
    app_run_port = 8000

    uvicorn.run(
        'main:app',
        host='127.0.0.1',
        port=app_run_port,
        reload=True,
    )
