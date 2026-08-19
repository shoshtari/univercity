import re
import time
from typing import Any, Optional, Sequence, cast

import jdatetime
import pdfplumber
import structlog
from rich.progress import track

from db.course_dto import Course, CourseTime

logger = structlog.getLogger()

WEEKDAYS = (
    "Saturday",
    "Sunday",
    "Monday",
    "Tuesday",
    "Wednesday",
)
START_SUFFIX = " Start"
END_SUFFIX = " End"


def is_ltr(text: str) -> bool:
    if text.isnumeric():
        return True

    if text[0] == "(" and text[-1] == ")":
        text = text[1 : len(text) - 1]

    return all(
        [
            (
                ord("a") <= ord(i) <= ord("z")
                or ord("A") <= ord(i) <= ord("Z")
                or ord("0") <= ord(i) <= ord("9")
                or i in ("!@#$%^&*")
            )
            for i in text
        ]
    )


class ScheduleReader:
    IN_PARANTHESIS_REGEX = re.compile(r"\([^)]*\)")
    TIME_REGEX = re.compile(r"\d+:\d+")

    def _reverse_row(self, line: Optional[str]) -> Optional[str]:
        """
        since we read pdf from left to right but its text is rtl, we need to reverse it except numbers and special symbols
        """
        if not line or not isinstance(line, str) or self.TIME_REGEX.match(line):

            return line

        # handle empty () in some lines (add paranthesis to line before)
        line_parts = line.split("\n")
        if "( )" in line_parts and line_parts.index("( )") > 0:
            ind = line_parts.index("( )") - 1
            line_parts[ind] = f"({line_parts[ind]})"
            line_parts.pop(ind + 1)
            line = "\n".join(line_parts)

        # handle mixed parts (ltr follow rtl without space
        tmp = ""
        for i in range(len(line) - 1):
            tmp += line[i]
            if not line[i].strip() or not line[i + 1].strip():
                continue
            is_ltr1 = is_ltr(line[i].strip())
            is_ltr2 = is_ltr(line[i + 1].strip())
            if is_ltr1 != is_ltr2:
                tmp += " "
        tmp += line[-1]
        line = tmp.strip()

        # reverse lines since it has been read reversed (at least by pdfplumber)
        line = " ".join(line.split("\n")[::-1])

        parts = line.split()
        parts_out = []
        for part in reversed(parts):
            if not (is_ltr(part) or self.TIME_REGEX.match(part)):
                part = part[::-1]
                part = part.translate(str.maketrans("(){}", ")(}{"))
            parts_out.append(part)
        return " ".join(parts_out)

    @staticmethod
    def _parse_exam_date(date_str: str) -> Optional[str]:
        if (
            not date_str
            or date_str == "امتحان کتبی ندارد"
            or date_str == "امتحان کتبی پایان ترم ندارد"
            or not isinstance(date_str, str)
        ):
            return None

        parsed_date = date_str.replace("ﺻﺒﺢ", "")
        parsed_date = parsed_date.replace("ﺻبﺢ", "")
        parsed_date = parsed_date.replace("ﻋﺼر", "")
        parsed_date = parsed_date.replace("عصر", "")
        parsed_date = parsed_date.replace("ﻋصر", "")
        parsed_date = parsed_date.strip()

        # Try new format: DD / MM / YY or DD / MM / YYYY (e.g., "26 / 10 / 05" or "26 / 10 / 1405")
        if re.match(r"^\d{1,2}\s*/\s*\d{1,2}\s*/\s*\d{2,4}$", parsed_date):
            parts = [p.strip() for p in parsed_date.split("/")]
            if len(parts) == 3:
                day, month, year = parts
                if len(year) == 2:
                    year = "14" + year  # Assume 14xx for Persian calendar
                try:
                    parsed_date = jdatetime.datetime(int(year), int(month), int(day)).date()
                    return cast(str, parsed_date.isoformat())
                except ValueError:
                    pass

        # Try old format with Persian month names
        month_map = {
            "فروردين": "01",
            "ارديبهشت": "02",
            "خرداد": "03",
            "تیر": "04",
            "مرداد": "05",
            "شهريور": "06",
            "مهر": "07",
            "آبان": "08",
            "آذر": "09",
            "دي": "10",
            "بهمن": "11",
            "اسفند": "12",
        }
        for month_name, month_num in month_map.items():
            if month_name in parsed_date:
                parsed_date = parsed_date.replace(month_name, month_num)
                break

        try:
            parsed_date = jdatetime.datetime.strptime(parsed_date, "%d %m %Y").date()
            return cast(str, parsed_date.isoformat())
        except ValueError:
            logger.critical(
                "Failed to parse exam date",
                date_str=date_str,
                parsed_date=parsed_date,
            )
            raise

    def _read_metadata(self, pdf_path: str) -> tuple[str, str]:
        """
        return semester and update_date
        """
        with pdfplumber.open(pdf_path) as pdf:
            page = pdf.pages[0]

            title = page.extract_text().split("\n")[0].strip()
            title_rev = self._reverse_row(title)
            if title_rev is None:
                logger.critical("title became none", title=title)
                raise ValueError("title is none")
            title = title_rev
            title = title.replace("ي", "ی")

            results = self.IN_PARANTHESIS_REGEX.findall(title)
            results = [i.replace("(", "").replace(")", "") for i in results]
            if len(results) != 2:
                logger.critical(
                    "expected title to have semester and update date in parantheses",
                    title=title,
                    results_length=len(results),
                )
                raise ValueError("missing or malformed metadata")
            if "نیمسال" not in results[0]:
                logger.critical(
                    "expected title to have semester and update date in parantheses",
                    title=title,
                    results_length=len(results),
                )
                raise ValueError("missing semester metadata")
            if "به روز رسانی درتاریخ: " not in results[1]:
                logger.critical(
                    "expected title to have semester and update date in parantheses",
                    title=title,
                    results_length=len(results),
                )
                raise ValueError("missing update_date metadata")

            semester = results[0].replace("نیمسال", "").strip()
            update_date = results[1].replace("به روز رسانی درتاریخ: ", "").strip()
            return semester, update_date

    def _read_tables_from_page_pdfplumber(
        self, page: pdfplumber.page.Page, logger: structlog.BoundLogger
    ) -> tuple[list[list[Any]], list[str | None]]:
        """
        return table read rows and headers which could be None
        """
        table_settings = {
            "vertical_strategy": "lines",
            "horizontal_strategy": "lines",
            "intersection_tolerance": 3,
        }
        tables = page.extract_tables(table_settings=table_settings)
        if not tables:
            logger.warning("no tables found")
            return [], []

        data = []
        header: list[str | None] = []
        header_row_offset = 3  # default: title, header, start-end row

        for table_num, table in enumerate(tables):
            if not table:
                continue

            logger.debug("found table", table_num=table_num, table_length=len(table))
            if len(table) <= 2:
                logger.critical("table counts are too low", table_count=len(table))
                raise ValueError("table counts are too low")

            if table_num == 0:
                title = table[0]
                header = table[1]

                # Check if this is new format with sub-header row (contains "ناياپ عورش")
                if len(table) > 2 and any(
                    cell and "ناياپ عورش" in str(cell) for cell in table[2]
                ):
                    logger.debug("detected new PDF format with sub-header row")
                    # Combine header row 1 and sub-header row 2
                    sub_header = table[2]
                    combined_header: list[str | None] = []
                    for i, (main, sub) in enumerate(zip(header, sub_header)):
                        if main and sub and "ناياپ عورش" in str(sub):
                            combined_header.append(main)
                        elif main:
                            combined_header.append(main)
                        elif sub:
                            combined_header.append(sub)
                        else:
                            combined_header.append(None)
                    header = combined_header
                    header_row_offset = 4  # title, header, sub-header, start-end row

            if title != table[0]:
                logger.critical("title mismatch", table_num=table_num)
                raise ValueError("title mismatch")

            if header != table[1]:
                logger.critical("header mismatch", table_num=table_num)
                raise ValueError("header mismatch")

            table = table[header_row_offset:]
            for row in table:
                if len(row) != len(header):
                    logger.critical("Row length mismatch on page", table_num=table_num)
                    raise ValueError("row length mismatch")
            data.extend(table)
        if not header:
            logger.critical("cant fill header", data_length=len(data))
            raise ValueError("cant find header in tables")
        return data, header

    def _read_data_with_pdfplumber(
        self, pdf_path: str
    ) -> tuple[list[list[Any]], list[Optional[str]]]:

        all_data = []
        header: list[str | None] = []
        with pdfplumber.open(
            pdf_path
        ) as pdf:  # we are less optimized for openning pdf twice by pdfplumber but this is cleaner
            for page_num, page in track(
                enumerate(pdf.pages, 1),
                total=len(pdf.pages),
                description="Processing PDF pages...",
                transient=True,
            ):
                logger.debug(f"Processing page {page_num}...")
                page_data, header = self._read_tables_from_page_pdfplumber(
                    page, logger.new(page_num=page_num)
                )
                all_data.extend(page_data)
        return all_data, header

    @staticmethod
    def _normalize_occurance_times(
        row: list[Any], headers: list[str]
    ) -> list[CourseTime]:
        """
        the occurance times in pdf are formatted into 10 columns (weekdays * 2) which determine start and end
        the code logic expect a list of objects with three fields 'weekday', 'start' and end
        this code converts it
        """

        def is_valid_time(time_str: str) -> bool:
            """Validate time format HH:MM"""
            if not isinstance(time_str, str):
                return False
            time_str = time_str.strip()
            if not time_str:
                return False
            # Must match HH:MM format
            if not re.match(r"^\d{1,2}:\d{2}$", time_str):
                return False
            try:
                hour, minute = map(int, time_str.split(":"))
                return 0 <= hour <= 23 and 0 <= minute <= 59
            except ValueError:
                return False

        class_times = []
        for weekday in WEEKDAYS:
            start_index = headers.index(weekday + START_SUFFIX)
            end_index = headers.index(weekday + END_SUFFIX)
            start_time = row[start_index]
            end_time = row[end_index]

            if (not start_time or not isinstance(start_time, str)) and (
                not end_time or not isinstance(end_time, str)
            ):
                continue

            # Validate time formats before adding
            if not is_valid_time(start_time) or not is_valid_time(end_time):
                logger.warning(
                    "Skipping invalid time format",
                    weekday=weekday,
                    start_time=start_time,
                    end_time=end_time,
                )
                continue

            class_times.append(
                CourseTime(weekday=weekday, start=start_time, end=end_time)
            )
        return class_times

    @staticmethod
    def _normalize_header(header: Sequence[Optional[str]]) -> list[str]:
        header = [
            col.strip() if col else None for col in header
        ]  # no empty or none header

        output: list[str] = []
        for i in range(len(header)):
            val = header[i]
            if isinstance(val, str):
                output.append(val)
            else:
                if i == 0 or not output:
                    logger.critical("got empty header at first col", header=header)
                    raise ValueError("empty header at start")

                before = output[i - 1]
                if before not in [
                    "هﺒنش",
                    "هﺒنشكي",
                    "هﺒنشود",
                    "هﺒنش هس",
                    "هﺒنشراهچ",
                ]:

                    logger.critical(
                        "none header has no previous weekday", header=header
                    )
                    raise ValueError("empty header without weekday before")
                weekday = output[i - 1]
                output.append(f"{weekday} شروع")
                output[i - 1] = f"{weekday} پایان"
        return output

    def _normalize_dataframe(
        self,
        data: list[list[Any]],
        semester: str,
        update_date: str,
        header: list[str],
    ) -> list[Course]:

        column_mapping = {
            "زاينمه*/زاين شيپ": "prerequisite_corequisite",
            "ناحتما خيرات": "exam_date",
            "شيارگ": "major",
            "سﻼك": "classroom",
            "هﺒنشراهچ شروع": "Wednesday Start",
            "هﺒنشراهچ پایان": "Wednesday End",
            "هﺒنش هس شروع": "Tuesday Start",
            "هﺒنش هس پایان": "Tuesday End",
            "هﺒنشود شروع": "Monday Start",
            "هﺒنشود پایان": "Monday End",
            "هﺒنشكي شروع": "Sunday Start",
            "هﺒنشكي پایان": "Sunday End",
            "هﺒنش شروع": "Saturday Start",
            "هﺒنش پایان": "Saturday End",
            "سردم": "instructor",
            "دحاو": "units",
            "هورگ": "group",
            "سرد هرامش": "code",
            "سرد مان": "name",
        }

        try:
            cleansed_header = [column_mapping[i] for i in header]
        except KeyError as e:
            logger.critical("unknown column in header", error=str(e), header=header)
            raise

        exam_date_index = cleansed_header.index("exam_date")
        cleansed_data = []
        for row in data:
            cleansed_row = []
            for i, cell in enumerate(row):
                if cell == "":
                    cell = None
                cell = self._reverse_row(cell)
                if isinstance(cell, str):
                    cell = cell.translate(str.maketrans("يﺒﺼﻋك", "یبصعک"))
                if i == exam_date_index:
                    cell = self._parse_exam_date(cell)

                cleansed_row.append(cell)
            if any([i is not None for i in cleansed_row]):
                if len(header) != len(cleansed_row):
                    logger.error(
                        "header length mismatch",
                        header_length=len(header),
                        row_length=len(cleansed_row),
                    )
                    raise ValueError("got row with different size than header")

                kwargs = dict(zip(cleansed_header, cleansed_row))
                for weekday in WEEKDAYS:
                    del kwargs[weekday + START_SUFFIX]
                    del kwargs[weekday + END_SUFFIX]
                kwargs["courseTimes"] = self._normalize_occurance_times(
                    row=cleansed_row, headers=cleansed_header
                )
                kwargs["id"] = None
                kwargs["semester"] = semester
                kwargs["update_date"] = update_date

                cleansed_data.append(Course(**kwargs))

        return cleansed_data

    def read_schedule_pdf(self, pdf_path: str) -> list[Course]:
        """
        Read a PDF file containing a course schedule table and return a DataFrame.

        Args:
            pdf_path: Path to the PDF file

        Returns:
            list of courses in the PDF file
        """

        semester, update_date = self._read_metadata(pdf_path)

        start = time.time()
        data, header = self._read_data_with_pdfplumber(pdf_path=pdf_path)
        logger.debug("pdf_parsing_time", duration=time.time() - start)
        if not data:
            raise ValueError("No data found in the PDF")

        if header is None:
            raise ValueError("No header found in the PDF")

        normalized_header = self._normalize_header(header)
        ans = self._normalize_dataframe(
            data=data,
            semester=semester,
            update_date=update_date,
            header=normalized_header,
        )
        return ans
