import pytest
from sqlalchemy import Engine, create_engine
from sqlalchemy.pool import StaticPool

from commands.migrate import migrate
from server.app import create_app


@pytest.fixture
def test_engine() -> Engine:
    return create_engine(
        "sqlite://",
        future=True,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )


@pytest.fixture(autouse=True)
def override_engine(monkeypatch: pytest.MonkeyPatch, test_engine: Engine) -> None:
    monkeypatch.setattr("db.engine.ENGINE", test_engine)
    monkeypatch.setattr("common.configs.JWT_ENCRYPT_KEY", "a" * 32)
    monkeypatch.setattr("common.configs.BCRYPT_ROUNDS", 4)
    migrate()


from flask.testing import FlaskClient


@pytest.fixture
def client() -> FlaskClient:
    app = create_app()
    app.config["TESTING"] = True
    return app.test_client()
