import structlog
from flask import Flask, Response, jsonify
from flask_compress import Compress
from flask_cors import CORS
from pydantic import ValidationError

from common.configs import Settings, load_settings
from common.initialize import init_dependency
from server.middleware import register_middlewares
from server.routes import register_routes

logger = structlog.get_logger()


def handle_validation_error(e: ValidationError) -> tuple[Response, int]:
    response = {
        "error": "validation_error",
        "details": e.errors(),
    }
    return jsonify(response), 400


def create_app(settings: Settings) -> Flask:
    app = Flask(__name__)
    Compress(app)
    CORS(app, supports_credentials=True, origins=settings.CORS_ORIGINS)

    deps = init_dependency(settings)

    register_middlewares(app=app, jwt_handler=deps.jwt_handler, settings=settings)
    register_routes(
        app=app,
        user_repository=deps.user_repository,
        course_repository=deps.course_repository,
        user_course_repository=deps.user_course_repository,
        jwt_handler=deps.jwt_handler,
    )

    app.register_error_handler(ValidationError, handle_validation_error)

    return app


def create_and_run_app() -> None:
    settings = load_settings()

    app = create_app(settings)

    logger.info(
        "Starting UniPick backend server",
        host=settings.WEBSERVER.HOST,
        port=settings.WEBSERVER.PORT,
        wsgi_server=settings.WEBSERVER.WSGI,
    )
    match settings.WEBSERVER.WSGI:
        case "flask":
            app.run(
                host=settings.WEBSERVER.HOST,
                port=settings.WEBSERVER.PORT,
                debug=True,
            )
        case "waitress":

            from waitress import serve

            serve(
                app,
                host=settings.WEBSERVER.HOST,
                port=settings.WEBSERVER.PORT,
                threads=settings.WEBSERVER.THREADS,
                connection_limit=settings.WEBSERVER.CONNECTION_LIMIT,
            )
        case _:
            raise ValueError(f"Invalid WSGI server: {settings.WEBSERVER.WSGI}")
