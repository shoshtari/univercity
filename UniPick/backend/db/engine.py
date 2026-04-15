from sqlalchemy import Engine, MetaData, create_engine

from common.configs import DATABASE_URL

METADATA = MetaData()
ENGINE = create_engine(DATABASE_URL)


def get_engine() -> Engine:
    """
    this is here so we can only monkeypatch this not all imports
    """
    return ENGINE
