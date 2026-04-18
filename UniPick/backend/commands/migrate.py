import structlog

from db import migrate as db_migrate

logger = structlog.getLogger()


def migrate() -> None:
    db_migrate()
    logger.info("migrate done successfully")
