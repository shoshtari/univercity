from sqlalchemy import Engine, MetaData, event
from sqlalchemy import create_engine as sqlalchemy_create_engine
from sqlalchemy.engine import Connection
from sqlalchemy.pool.base import _ConnectionRecord

METADATA = MetaData()


def create_engine(connstring: str) -> Engine:
    engine = sqlalchemy_create_engine(connstring)

    if engine.dialect.name == "sqlite":

        @event.listens_for(engine, "connect")
        def my_connection_setup_function(
            dbapi_connection: Connection, _: _ConnectionRecord
        ) -> None:
            cursor = dbapi_connection.cursor()  # type: ignore[attr-defined]
            cursor.execute("PRAGMA foreign_keys = ON;")
            cursor.close()

    return engine


def migrate(engine: Engine) -> None:
    METADATA.create_all(engine)
