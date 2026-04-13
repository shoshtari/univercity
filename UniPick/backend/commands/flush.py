import structlog

from db import CourseRepository

logger = structlog.getLogger()


def flush() -> None:
    course_repo = CourseRepository()
    course_repo.flush()
    logger.info("course repository flushed")
