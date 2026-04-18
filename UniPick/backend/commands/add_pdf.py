import structlog

from db import CourseRepository
from utils import schedule_reader

logger = structlog.getLogger()


def add_pdf(pdf_path: str) -> None:
    """Add courses from PDF file to database"""
    course_repo = CourseRepository()
    df = schedule_reader.read_schedule_pdf(pdf_path)
    logger.info("parsed pdf and got df", df_length=len(df))
    course_repo.insert_from_dataframe(df=df)
    logger.info("inserted df to db")
