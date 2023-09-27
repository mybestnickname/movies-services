from http import HTTPStatus
import math

from flask import request
from flask_restx import Namespace, Resource, fields, reqparse
from marshmallow import Schema, ValidationError
from marshmallow import fields as ma_fields

from services.user_service import get_user_service
from views.req_models import inner_services_token
from views.resp_models import internal_error_model
from views.views_decorators import inner_token_required

users_ns = Namespace(
    'Users',
    description='Operations with users',
    path='/users'
)

# TODO: спрятать вьюху


@users_ns.route('/')
class Users(Resource):

    def __init__(self, api=None, *args, **kwargs):
        super().__init__(api, *args, **kwargs)
        self.user_service = get_user_service()

    user_fields = users_ns.model('User', {
        'id': fields.String,
        'login': fields.String,
        "registration_timestamp": fields.DateTime
    })

    user_list_fields = users_ns.model('UserList', {
        "page": fields.Integer,
        "per_page": fields.Integer,
        "page_count": fields.Integer,
        "total_count": fields.Integer,
        "users": fields.List(fields.Nested(user_fields)),
    })

    class GetReqSchema(Schema):
        roles = ma_fields.String(required=False)
        count_per_page = ma_fields.Integer(required=True)
        page_number = ma_fields.Integer(required=True)

    get_users_req_model = reqparse.RequestParser()
    get_users_req_model.add_argument(
        "roles", type=str, required=False,
    )
    get_users_req_model.add_argument(
        "count_per_page", type=int, required=True,
    )
    get_users_req_model.add_argument(
        "page_number", type=int, required=True,
    )

    get_users_bad_req = users_ns.model(
        'GetUsersBadReqModel',
        {
            "message": fields.String(
                example=(
                    "Wrong inner token!",
                )
            )
        }
    )

    @users_ns.doc(
        responses={
            int(HTTPStatus.OK): ('Success', user_list_fields),
            int(HTTPStatus.INTERNAL_SERVER_ERROR): ('Internal error', internal_error_model),
            int(HTTPStatus.BAD_REQUEST): ("Bad request", get_users_bad_req),
        }
    )
    @users_ns.expect(get_users_req_model, inner_services_token)
    @inner_token_required
    def get(self):
        """
        Get all users with roles filtration
        """
        try:
            data = self.GetReqSchema().load(request.args)
        except ValidationError as err:
            return {"errors": err.messages}, HTTPStatus.BAD_REQUEST

        users = self.user_service.get_users_list(
            roles=data.get("roles"),
            count_per_page=data.get("count_per_page"),
            page_number=data.get('page_number'),
        )

        total_count = self.user_service.get_users_count(
            roles=data.get("roles"),
        )

        return {
            "page": data.get('page_number'),
            "per_page": data.get("count_per_page"),
            "page_count": math.ceil(total_count / data.get("count_per_page")),
            "total_count": total_count,
            "users": users
        }, HTTPStatus.OK


@users_ns.route('/get_by_ids')
class UsersById(Resource):

    def __init__(self, api=None, *args, **kwargs):
        super().__init__(api, *args, **kwargs)
        self.user_service = get_user_service()

    user_fields = users_ns.model('UserById', {
        'id': fields.String,
        'login': fields.String,
        "registration_timestamp": fields.DateTime
    })

    user_list_fields = users_ns.model('UserListById', {
        "users": fields.List(fields.Nested(user_fields)),
    })

    class GetReqSchema(Schema):
        user_ids = ma_fields.String(required=False)

    get_users_by_id_req_model = reqparse.RequestParser()
    get_users_by_id_req_model.add_argument(
        "user_ids", type=str, required=True, help="Users UUIDs separated by commas"
    )

    get_users_bad_req = users_ns.model(
        'GetUsersBadReqModel',
        {
            "message": fields.String(
                example=(
                    "Wrong inner token!",
                )
            )
        }
    )

    @users_ns.doc(
        responses={
            int(HTTPStatus.OK): ('Success', user_list_fields),
            int(HTTPStatus.INTERNAL_SERVER_ERROR): ('Internal error', internal_error_model),
            int(HTTPStatus.BAD_REQUEST): ("Bad request", get_users_bad_req),
        }
    )
    @users_ns.expect(get_users_by_id_req_model, inner_services_token)
    @inner_token_required
    def get(self):
        """
        Get all users with roles filtration
        """
        try:
            data = self.GetReqSchema().load(request.args)
        except ValidationError as err:
            return {"errors": err.messages}, HTTPStatus.BAD_REQUEST

        users = self.user_service.get_users_by_ids(
            user_ids=data.get("user_ids").split(','),
        )

        return {
            "users": users
        }, HTTPStatus.OK
