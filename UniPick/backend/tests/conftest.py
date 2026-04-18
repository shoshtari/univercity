import pytest
from flask.testing import FlaskClient
from sqlalchemy import Engine, create_engine, text
from sqlalchemy.pool import StaticPool

from commands.migrate import migrate
from server.app import create_app


@pytest.fixture
def test_engine() -> Engine:
    engine = create_engine(
        "sqlite://",
        future=True,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    with engine.connect() as conn:
        conn.execute(text("PRAGMA foreign_keys=ON"))
    return engine


@pytest.fixture(autouse=True)
def override_engine(monkeypatch: pytest.MonkeyPatch, test_engine: Engine) -> None:
    monkeypatch.setattr("db.engine.ENGINE", test_engine)
    monkeypatch.setattr("common.configs.JWT_ENCRYPT_KEY", "a" * 32)
    monkeypatch.setattr("common.configs.BCRYPT_ROUNDS", 4)
    migrate()


@pytest.fixture(scope="session")
def client() -> FlaskClient:
    app = create_app()
    app.config["TESTING"] = True
    app.config["SERVER_NAME"] = "localhost:8080"
    with app.test_client() as client:
        with app.app_context():
            yield client
