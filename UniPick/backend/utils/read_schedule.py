import re
from typing import Optional, Sequence, cast

import jdatetime
import pandas as pd
import pdfplumber
import structlog
from rich.progress import track

logger = structlog.getLogger()


class ScheduleReader:
    @staticmethod
    def _substitute(text: str, pairs: Sequence[tuple[str, str]]) -> str:
        """
        for each pair, it substitue the first element with second in text
        it is used for simultainous multiple substitutions
        """
        substitutes: list[tuple[int, str]] = []
        for pair in pairs:
            bef, aft = pair
            for i in range(text.count(bef)):
                substitutes.append(
                    (
                        text.find(
                            bef,
                            substitutes[-1][0] if i > 0 else 0,
                        ),
                        aft,
                    )
                )

        text_list = list(text)
        for ind, char in substitutes:
            text_list[ind] = char
        return "".join(text_list)

    def _reverse_row(self, line: Optional[str]) -> Optional[str]:
        """
        since we read pdf from left to right but its text is rtl, we need to reverse it except numbers and special symbols
        """
        if not line:
            return line

        parts = line.split()
        parts_out = []
        for part in reversed(parts):
            if part.isnumeric() or re.match(r"\d+:\d+", part):
                pass

            else:
                part = part[::-1]
                part = self._substitute(part, (("(", ")"), (")", "(")))
            parts_out.append(part)
        return " ".join(parts_out)

    @staticmethod
    def _parse_exam_date(date_str: str) -> Optional[str]:
        if not date_str or date_str == "امتحان كتﺒي ندارد":
            return None

        parsed_date = date_str.replace("ﺻﺒﺢ", "")
        parsed_date = parsed_date.replace("ﻋﺼر", "")
        parsed_date = parsed_date.replace("عصر", "")
        parsed_date = parsed_date.strip()
        month_map = {
            "فروردين": "01",
            "ارديبهشت": "02",
            "خرداد": "03",
            "تير": "04",
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

    def _read_metadata(self, page: pdfplumber.page.Page) -> tuple[str, str]:
        """
        return semester and update_date
        """
        title = page.extract_text_simple().split("\n")[0].strip()
        title_rev = self._reverse_row(title)
        if title_rev is None:
            logger.critical("title became none", title=title)
            raise ValueError("title is none")
        title = title_rev
        title = title.replace("ي", "ی")

        results = re.findall(r"\([^)]*\)", title)
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

    def _read_tables(
        self, page: pdfplumber.page.Page, logger: structlog.BoundLogger
    ) -> tuple[list[list[str | None]], list[str | None] | None]:
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
            return [], None

        data = []
        header = None

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

            if title != table[0]:
                logger.critical("title mismatch", table_num=table_num)
                raise ValueError("title mismatch")

            if header != table[1]:
                logger.critical("header mismatch", table_num=table_num)
                raise ValueError("header mismatch")

            table = table[3:]  # title, header, start - end
            for row in table:
                if len(row) != len(header):
                    logger.critical("Row length mismatch on page", table_num=table_num)
                    raise ValueError("row length mismatch")
            data.extend(table)
        return data, header

    @staticmethod
    def _normalize_occurance_times(df: pd.DataFrame) -> pd.DataFrame:
        """
        the occurance times in pdf are formatted into 10 columns (weekdays * 2) which determine start and end
        the code logic expect a list of objects with three fields 'weekday', 'start' and end
        this code converts it
        """
        start_suffix = " Start"
        end_suffix = " End"

        weekdays = (
            "Saturday",
            "Sunday",
            "Monday",
            "Tuesday",
            "Wednesday",
        )

        def occurance_func(row: pd.Series) -> list[dict[str, str]]:
            ans = []
            for weekday in weekdays:
                start_time = row[weekday + start_suffix]
                end_time = row[weekday + end_suffix]

                if not start_time and not end_time:
                    continue

                ans.append(
                    {
                        "weekday": weekday,
                        "start": start_time,
                        "end": end_time,
                    }
                )
            return ans

        df["course_times"] = df.apply(occurance_func, axis=1)
        drop_columns = [i + start_suffix for i in weekdays]
        drop_columns.extend([i + end_suffix for i in weekdays])
        df.drop(columns=drop_columns, inplace=True)
        return df

    @staticmethod
    def _normalize_header(header: Sequence[Optional[str]]) -> list[str]:
        header = [col.strip() if col is not None else None for col in header]

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
        df: pd.DataFrame,
        semester: str,
        update_date: str,
        header: list[str],
    ) -> pd.DataFrame:

        df = df.dropna(how="all")  # Remove completely empty rows
        df = df.reset_index(drop=True)

        column_mapping = {
            "زاينمه*/زاين شيپ": "prerequisite_corequisite",
            "ناحتما خيرات": "exam_date",
            "شيارگ": "major",
            "سﻼك": "class",
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

        df.rename(columns=column_mapping, inplace=True)
        try:
            headers_eng = [column_mapping[col] for col in header]
        except KeyError as e:
            logger.critical("unknown column in header", column=str(e), header=header)
            raise

        headers_eng.reverse()
        df = df[headers_eng]  # Reorder
        for col in df.columns:
            df[col] = df[col].apply(self._reverse_row)
        df = self._normalize_occurance_times(df)
        df["exam_date"] = df["exam_date"].apply(self._parse_exam_date)
        df["semester"] = semester
        df["univercity_update_date"] = update_date
        return df

    def read_schedule_pdf(self, pdf_path: str) -> pd.DataFrame:
        """
        Read a PDF file containing a course schedule table and return a DataFrame.

        Args:
            pdf_path: Path to the PDF file

        Returns:
            pandas DataFrame containing the course schedule
            semester of the schedule
        """
        all_data = []
        header = None

        with pdfplumber.open(pdf_path) as pdf:
            for page_num, page in track(
                enumerate(pdf.pages, 1),
                total=len(pdf.pages),
                description="Processing PDF pages...",
                transient=True,
            ):
                logger.debug(f"Processing page {page_num}...")
                if page_num == 1:
                    semester, update_date = self._read_metadata(page)
                page_data, header = self._read_tables(
                    page, logger.new(page_num=page_num)
                )
                all_data.extend(page_data)
        if not all_data:
            raise ValueError("No data found in the PDF")

        if header is None:
            raise ValueError("No header found in the PDF")
        normalized_header = self._normalize_header(header)
        df = pd.DataFrame(all_data, columns=normalized_header)
        df = self._normalize_dataframe(
            df=df, semester=semester, update_date=update_date, header=normalized_header
        )
        return df


schedule_reader = ScheduleReader()
