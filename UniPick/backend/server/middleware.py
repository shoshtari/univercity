import jwt
from flask import Flask, Response, g, jsonify, request

from utils.jwt_wrapper import parse_token

PUBLIC_ENDPOINTS = {"liveness", "signup", "login"}


def register_middlewares(app: Flask) -> None:

    @app.before_request
    def authenticate() -> None | tuple[Response, int]:
        if request.endpoint in PUBLIC_ENDPOINTS:
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
