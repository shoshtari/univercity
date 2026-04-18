import flask

from server.middleware import public_endpoint


@public_endpoint
def liveness() -> flask.Response:
    return flask.jsonify({"status": "alive"})
