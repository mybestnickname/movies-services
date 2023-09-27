import logging

import aioredis
import uvicorn
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from fastapi.responses import ORJSONResponse


from api.middlewares import RequestContextMiddleware
from core.config import Settings
from db import redis
from core.logger import setup_logging
from api.v1 import recommendations

logger = logging.getLogger()

setup_logging(logger)


app = FastAPI(
    docs_url='/recservice_api/openapi',
    openapi_url='/recservice_api/openapi.json',
    default_response_class=ORJSONResponse,
)

app.add_middleware(RequestContextMiddleware)


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Recommendations service api for online cinema",
        version="1.0.0",
        description="This is the first version of the recommendations service",
        routes=app.routes,
    )
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


@app.on_event('startup')
async def startup():
    logger.info(f"Connecting to Redis {Settings().REC_REDIS_HOST}:{Settings().REC_REDIS_PORT}")
    redis.redis = await aioredis.create_redis_pool(
        (Settings().REC_REDIS_HOST, Settings().REC_REDIS_PORT),
        minsize=10,
        maxsize=20,
    )


@app.on_event('shutdown')
async def shutdown():
    redis.redis.close()
    await redis.redis.wait_closed()

app.add_middleware(RequestContextMiddleware)

app.include_router(recommendations.router, prefix='/recservice_api/v1')

if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        host='0.0.0.0',
        port=8000,
    )
