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
    MetaData,
    String,
    Table,
    text,
)

from db.engine import ENGINE

logger = structlog.getLogger()


metadata = MetaData()
course = Table(
    "course",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("semester", String(255), nullable=False),
    Column("univercity_update_date", String(255), nullable=False),
    Column("name", String(255), nullable=False),
    Column("code", String(255), nullable=False),
    Column("group", String(255), nullable=False),
    Column("instructor", String(255), nullable=False),
    Column("class", String(255), nullable=False),
    Column("major", String(255), nullable=False),
    Column("exam_date", String(255), nullable=True),
    Column("course_times", JSON, nullable=False),
    Column("units", Integer, nullable=False),
    Column("prerequisite/corequisite", String(255), nullable=False),
    Column("visible", Boolean, default=True),
    Column("created_at", DateTime, default=datetime.datetime.now),
    Column(
        "updated_at",
        DateTime,
        default=datetime.datetime.now,
        onupdate=datetime.datetime.now,
    ),
)


class CourseRepository:
    @staticmethod
    def migrate() -> None:
        course.create(ENGINE, checkfirst=True)
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
        df.to_sql("course", ENGINE, if_exists="append", index=False)

    @staticmethod
    def flush() -> None:
        with ENGINE.begin() as conn:
            result = conn.execute(text("DELETE FROM course"))
        logger.warning("table flushed", rows=result.rowcount)
