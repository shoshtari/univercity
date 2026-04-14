import structlog
from flask import Flask
from waitress import serve

from common import configs
from server.middleware import register_middlewares
from server.routes import register_routes

logger = structlog.get_logger()


def create_app() -> Flask:
    app = Flask(__name__)

    register_middlewares(app)
    register_routes(app)

    return app


def create_and_run_app() -> None:
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
