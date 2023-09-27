from http import HTTPStatus
from services.user_service import get_user_service

from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt
from views.resp_models import internal_error_model, unauth_error_resp_model

check_token_ns = Namespace(
    'CheckRoles',
    description='Validate jwt token and return user roles.',
    path='/auth'
)


@check_token_ns.route('/check_roles', doc=False)
class CheckRoles(Resource):
    def __init__(self, api=None, *args, **kwargs):
        super().__init__(api, *args, **kwargs)
        self.user_service = get_user_service()

    post_resp_model = check_token_ns.model('CheckRolesRespModel', {
        'message': fields.String(
            example=['subscription'])
    })

    @check_token_ns.doc(
        responses={
            HTTPStatus.OK: ('Success', post_resp_model),

            HTTPStatus.UNAUTHORIZED: (
                'error', unauth_error_resp_model
            ),
            HTTPStatus.INTERNAL_SERVER_ERROR: (
                'Internal error', internal_error_model
            )
        }
    )
    @check_token_ns.param(
        name='Authorization',
        description='jwt token in format "Bearer {jwt}"',
        _in='header')
    @jwt_required(locations='headers')
    def get(self):
        roles = get_jwt().get('sub', {}).get('user_roles')
        user_id = get_jwt().get('sub', {}).get('user_id')
        if not roles:
            roles = ["not_subscription"]
        resp_dict = {
            "user_roles": roles,
            "user_id": user_id
        }

        user = self.user_service.get_user_by_id(user_id)
        if user:
            resp_dict['user_name'] = user.login

        return resp_dict
