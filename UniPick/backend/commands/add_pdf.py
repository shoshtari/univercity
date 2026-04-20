import structlog

from common.configs import settings
from db import CourseRepository, create_engine
from utils import ScheduleReader

logger = structlog.getLogger()


def add_pdf(pdf_path: str) -> None:
    """Add courses from PDF file to database"""
    engine = create_engine(settings.DatabaseUrl)

    course_repo = CourseRepository(engine)
    schedule_reader = ScheduleReader(settings.PDFEngine)

    df = schedule_reader.read_schedule_pdf(pdf_path)
    logger.info("parsed pdf and got df", df_length=len(df))
    course_repo.insert_from_dataframe(df=df)
    logger.info("inserted df to db")
