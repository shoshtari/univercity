import datetime

import structlog
from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    Table,
    delete,
    insert,
    select,
)
from sqlalchemy.exc import IntegrityError

from common.errors import CourseNotFoundError
from db.engine import METADATA, get_engine

logger = structlog.getLogger()


user_course = Table(
    "user_course",
    METADATA,
    Column("user_id", Integer, ForeignKey("user.id"), primary_key=True),
    Column("course_id", Integer, ForeignKey("course.id"), primary_key=True),
    Column(
        "created_at",
        DateTime,
        default=lambda: datetime.datetime.now(datetime.timezone.utc),
    ),
    Column(
        "deleted_at",
        DateTime,
        nullable=True,
    ),
)


class UserCourseRepository:

    @staticmethod
    def insert(user_id: int, course_id: int) -> int:
        """
        insert the row with specified values and return affected rows
        """
        stmt = insert(user_course).values(user_id=user_id, course_id=course_id)

        try:
            with get_engine().begin() as conn:
                ans = conn.execute(stmt).rowcount
        except IntegrityError as e:
            unique_failed_error = (
                "UNIQUE constraint failed: user_course.user_id, user_course.course_id"
            )
            foreignkey_failed_error = "FOREIGN KEY constraint failed"
            if str(e.orig) == unique_failed_error:
                return 0
            if str(e.orig) == foreignkey_failed_error:
                raise CourseNotFoundError

            raise

        return ans

    @staticmethod
    def get_by_user_id(user_id: int) -> list[int]:

        stmt = select(user_course.c.course_id).where(
            user_course.c.user_id == user_id, user_course.c.deleted_at == None
        )

        with get_engine().connect() as conn:
            result = conn.execute(stmt).fetchall()
        ans = [i.course_id for i in result]

        return ans

    @staticmethod
    def remove(user_id: int, course_id: int) -> int:
        stmt = delete(user_course).where(
            user_course.c.user_id == user_id, user_course.c.course_id == course_id
        )

        with get_engine().begin() as conn:
            ans = conn.execute(stmt).rowcount

        return ans
