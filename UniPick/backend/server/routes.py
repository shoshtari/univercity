import flask

import api


def register_routes(app: flask.Flask) -> None:
    app.add_url_rule("/liveness", view_func=api.liveness, methods=["GET"])
    app.add_url_rule("/auth/signup", view_func=api.signup, methods=["POST"])
    app.add_url_rule("/auth/login", view_func=api.login, methods=["POST"])
    app.add_url_rule("/auth/getme", view_func=api.getme, methods=["GET"])
