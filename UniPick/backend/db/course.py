import datetime
import json

import pandas as pd
import structlog
from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    Integer,
    String,
    Table,
    select,
    text,
)

import db.course_dto as dto
from db.engine import METADATA, get_engine

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
    Column("instructor", String(255), nullable=False),
    Column("classroom", String(255), nullable=False),
    Column("major", String(255), nullable=False),
    Column("exam_date", String(255), nullable=True),
    Column("course_times", JSON, nullable=False),
    Column("units", Integer, nullable=False),
    Column("prerequisite_corequisite", String(255), nullable=False),
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
    @staticmethod
    def migrate() -> None:
        course.create(get_engine(), checkfirst=True)
        logger.info("course table migration done")

    @classmethod
    def insert_from_dataframe(cls, df: pd.DataFrame) -> None:
        table_columns = set(
            [
                i.name
                for i in course.columns
                if i.name not in ("id", "created_at", "updated_at", "visible")
            ]
        )
        df_columns = set(df.columns)

        if table_columns != df_columns:
            logger.error(
                "dataframe has different columns than table",
                extra_columns=df_columns - table_columns,
                lacking_columns=table_columns - df_columns,
            )
            raise ValueError("dataframe has invalid columns")
        df["course_times"] = df["course_times"].apply(json.dumps)
        # df.to_sql("course", get_engine(), if_exists="append", index=False)
        # since at least for now, the load is not that huge, we can iterate
        with get_engine().begin() as conn:
            for _, row in df.iterrows():
                stmt = course.insert().values(
                    semester=row.semester,
                    univercity_update_date=row.univercity_update_date,
                    name=row[
                        "name"
                    ],  # cant use getattr since it conflicts and return index
                    code=row.code,
                    group=row.group,
                    instructor=row.instructor,
                    classroom=row.classroom,
                    major=row.major,
                    exam_date=row.exam_date,
                    course_times=row.course_times,
                    units=row.units,
                    prerequisite_corequisite=row.prerequisite_corequisite,
                )
                conn.execute(stmt)
        logger.info("dataframe inserted into course table", rows=len(df))

    @staticmethod
    def flush() -> None:
        with get_engine().begin() as conn:
            result = conn.execute(text("DELETE FROM course"))
        logger.warning("table flushed", rows=result.rowcount)

    @staticmethod
    def get_visible_courses() -> list[dto.Course]:
        stmt = select(
            course.c.id,
            course.c.name,
            course.c.code,
            course.c.course_times,
            course.c.group,
            course.c.instructor,
            course.c.units,
            course.c.exam_date,
        ).where(course.c.visible == True)

        with get_engine().connect() as conn:
            query_result = conn.execute(stmt).all()
            output = [
                dto.Course(
                    id=row[0],
                    name=row[1],
                    code=row[2],
                    course_times=dto.CourseTime.parse_json(row[3]),
                    group=row[4],
                    instructor=row[5],
                    units=row[6],
                    exam_date=row[7],
                )
                for row in query_result
            ]
        return output
