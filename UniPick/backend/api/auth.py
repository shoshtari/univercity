import flask
import structlog
from flask import jsonify, request
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError

import common.configs as configs
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
from utils.jwt_wrapper import create_token

logger = structlog.getLogger()


@public_endpoint
def signup() -> flask.Response | tuple[flask.Response, int]:
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
        user_id = UserRepository.create(
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

    return flask.Response(response=response.model_dump_json(), status=201, content_type="application/json")


@public_endpoint
def login() -> flask.Response:
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
        user_id = UserRepository.check_password(
            username=payload.username,
            password=payload.password,
        )
        response = UserLoginOut(
            access_token=create_token(user_id=user_id, ttl=configs.JWT_TTL),
            ttl=configs.JWT_TTL,
        )
        return flask.Response(response=response.model_dump_json(), status=200, content_type="application/json")

    except InvalidUserPasswordError:
        ans = jsonify({"error": "invalid_username_or_password"})
        ans.status_code = 401
        return ans


def getme() -> flask.Response:
    user_id = flask.g.get("user_id")
    if not isinstance(user_id, int):
        ans = jsonify(
            {"error": "internal_error"}
        )  # since token must be parsed in middleware, it is server error not user error
        ans.status_code = 500
        return ans
    try:
        user_name = UserRepository.get_username_by_id(user_id)
    except UserNotFoundError:
        ans = jsonify({"error": "user_not_found"})
        ans.status_code = 404
        return ans
    response = GetMeOut(
        id=user_id,
        username=user_name,
    )
    return flask.Response(response=response.model_dump_json(), status=200, content_type="application/json")
