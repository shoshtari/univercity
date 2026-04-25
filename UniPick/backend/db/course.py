import datetime
import json

import structlog
from cachetools import TTLCache, cached
from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    Engine,
    Integer,
    String,
    Table,
    select,
    text,
)

import db.course_dto as dto
from db.engine import METADATA

logger = structlog.getLogger()


course = Table(
    "course",
    METADATA,
    Column("id", Integer, primary_key=True),
    Column("semester", String(255), nullable=False),
    Column("univercity_update_date", String(255), nullable=False),
    Column("name", String(255), nullable=False),
    Column("code", String(255), nullable=False),
    Column("group", String(255), nullable=False),
    Column("instructor", String(255), nullable=True),
    Column("classroom", String(255), nullable=True),
    Column("major", String(255), nullable=True),
    Column("exam_date", String(255), nullable=True),
    Column("course_times", JSON, nullable=False),
    Column("units", Integer, nullable=False),
    Column("prerequisite_corequisite", String(255), nullable=True),
    Column("visible", Boolean, default=True),
    Column(
        "created_at",
        DateTime,
        default=lambda: datetime.datetime.now(datetime.timezone.utc),
    ),
    Column(
        "updated_at",
        DateTime,
        default=lambda: datetime.datetime.now(datetime.timezone.utc),
        onupdate=lambda: datetime.datetime.now(datetime.timezone.utc),
    ),
)


class CourseRepository:
    def __init__(self, engine: Engine):
        self.engine = engine

    def insert_from_dataframe(self, data: list[dto.Course]) -> None:
        rows = [
            {
                "semester": row.semester,
                "univercity_update_date": row.update_date,
                "name": row.name,
                "code": row.code,
                "group": row.group,
                "instructor": row.instructor,
                "classroom": row.classroom,
                "major": row.major,
                "exam_date": row.exam_date,
                "course_times": json.dumps(
                    row.courseTimes, default=lambda o: (o.__dict__)
                ),
                "units": row.units,
                "prerequisite_corequisite": row.prerequisite_corequisite,
            }
            for row in data
        ]
        stmt = course.insert()
        with self.engine.begin() as conn:
            conn.execute(stmt, rows)

        logger.info("dataframe inserted into course table", rows=len(data))

    def flush(self) -> None:
        with self.engine.begin() as conn:
            result = conn.execute(text("DELETE FROM course"))
        logger.warning("table flushed", rows=result.rowcount)

    @cached(
        TTLCache(maxsize=1, ttl=1)
    )  # since we want to make sure that the cache is synced with the database, we set the ttl to 1 second. its main goal is to avoid high spike.
    def get_visible_courses(self) -> list[dto.Course]:
        stmt = select(
            course.c.id,
            course.c.name,
            course.c.code,
            course.c.course_times,
            course.c.group,
            course.c.instructor,
            course.c.units,
            course.c.exam_date,
            course.c.major,
            course.c.classroom,
            course.c.prerequisite_corequisite,
            course.c.semester,
            course.c.univercity_update_date,
        ).where(course.c.visible == True)

        with self.engine.connect() as conn:
            query_result = conn.execute(stmt).all()
            output = [
                dto.Course(
                    id=row[0],
                    name=row[1],
                    code=row[2],
                    courseTimes=dto.CourseTime.parse_json(row[3]),
                    group=row[4],
                    instructor=row[5],
                    units=row[6],
                    exam_date=row[7],
                    major=row[8],
                    classroom=row[9],
                    prerequisite_corequisite=row[10],
                    semester=row[11],
                    update_date=row[12],
                )
                for row in query_result
            ]
        return output
