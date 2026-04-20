import flask
import structlog
from flask import jsonify, request
from flask.views import MethodView
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError

from api.auth_schema import (
    GetMeOut,
    UserLoginIn,
    UserLoginOut,
    UserSignupIn,
    UserSignupOut,
)
from common.errors import InvalidUserPasswordError, UserNotFoundError
from db import UserRepository
from server.middleware import public_endpoint
from utils.jwt_wrapper import JWTHandler

logger = structlog.getLogger()


class SignupView(MethodView):
    decorators = [public_endpoint]

    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    def post(self) -> flask.Response | tuple[flask.Response, int]:
        try:
            payload = UserSignupIn.model_validate(request.get_json())
        except ValidationError as e:
            ans = jsonify(
                {
                    "error": "validation_error",
                    "details": e.errors(),
                }
            )
            ans.status = 400
            return ans

        try:
            user_id = self.user_repository.create(
                username=payload.username,
                password=payload.password,
            )
        except IntegrityError as e:
            logger.error("failed user creation", username=payload.username, error=e)
            return jsonify({"error": "username_already_exists"}), 409

        response = UserSignupOut(
            id=user_id,
            username=payload.username,
        )

        return flask.Response(
            response=response.model_dump_json(),
            status=201,
            content_type="application/json",
        )


class LoginView(MethodView):
    def __init__(self, user_repository: UserRepository, jwt_handler: JWTHandler):
        self.user_repository = user_repository
        self.jwt_handler = jwt_handler

    decorators = [public_endpoint]

    def post(self) -> flask.Response:
        try:
            payload = UserLoginIn.model_validate(request.get_json())
        except ValidationError as e:
            ans = jsonify(
                {
                    "error": "validation_error",
                    "details": e.errors(),
                }
            )
            ans.status = 400
            return ans

        try:
            user_id = self.user_repository.check_password(
                username=payload.username,
                password=payload.password,
            )
            response = UserLoginOut(
                access_token=self.jwt_handler.create_token(
                    user_id=user_id,
                ),
                ttl=self.jwt_handler.ttl,
            )
            return flask.Response(
                response=response.model_dump_json(),
                status=200,
                content_type="application/json",
            )

        except InvalidUserPasswordError:
            ans = jsonify({"error": "invalid_username_or_password"})
            ans.status_code = 401
            return ans


class GetmeView(MethodView):
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    def get(self) -> flask.Response:
        user_id = flask.g.get("user_id")
        if not isinstance(user_id, int):
            ans = jsonify(
                {"error": "internal_error"}
            )  # since token must be parsed in middleware, it is server error not user error
            ans.status_code = 500
            return ans
        try:
            user_name = self.user_repository.get_username_by_id(user_id)
        except UserNotFoundError:
            ans = jsonify({"error": "user_not_found"})
            ans.status_code = 404
            return ans
        response = GetMeOut(
            id=user_id,
            username=user_name,
        )
        return flask.Response(
            response=response.model_dump_json(),
            status=200,
            content_type="application/json",
        )
