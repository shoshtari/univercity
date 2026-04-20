import structlog

from common.configs import settings
from db import create_engine
from db import migrate as db_migrate

logger = structlog.getLogger()


def migrate() -> None:
    engine = create_engine(settings.DatabaseUrl)
    db_migrate(engine=engine)
    logger.info("migrate done successfully")
