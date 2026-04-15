import pytest
from flask.testing import FlaskClient
from werkzeug.test import (
    TestResponse,  # can import from flask but mypy complain. this is what flask's test client uses
)

from utils.jwt_wrapper import create_token


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

    def test_duplicate_username(self) -> None:
        username = "ali"
        password = "12345678"

        result = self._sign_up(username=username, password=password)
        assert result.status_code == 201, result.json
        assert result.json is not None
        user_id = result.json.get("id")
        assert isinstance(user_id, int), user_id

        result = self._sign_up(username=username, password=password)
        assert result.status_code == 409, result.json
        assert result.json is not None
        error_text = result.json.get("error")
        assert error_text == "username_already_exists", error_text

    def test_weak_password(self) -> None:
        username = "ali"
        password = "123"

        result = self._sign_up(username=username, password=password)
        assert result.status_code == 400, result.json
        assert result.json is not None
        error_text = result.json.get("error")
        assert error_text == "validation_error", error_text
        error_details = result.json.get("details")
        assert error_details is not None, "details should be present in the response"
        assert isinstance(error_details, list), "details should be a list"
        assert len(error_details) == 1, "there should be exactly one validation error"
        loc = error_details[0].get("loc")
        assert loc == ["password"]

    def test_invalid_login(self) -> None:
        username = "ali"
        password = "12345678"

        result = self._sign_up(username=username, password=password)
        assert result.status_code == 201, result.json
        assert result.json is not None
        user_id = result.json.get("id")
        assert isinstance(user_id, int), user_id

        result = self._login(username=username, password=password + "foo")
        assert result.status_code == 401, result.json
        assert result.json is not None
        error = result.json.get("error")
        assert error == "invalid_username_or_password", error

    def test_malformed_token(self) -> None:
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

        result = self._getme(access_token=access_token + "a")
        assert result.status_code == 401, result.text
        assert result.json is not None
        assert result.json.get("error") == "invalid_token", result.json

    def test_token_wrong_signature(self, monkeypatch: pytest.MonkeyPatch) -> None:
        username = "ali"
        password = "12345678"

        result = self._sign_up(username=username, password=password)
        assert result.status_code == 201, result.json
        assert result.json is not None
        user_id = result.json.get("id")
        assert isinstance(user_id, int), user_id

        monkeypatch.setattr("common.configs.JWT_ENCRYPT_KEY", "b" * 32)
        access_token = create_token(user_id=user_id)
        result = self._getme(access_token=access_token)
        assert result.status_code == 401, result.text
        assert result.json is not None
        assert result.json.get("error") == "invalid_token", result.json

    def test_token_expired(self, monkeypatch: pytest.MonkeyPatch) -> None:
        username = "ali"
        password = "12345678"

        result = self._sign_up(username=username, password=password)
        assert result.status_code == 201, result.json
        assert result.json is not None
        user_id = result.json.get("id")
        assert isinstance(user_id, int), user_id

        monkeypatch.setattr("common.configs.JWT_TTL", -100)
        access_token = create_token(user_id=user_id)
        result = self._getme(access_token=access_token)
        assert result.status_code == 401, result.text
        assert result.json is not None
        assert result.json.get("error") == "token_expired", result.json

    def test_getme_user_not_exist(self, monkeypatch: pytest.MonkeyPatch) -> None:
        access_token = create_token(user_id=1)
        result = self._getme(access_token=access_token)
        assert result.status_code == 404, result.text
        assert result.json is not None
        assert result.json.get("error") == "user_not_found", result.json

    def test_login_no_password(self):
        username = "ali"
        password = "12345678"

        result = self._sign_up(username=username, password=password)
        assert result.status_code == 201, result.json
        assert result.json is not None
        user_id = result.json.get("id")
        assert isinstance(user_id, int), user_id

        result = self._login(username=username, password="")
        assert result.status_code == 400, result.json
        assert result.json is not None
        assert result.json.get("error") == "validation_error", result.json
        error_details = result.json.get("details")
        assert isinstance(error_details, list), "details should be a list"
        assert len(error_details) == 1, "there should be exactly one validation error"
        loc = error_details[0].get("loc")
        assert loc == [
            "password"
        ], f"validation error should be about password, but got {loc}"
