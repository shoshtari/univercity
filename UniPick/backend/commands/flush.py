import structlog

from common.configs import settings
from db import CourseRepository, create_engine

logger = structlog.getLogger()


def flush() -> None:
    engine = create_engine(settings.DatabaseUrl)

    course_repo = CourseRepository(engine=engine)
    course_repo.flush()
    logger.info("course repository flushed")
