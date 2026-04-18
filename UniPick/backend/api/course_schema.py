"""
API schemas for auth apis
"""

from typing import Literal

from pydantic import BaseModel

from db.course_dto import Course


class GetCoursesOut(BaseModel):
    courses: list[Course]


class ToggleCourseIn(BaseModel):
    id: int
    change: Literal["add", "remove"]


class UserCourseOut(BaseModel):
    course_ids: list[int]
