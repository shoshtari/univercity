import time

import pandas as pd
import pytest
import structlog
from flask.testing import FlaskClient

from utils import ScheduleReader

logger = structlog.getLogger()


class TestSchedulePDFParser:
    @pytest.fixture(autouse=True)
    def setup(self, client: FlaskClient) -> None:
        self.schedule_reader = ScheduleReader(client.settings.PDF_ENGINE)

    def _run_parse_pdf(self) -> tuple[pd.DataFrame, float]:
        start_time = time.time()
        df = self.schedule_reader.read_schedule_pdf("./tests/schedule-test.pdf")
        eclapsed_time = time.time() - start_time
        return df, eclapsed_time

    def test_parse_schedule(self, monkeypatch: pytest.MonkeyPatch) -> None:
        row_count = 14
        columns = {
            "name",
            "code",
            "group",
            "units",
            "instructor",
            "classroom",
            "major",
            "exam_date",
            "prerequisite_corequisite",
            "course_times",
            "semester",
            "univercity_update_date",
        }

        self.schedule_reader.pdf_engine = "camelot"
        df, eclapsed = self._run_parse_pdf()
        assert len(df) == row_count
        assert set(df.columns) == columns
        logger.info("parsed pdf", engine="camelot", eclapsed_time=eclapsed)

        self.schedule_reader.pdf_engine = "pdfplumber"
        df, eclapsed = self._run_parse_pdf()
        assert len(df) == row_count
        assert set(df.columns) == columns
        logger.info("parsed pdf", engine="pdfplumber", eclapsed_time=eclapsed)
