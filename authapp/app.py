from authlib.integrations.flask_client import OAuth

from config import config
import logging
import os

import sentry_sdk
from flask import Flask, request
from flask_jwt_extended import JWTManager
from flask_restx import Api
from sentry_sdk.integrations.flask import FlaskIntegration

from auth_jwt import init_jwt
from clicommands import init_clicommands
from config import Config, config
from db import init_db
from jaeger_tracer import configure_tracer
from limiter import init_limiter

from models.auth import AuthHistory
from models.roles import Role, UserRole
from models.tokens import UserRefreshToken
from models.user import User
from oauth import init_oauth
from routes import register_routes
from logger import setup_logging

logger = logging.getLogger()


setup_logging(logger)

sentry_sdk.init(
    dsn=Config().AUTH_SENTRY_SDK,
    integrations=[
        FlaskIntegration(),
    ],
    traces_sample_rate=1.0,
)

app = Flask(__name__)

app.config.from_object(
    config.get(os.environ.get('ENV', 'default'))
)

jwt = JWTManager(app)

init_db(app)

init_jwt(app)

api = Api(
    app,
    prefix='/auth_api/v1',
    version='1.0',
    title='Auth Flask Api',
    description='A simple jwt token auth.',
    doc='/auth_api/doc/'
)
register_routes(api)

init_clicommands(app)

init_oauth(app)

init_limiter(app)

configure_tracer(app)

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8000)
