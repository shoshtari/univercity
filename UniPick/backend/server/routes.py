from typing import Any

import flask

import api
import db
from utils.jwt_wrapper import JWTHandler


def register_routes(
    *_: Any,
    app: flask.Flask,
    user_repository: db.UserRepository,
    course_repository: db.CourseRepository,
    user_course_repository: db.UserCourseRepository,
    jwt_handler: JWTHandler
) -> None:
    """
    since repositories can get mixed, disabled positional arguments
    """
    app.add_url_rule(
        "/liveness", view_func=api.liveness, methods=["GET"], endpoint="liveness"
    )

    app.add_url_rule(
        "/auth/signup",
        view_func=api.SignupView.as_view("signup", user_repository=user_repository),
        methods=["POST"],
        endpoint="signup",
    )
    app.add_url_rule(
        "/auth/login",
        view_func=api.LoginView.as_view(
            "login", user_repository=user_repository, jwt_handler=jwt_handler
        ),
        methods=["POST"],
        endpoint="login",
    )
    app.add_url_rule(
        "/auth/getme",
        view_func=api.GetmeView.as_view("getme", user_repository=user_repository),
        methods=["GET"],
        endpoint="getme",
    )

    app.add_url_rule(
        "/courses/all",
        view_func=api.GetCoursesView.as_view(
            "get-all-courses", course_repository=course_repository
        ),
        methods=["GET"],
        endpoint="get-all-courses",
    )
    app.add_url_rule(
        "/courses/my",
        view_func=api.GetUserCoursesView.as_view(
            "get-user-courses", user_course_repository=user_course_repository
        ),
        methods=["GET"],
        endpoint="get-user-courses",
    )
    app.add_url_rule(
        "/courses/<course_id_str>",
        view_func=api.ToggleCourseView.as_view(
            "toggle-course", user_course_repository=user_course_repository
        ),
        methods=["POST"],
        endpoint="toggle-course",
    )
