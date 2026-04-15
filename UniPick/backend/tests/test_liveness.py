"""
just a simple test to check there is no syntax error or such
"""

from flask.testing import FlaskClient


def test_liveness(client: FlaskClient) -> None:
    response = client.get(
        "/liveness",
    )

    assert response.status_code == 200
