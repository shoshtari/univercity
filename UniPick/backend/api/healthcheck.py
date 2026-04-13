import flask


def liveness() -> flask.Response:
    return flask.jsonify({"status": "alive"})
