import flask

import api


def register_routes(app: flask.Flask) -> None:
    app.add_url_rule(
        "/liveness", view_func=api.liveness, methods=["GET"], endpoint="liveness"
    )

    app.add_url_rule(
        "/auth/signup", view_func=api.signup, methods=["POST"], endpoint="signup"
    )
    app.add_url_rule(
        "/auth/login", view_func=api.login, methods=["POST"], endpoint="login"
    )
    app.add_url_rule(
        "/auth/getme", view_func=api.getme, methods=["GET"], endpoint="getme"
    )

    app.add_url_rule(
        "/courses/all",
        view_func=api.get_courses,
        methods=["GET"],
        endpoint="get-all-courses",
    )
    app.add_url_rule(
        "/courses/my",
        view_func=api.get_user_courses,
        methods=["GET"],
        endpoint="get-user-courses",
    )
    app.add_url_rule(
        "/courses/<course_id_str>",
        view_func=api.toggle_course,
        methods=["POST"],
        endpoint="toggle-course",
    )
