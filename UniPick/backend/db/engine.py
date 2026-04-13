from sqlalchemy import create_engine

from common.configs import DATABASE_URL

ENGINE = create_engine(DATABASE_URL)
