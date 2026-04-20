import structlog
from flask import Flask
from flask_compress import Compress

import db
from common.configs import Settings, settings
from server.middleware import register_middlewares
from server.routes import register_routes
from utils.jwt_wrapper import JWTHandler

logger = structlog.get_logger()


def create_app(settings: Settings) -> Flask:
    app = Flask(__name__)
    Compress(app)

    db_engine = db.create_engine(settings.DatabaseUrl)
    db.migrate(db_engine)
    user_repository = db.UserRepository(db_engine, bcrypt_rounds=settings.BcryptRounds)
    course_repository = db.CourseRepository(db_engine)
    user_course_repository = db.UserCourseRepository(db_engine)
    jwt_handler = JWTHandler(
        encrypt_key=settings.JwtEncryptKey,
        decrypt_key=settings.JwtDecryptKey,
        algorithm=settings.JwtAlgorithm,
        ttl=settings.JwtTTL,
    )

    register_middlewares(app=app, jwt_handler=jwt_handler)
    register_routes(
        app=app,
        user_repository=user_repository,
        course_repository=course_repository,
        user_course_repository=user_course_repository,
        jwt_handler=jwt_handler,
    )

    return app


def create_and_run_app() -> None:

    app = create_app(settings)

    logger.info(
        "Starting UniPick backend server",
        host=settings.WebserverHost,
        port=settings.WebserverPort,
        wsgi_server=settings.WSGIServer,
    )
    match settings.WSGIServer:
        case "flask":
            app.run(
                host=settings.WebserverHost,
                port=settings.WebserverPort,
                debug=True,
            )
        case "waitress":

            from waitress import serve

            serve(
                app,
                host=settings.WebserverHost,
                port=settings.WebserverPort,
                threads=settings.WebserverThreads,
                connection_limit=settings.WebserverConnectionLimit,
            )
        case _:
            raise ValueError(f"Invalid WSGI server: {settings.WSGIServer}")
