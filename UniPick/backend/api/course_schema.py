"""
API schemas for auth apis
"""

from pydantic import BaseModel

from db.course_dto import Course

# class CourseTime(BaseModel):
#     weekday: str
#     start: datetime.time
#     end: datetime.time

# class Course(BaseModel):
#     id: int
#     name: str
#     code: str
#     group: str
#     units: int
#     instructor: str
#     course_times: list[CourseTime]
#     exam_date: str


class GetCoursesOut(BaseModel):
    courses: list[Course]
