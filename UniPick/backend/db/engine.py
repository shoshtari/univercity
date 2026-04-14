from sqlalchemy import MetaData, create_engine

from common.configs import DATABASE_URL

METADATA = MetaData()
ENGINE = create_engine(DATABASE_URL)
