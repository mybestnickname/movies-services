import logging

import aioredis
import sentry_sdk
import uvicorn
from elasticsearch import AsyncElasticsearch
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from fastapi.responses import ORJSONResponse
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.starlette import StarletteIntegration

from api.metadata.tags_metadata import tags_metadata
from api.middlewares import RequestContextMiddleware
from api.v1 import films, genre, person, inner_views
from core.config import Settings
from db import elastic, redis
from core.logger import setup_logging

logger = logging.getLogger()

setup_logging(logger)

sentry_sdk.init(
    dsn=Settings().MOVIES_SENTRY_SDK,
    integrations=[
        StarletteIntegration(),
        FastApiIntegration(),
    ],
    traces_sample_rate=0.1,
    send_default_pii=True,
)

app = FastAPI(
    docs_url='/movies_api/openapi',
    openapi_url='/movies_api/openapi.json',
    default_response_class=ORJSONResponse,
)

app.add_middleware(RequestContextMiddleware)


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Online cinema api",
        version="1.0.0",
        description="This is the first version of the cinema API made by Vladislav and Nick",
        routes=app.routes,
        tags=tags_metadata
    )
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


@app.on_event('startup')
async def startup():
    logger.info(f"Connecting to Redis {Settings().REDIS_HOST}:{Settings().REDIS_PORT}")
    redis.redis = await aioredis.create_redis_pool(
        (Settings().REDIS_HOST, Settings().REDIS_PORT), minsize=10, maxsize=20
    )
    logger.info(f"Connecting to ES {Settings().ELASTIC_HOST}:{Settings().ELASTIC_PORT}")
    elastic.es = AsyncElasticsearch(
        hosts=[f'{Settings().ELASTIC_HOST}:{Settings().ELASTIC_PORT}']
    )


@app.on_event('shutdown')
async def shutdown():
    redis.redis.close()
    await redis.redis.wait_closed()
    await elastic.es.close()

app.add_middleware(RequestContextMiddleware)


app.include_router(films.router, prefix='/movies_api/v1/films', tags=['films'])
app.include_router(person.router, prefix='/movies_api/v1/person', tags=['person'])
app.include_router(genre.router, prefix='/movies_api/v1/genre', tags=['genre'])
app.include_router(inner_views.router, prefix='/movies_api/v1/inner', tags=['inner'])

if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        host='0.0.0.0',
        port=8000,
    )
