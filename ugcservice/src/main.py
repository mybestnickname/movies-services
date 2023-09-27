import logging
import aioredis
import sentry_sdk
import uvicorn
from aiokafka import AIOKafkaProducer
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from fastapi.responses import ORJSONResponse
from fastapi_limiter import FastAPILimiter
from motor.motor_asyncio import AsyncIOMotorClient
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.starlette import StarletteIntegration

from api.middlewares import RequestContextMiddleware
from api.v1.bookmarks.views import router as bookmarks_router
from api.v1.likes.views import router as user_likes_router
from api.v1.moviescores.views import router as movie_scores_router
from api.v1.moviewatchmark import router as movie_watchmark_router
from api.v1.reviews.views import router as film_reviews_router
from core.config import Settings
from core.logger import setup_logging
from db import kafka, mongo
from db import redis as redis_cashed

logger = logging.getLogger()

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
    docs_url='/ugcservice_api/openapi',
    openapi_url='/ugcservice_api/openapi.json',
    default_response_class=ORJSONResponse,
)
app.add_middleware(RequestContextMiddleware)


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="UGC service api",
        version="1.0.0",
        description="This is the first version of the user generated content service api.",
        routes=app.routes,
    )
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


@app.on_event("startup")
async def startup():
    redis_uri = f"redis://{Settings().REDIS_LIMITER_HOST}:{Settings().REDIS_LIMITER_PORT}/1"
    logger.info(f"Connecting to Redis {redis_uri}")
    redis = await aioredis.from_url(
        redis_uri,
        encoding="utf-8",
        decode_responses=True,
    )
    await FastAPILimiter.init(redis)

    # пока уберу подключение к кафки за ненадобностью TODO: верни
    # logger.info(f"Connecting to Kafka {Settings().KAFKA_HOST}:{Settings().KAFKA_PORT}")
    # kafka.kafka = AIOKafkaProducer(
    #     bootstrap_servers=f'{Settings().KAFKA_HOST}:{Settings().KAFKA_PORT}',
    # )
    # await kafka.kafka.start()

    redis_cashed.redis = redis

    logger.info(f"Connecting to mongo DB {Settings().MONGO_HOST}:{Settings().MONGO_PORT}")
    mongo.mongo = AsyncIOMotorClient(f'{Settings().MONGO_HOST}:{Settings().MONGO_PORT}')


@app.on_event("shutdown")
async def shutdown():
    await redis_cashed.redis.close()
    await FastAPILimiter.close()
    # await kafka.kafka.stop()

app.include_router(movie_watchmark_router, prefix='/ugcservice_api/v1/movie_watchmark')
app.include_router(film_reviews_router, prefix='/ugcservice_api/v1')
app.include_router(user_likes_router, prefix='/ugcservice_api/v1/users_likes')
app.include_router(movie_scores_router, prefix='/ugcservice_api/v1/movie_scores')
app.include_router(bookmarks_router, prefix='/ugcservice_api/v1')


if __name__ == '__main__':
    app_run_port = 8001

    uvicorn.run(
        'main:app',
        host='127.0.0.1',
        port=app_run_port,
        reload=True,
    )
