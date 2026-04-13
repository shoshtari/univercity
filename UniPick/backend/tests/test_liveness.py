from flask.testing import FlaskClient


def test_liveness(client: FlaskClient) -> None:
    response = client.get(
        "/liveness",
    )

    assert response.status_code == 200
