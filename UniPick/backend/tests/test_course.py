import pytest
from flask.testing import FlaskClient
from werkzeug.test import (
    TestResponse,  # can import from flask but mypy complain. this is what flask's test client uses
)

import commands
from utils.jwt_wrapper import create_token


class TestAuth:
    @pytest.fixture(autouse=True)
    def setup(self, client: FlaskClient) -> None:
        self.client = client
        self.token = create_token(user_id=1)

    def test_get_visible_courses(self) -> None:
        commands.add_pdf("./tests/schedule-test.pdf")
        result: TestResponse = self.client.get(
            "/courses",
            headers={
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "Application/Json",
            },
        )
        assert result.status_code == 200
        courses = result.json["courses"]
        assert isinstance(courses, list)
        assert len(courses) == 14
        assert courses[0] == {
            "id": 1,
            "name": "سيستمهاي الكترومغناطيسي حركت خطي",
            "code": "8101508",
            "instructor": "دكتر واعظ زاده",
            "group": "01",
            "course_times": [
                {"weekday": "Sunday", "start": "13:30:00", "end": "15:00:00"},
                {"weekday": "Tuesday", "start": "13:30:00", "end": "15:00:00"},
            ],
            "units": 3,
            "exam_date": "1405-04-14",
        }
