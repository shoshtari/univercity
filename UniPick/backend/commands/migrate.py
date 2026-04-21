import structlog

from common.configs import load_settings
from db import create_engine
from db import migrate as db_migrate

logger = structlog.getLogger()


def migrate() -> None:
    settings = load_settings()
    engine = create_engine(settings.DATABASE_URL)
    db_migrate(engine=engine)
    logger.info("migrate done successfully")
