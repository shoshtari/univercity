import flask
import structlog
from flask.views import MethodView

from api.course_schema import GetCoursesOut, ToggleCourseIn, UserCourseOut
from common.errors import CourseNotFoundError
from db import CourseRepository, UserCourseRepository

logger = structlog.getLogger()


class GetCoursesView(MethodView):

    def __init__(self, course_repository: CourseRepository):
        self.course_repository = course_repository

    def get(self) -> flask.Response:
        courses = self.course_repository.get_visible_courses()
        response = GetCoursesOut(courses=courses)

        return flask.Response(
            response=response.model_dump_json(), content_type="application/json"
        )


class ToggleCourseView(MethodView):
    def __init__(self, user_course_repository: UserCourseRepository):
        self.user_course_repository = user_course_repository

    def post(self, course_id_str: str) -> flask.Response:
        req_data = flask.request.get_json()
        req_data["id"] = course_id_str
        payload: ToggleCourseIn = ToggleCourseIn.model_validate(req_data)
        logger_api = logger.new(api="toggle_course", payload=payload)

        user_id = flask.g.get("user_id")
        if not isinstance(user_id, int):
            ans = flask.jsonify(
                {"error": "internal_error"}
            )  # since token must be parsed in middleware, it is server error not user error
            ans.status_code = 500
            return ans

        course_id = payload.id
        change = payload.change

        try:
            match change:
                case "add":
                    nrows = self.user_course_repository.insert(
                        user_id=user_id, course_id=course_id
                    )
                case "remove":
                    nrows = self.user_course_repository.remove(
                        user_id=user_id, course_id=course_id
                    )
                    logger_api.info(
                        "remove_toggle", nrows=nrows, uid=user_id, cid=course_id
                    )
                case _:
                    logger_api.error(
                        "unexpected_payload",
                        field="change",
                    )
                    ans = flask.jsonify(
                        {"error": "internal_error"}
                    )  # since pydantic should caught this, if we reach here, it is server error
                    ans.status_code = 500
                    return ans
        except CourseNotFoundError:
            logger_api.warning("course_not_found")
            ans = flask.jsonify({"error": "course_not_found"})
            ans.status = 404
            return ans

        status_code = 200 if nrows else 204
        response = flask.Response(status=status_code)
        return response


class GetUserCoursesView(MethodView):
    def __init__(self, user_course_repository: UserCourseRepository):
        self.user_course_repository = user_course_repository

    def get(self) -> flask.Response:
        user_id = flask.g.get("user_id")
        if not isinstance(user_id, int):
            ans = flask.jsonify(
                {"error": "internal_error"}
            )  # since token must be parsed in middleware, it is server error not user error
            ans.status_code = 500
            return ans
        course_ids = self.user_course_repository.get_by_user_id(user_id)
        response = UserCourseOut(course_ids=course_ids)
        return flask.Response(
            response=response.model_dump_json(), content_type="application/json"
        )
