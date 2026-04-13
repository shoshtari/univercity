import structlog

from db import CourseRepository, UserRepository

logger = structlog.getLogger()


def migrate() -> None:
    CourseRepository().migrate()
    UserRepository().migrate()
