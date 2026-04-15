import time

import pandas as pd
import pytest
import structlog

from utils.read_schedule import schedule_reader

logger = structlog.getLogger()


class TestSchedulePDFParser:
    def _run_parse_pdf(self) -> tuple[pd.DataFrame, float]:
        start_time = time.time()
        df = schedule_reader.read_schedule_pdf("./tests/schedule-test.pdf")
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

        monkeypatch.setattr("common.configs.PDF_ENGINE", "camelot")
        df, eclapsed = self._run_parse_pdf()
        assert len(df) == row_count
        assert set(df.columns) == columns
        logger.info("parsed pdf", engine="camelot", eclapsed_time=eclapsed)

        monkeypatch.setattr("common.configs.PDF_ENGINE", "pdfplumber")
        df, eclapsed = self._run_parse_pdf()
        assert len(df) == row_count
        assert set(df.columns) == columns
        logger.info("parsed pdf", engine="pdfplumber", eclapsed_time=eclapsed)
