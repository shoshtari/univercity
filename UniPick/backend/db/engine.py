from sqlalchemy import Engine, MetaData, create_engine, event
from sqlalchemy.engine import Connection
from sqlalchemy.pool.base import _ConnectionRecord

from common.configs import DATABASE_URL

METADATA = MetaData()
ENGINE = create_engine(DATABASE_URL)
if ENGINE.dialect.name == "sqlite":

    @event.listens_for(ENGINE, "connect")
    def my_connection_setup_function(
        dbapi_connection: Connection, _: _ConnectionRecord
    ) -> None:
        cursor = dbapi_connection.cursor()  # type: ignore[attr-defined]
        cursor.execute("PRAGMA foreign_keys = ON;")
        cursor.close()


def get_engine() -> Engine:
    """
    this is here so we can only monkeypatch this not all imports
    """
    return ENGINE


def migrate() -> None:
    METADATA.create_all(get_engine())
