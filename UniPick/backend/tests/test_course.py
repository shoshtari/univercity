from typing import Optional

import pytest
from flask import url_for
from flask.testing import FlaskClient
from werkzeug.test import (
    TestResponse,  # can import from flask but mypy complain. this is what flask's test client uses
)

import commands
from db import UserRepository
from utils.jwt_wrapper import create_token


class TestCourse:
    @pytest.fixture(autouse=True)
    def setup(self, client: FlaskClient) -> None:
        user_id = UserRepository.create(username="a", password="a")
        self.client = client
        self.token = create_token(user_id=user_id)
        commands.add_pdf("./tests/schedule-test.pdf")

    def _get_user_course(self, token: Optional[str] = None) -> TestResponse:
        if token is None:
            token = self.token
        return self.client.get(
            "/courses/my",
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            },
        )

    def _toggle_course(self, course_id: int, change: str) -> TestResponse:
        return self.client.post(
            f"/courses/{course_id}",
            headers={
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json",
            },
            json={"change": change},
        )

    def test_get_visible_courses(self) -> None:
        result: TestResponse = self.client.get(
            url_for("get-all-courses"),
            headers={
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "aaplication/json",
            },
        )
        assert result.status_code == 200
        courses = result.json["courses"]
        assert isinstance(courses, list)
        assert len(courses) == 14
        assert courses[0] == {
            "id": 1,
            "name": "سیستمهای الکترومغناطیسی حرکت خطی",
            "code": "8101508",
            "instructor": "دکتر واعظ زاده",
            "group": "01",
            "courseTimes": [
                {"weekday": "Sunday", "start": "13:30:00", "end": "15:00:00"},
                {"weekday": "Tuesday", "start": "13:30:00", "end": "15:00:00"},
            ],
            "units": 3,
            "exam_date": "1405-04-14",
        }

    def test_toggle_course(self) -> None:
        result = self._toggle_course(1, "add")
        assert result.status_code == 200, result.text

        result = self._get_user_course()
        assert result.status_code == 200, result.text
        assert len(result.json["course_ids"]) == 1, result.json

        result = self._toggle_course(1, "add")
        assert result.status_code == 208, result.text

        result = self._get_user_course()
        assert result.status_code == 200, result.text
        assert len(result.json["course_ids"]) == 1, result.json

        other_token = create_token(user_id=10)
        result = self._get_user_course(token=other_token)
        assert result.status_code == 200, result.text
        assert len(result.json["course_ids"]) == 0, result.json

        result = self._toggle_course(1, "remove")
        assert result.status_code == 200, result.text

        result = self._get_user_course()
        assert result.status_code == 200, result.text
        assert len(result.json["course_ids"]) == 0, result.json

        result = self._toggle_course(1, "remove")
        assert result.status_code == 208, result.text

    def test_invalid_input_toggle_course(self) -> None:
        # non existend course
        result = self._toggle_course(10000, change="add")
        assert result.status_code == 404

        # invalid value for change
        result = self._toggle_course(10000, change="golabi")
        assert result.status_code == 400
        assert result.json["error"] == "validation_error"
        assert result.json["details"][0]["loc"] == ["change"]
