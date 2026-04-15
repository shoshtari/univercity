from typing import Callable, ParamSpec, TypeVar

import jwt
from flask import Flask, Response, g, jsonify, request

from utils.jwt_wrapper import parse_token

P = ParamSpec("P")
R = TypeVar("R")


def public_endpoint(func: Callable[P, R]) -> Callable[P, R]:
    """
    this decorator is used to mark an endpoint as public, which means it can be accessed without authentication.
    """
    setattr(func, "_is_public", True)
    return func


def register_middlewares(app: Flask) -> None:

    @app.before_request
    def authenticate() -> None | tuple[Response, int]:

        endpoint = request.endpoint
        if endpoint is None:
            return None

        view_func = app.view_functions.get(endpoint)
        if view_func and getattr(view_func, "_is_public", False):
            return None

        auth = request.headers.get("Authorization")
        if not auth or not auth.startswith("Bearer "):
            return jsonify({"error": "missing_token"}), 401

        token = auth.removeprefix("Bearer ").strip()

        try:
            user_id = parse_token(token)
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "token_expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "invalid_token"}), 401

        g.user_id = user_id
        return None

    return None
