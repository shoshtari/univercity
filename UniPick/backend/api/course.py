import flask
import structlog

from api.course_schema import GetCoursesOut
from db import CourseRepository

logger = structlog.getLogger()


def get_courses() -> flask.Response | tuple[flask.Response, int]:
    courses = CourseRepository.get_visible_courses()
    response = GetCoursesOut(courses=courses)

    return flask.Response(
        response=response.model_dump_json(), content_type="application/json"
    )
