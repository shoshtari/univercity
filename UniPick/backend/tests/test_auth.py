import pytest
from flask.testing import FlaskClient
from werkzeug.test import (
    TestResponse,  # can import from flask but mypy complain. this is what flask's test client uses
)


class TestAuth:
    @pytest.fixture(autouse=True)
    def setup(self, client: FlaskClient) -> None:
        self.client = client

    def _sign_up(self, username: str, password: str) -> TestResponse:

        return self.client.post(
            "/auth/signup",
            json={
                "username": username,
                "password": password,
            },
        )

    def _login(self, username: str, password: str) -> TestResponse:

        return self.client.post(
            "/auth/login",
            json={
                "username": username,
                "password": password,
            },
        )

    def _getme(self, access_token: str) -> TestResponse:
        return self.client.get(
            "/auth/getme",
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "Application/Json",
            },
        )

    def test_login_success(self) -> None:
        username = "ali"
        password = "12345678"

        result = self._sign_up(username=username, password=password)
        assert result.status_code == 201, result.json
        assert result.json is not None
        user_id = result.json.get("id")
        assert isinstance(user_id, int), user_id

        result = self._login(username=username, password=password)
        assert result.status_code == 200, result.json
        assert result.json is not None
        access_token = result.json.get("access_token")
        assert isinstance(access_token, str), access_token

        result = self._getme(access_token=access_token)
        assert result.status_code == 200, result.text
        assert result.json is not None
        user_id2 = result.json.get("id")
        assert user_id2 == user_id, (user_id2, user_id)

        username = result.json.get("username")
        assert username == username, username
