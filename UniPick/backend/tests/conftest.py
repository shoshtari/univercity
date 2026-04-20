import pytest
from flask.testing import FlaskClient
from sqlalchemy import Engine, create_engine, text
from sqlalchemy.pool import StaticPool

from common.configs import settings
from server.app import create_app


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


@pytest.fixture()
def client(monkeypatch) -> FlaskClient:
    engine = test_engine()
    monkeypatch.setattr(
        "db.create_engine",
        lambda _: engine,
    )

    app = create_app(settings)
    app.config["TESTING"] = True
    app.config["SERVER_NAME"] = "localhost:8080"
    app.config["FOO"] = "BAR"
    with app.test_client() as client:
        with app.app_context():
            client.settings = settings
            client.db_engine = engine
            yield client
