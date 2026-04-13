import flask
import structlog
from flask import jsonify, request
from pydantic import ValidationError

import common.configs as configs
from api.auth_schema import UserLoginIn, UserLoginOut, UserSignupIn, UserSignupOut
from db import UserRepository
from utils.jwt_wrapper import create_token

logger = structlog.getLogger()

user_repository = UserRepository()


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
        user_id = user_repository.create(
            username=payload.username,
            password=payload.password,
        )
    except Exception as e:
        logger.error("failed user creation", username=payload.username, error=e)
        return jsonify({"error": "username_already_exists"}), 409

    response = UserSignupOut(
        id=user_id,
        username=payload.username,
    )

    return jsonify(response.model_dump()), 201


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
        result, user_id = user_repository.check_password(
            username=payload.username,
            password=payload.password,
        )
        if not result:
            ans = jsonify({"error": "invalid username or password"})
            ans.status_code = 403
            return ans
        response = UserLoginOut(
            access_token=create_token(user_id=user_id, ttl=configs.JWT_TTL),
            ttl=configs.JWT_TTL,
        )
        return jsonify(response.model_dump())

    except Exception as e:
        logger.error("failed check password", username=payload.username, error=e)
        ans = jsonify({"error": "internal error"})
        ans.status_code = 500
        return ans
