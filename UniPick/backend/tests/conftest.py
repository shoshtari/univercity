import pytest
from sqlalchemy import Engine, create_engine

import common.configs as configs
from commands.migrate import migrate
from commands.runserver import create_app


@pytest.fixture
def test_engine() -> Engine:
    return create_engine("sqlite:///:memory:", future=True)


@pytest.fixture(autouse=True)
def override_engine(monkeypatch: pytest.MonkeyPatch, test_engine: Engine) -> None:
    monkeypatch.setattr("db.engine.ENGINE", test_engine)
    monkeypatch.setattr("db.course.ENGINE", test_engine)
    monkeypatch.setattr("db.user.ENGINE", test_engine)
    migrate()


from flask.testing import FlaskClient


@pytest.fixture
def client() -> FlaskClient:
    app = create_app()
    app.config["TESTING"] = True
    configs.DATABASE_URL = "sqlite://:memory:"
    return app.test_client()
