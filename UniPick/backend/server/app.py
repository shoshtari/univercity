import structlog
from flask import Flask
from flask_compress import Compress

from common import configs
from server.middleware import register_middlewares
from server.routes import register_routes

logger = structlog.get_logger()


def create_app() -> Flask:
    app = Flask(__name__)
    Compress(app)

    register_middlewares(app)
    register_routes(app)

    return app


def create_and_run_app() -> None:
    app = create_app()

    logger.info(
        "Starting UniPick backend server",
        host=configs.WEBSERVER_HOST,
        port=configs.WEBSERVER_PORT,
        wsgi_server=configs.WSGI_SERVER,
    )
    match configs.WSGI_SERVER:
        case "flask":
            app.run(
                host=configs.WEBSERVER_HOST,
                port=configs.WEBSERVER_PORT,
                debug=True,
            )
        case "waitress":

            from waitress import serve

            serve(
                app,
                host=configs.WEBSERVER_HOST,
                port=configs.WEBSERVER_PORT,
                threads=configs.WEBSERVER_THREADS,
                connection_limit=configs.WEBSERVER_CONNECTION_LIMIT,
            )
        case _:
            raise ValueError(f"Invalid WSGI server: {
                             configs.WSGI_SERVER}")
