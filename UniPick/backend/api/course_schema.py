"""
API schemas for auth apis
"""

from pydantic import BaseModel

from db.course_dto import Course


class GetCoursesOut(BaseModel):
    courses: list[Course]
