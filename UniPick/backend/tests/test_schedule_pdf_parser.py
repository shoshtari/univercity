import time

import pytest
import structlog
from flask.testing import FlaskClient

from utils import ScheduleReader
from db.course_dto import Course

logger = structlog.getLogger()


class TestSchedulePDFParser:
    @pytest.fixture(autouse=True)
    def setup(self, client: FlaskClient) -> None:
        self.schedule_reader = ScheduleReader()

    def _run_parse_pdf(self) -> tuple[list[Course], float]:
        start_time = time.time()
        courses = self.schedule_reader.read_schedule_pdf("./tests/schedule-test.pdf")
        eclapsed_time = time.time() - start_time
        return courses, eclapsed_time

    def test_parse_schedule(self, monkeypatch: pytest.MonkeyPatch) -> None:
        row_count = 14

        self.schedule_reader.pdf_engine = "pdfplumber"
        courses, eclapsed = self._run_parse_pdf()
        assert len(courses) == row_count
        logger.info("parsed pdf", engine="pdfplumber", eclapsed_time=eclapsed)
