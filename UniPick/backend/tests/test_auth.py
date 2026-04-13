import pytest
from flask.testing import FlaskClient


class TestAuth:
    @pytest.fixture(autouse=True)
    def setup(self, client: FlaskClient) -> None:
        self.client = client

    def create_user(self, username: str, password: str) -> int:

        result = self.client.post(
            "/auth/signup",
            json={
                "username": username,
                "password": password,
            },
        )
        assert result.status_code == 201, result.json
        assert result.json is not None
        user_id = result.json.get("id")
        assert user_id is not None, result.json
        assert isinstance(user_id, int), user_id
        return user_id

    def login(self, username: str, password: str) -> str:

        result = self.client.post(
            "/auth/login",
            json={
                "username": username,
                "password": password,
            },
        )
        assert result.status_code == 200, result.json
        assert result.json is not None
        access_token = result.json.get("access_token")
        assert access_token is not None, result.json
        assert isinstance(access_token, str), access_token
        return access_token

    def test_login_success(self) -> None:
        username = "ali"
        password = "12345678"
        user_id = self.create_user(username=username, password=password)
        access_token = self.login(username=username, password=password)
        print(user_id, access_token)
