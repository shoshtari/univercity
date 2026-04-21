import structlog

from common.configs import load_settings
from db import CourseRepository, create_engine

logger = structlog.getLogger()


def flush() -> None:
    settings = load_settings()
    engine = create_engine(settings.DATABASE_URL)

    course_repo = CourseRepository(engine=engine)
    course_repo.flush()
    logger.info("course repository flushed")
