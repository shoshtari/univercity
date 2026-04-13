import structlog
from flask import Flask
from waitress import serve

import api
from common import configs

logger = structlog.get_logger()


def create_app() -> Flask:
    app = Flask(__name__)

    app.add_url_rule("/liveness", view_func=api.liveness, methods=["GET"])
    app.add_url_rule("/auth/signup", view_func=api.signup, methods=["POST"])
    app.add_url_rule("/auth/login", view_func=api.login, methods=["POST"])

    return app


def runserver() -> None:
    app = create_app()
    logger.info(
        "Starting UniPick backend server",
        host=configs.WEBSERVER_HOST,
        port=configs.WEBSERVER_PORT,
    )
    serve(
        app,
        host=configs.WEBSERVER_HOST,
        port=configs.WEBSERVER_PORT,
        threads=configs.WEBSERVER_THREADS,
        connection_limit=configs.WEBSERVER_CONNECTION_LIMIT,
    )
