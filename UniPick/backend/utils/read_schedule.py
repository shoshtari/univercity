import re
import time
from typing import Any, Optional, Sequence, cast

import jdatetime
import pandas as pd
import pdfplumber
import structlog
from rich.progress import track

import common.configs as configs

logger = structlog.getLogger()


def is_ltr(text: str) -> bool:
    if text.isnumeric():
        return True

    if text[0] == "(" and text[-1] == ")":
        text = text[1: len(text) - 1]

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
            or not isinstance(date_str, str)
        ):
            return None

        parsed_date = date_str.replace("ﺻﺒﺢ", "")
        parsed_date = parsed_date.replace("ﺻبﺢ", "")
        parsed_date = parsed_date.replace("ﻋﺼر", "")
        parsed_date = parsed_date.replace("عصر", "")
        parsed_date = parsed_date.replace("ﻋصر", "")
        parsed_date = parsed_date.strip()
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
            parsed_date = jdatetime.datetime.strptime(
                parsed_date, "%d %m %Y").date()
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
            update_date = results[1].replace(
                "به روز رسانی درتاریخ: ", "").strip()
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
        header = []

        for table_num, table in enumerate(tables):
            if not table:
                continue

            logger.debug("found table", table_num=table_num,
                         table_length=len(table))
            if len(table) <= 2:
                logger.critical("table counts are too low",
                                table_count=len(table))
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
                    logger.critical(
                        "Row length mismatch on page", table_num=table_num)
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

    def _read_data_with_camelot(
        self, pdf_path: str
    ) -> tuple[list[list[Any]], list[Optional[str]]]:

        import camelot
        tables = camelot.read_pdf(  # type: ignore[attr-defined]
            pdf_path, pages="1-end", flavor="lattice", parallel=True
        )

        # remove first three rows (title, header, start-end)
        df = pd.concat([table.df.iloc[3:]
                       for table in tables], ignore_index=True)
        header = tables[0].df.iloc[1].tolist()
        return df.values.tolist(), header

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

                if (not start_time or not isinstance(start_time, str)) and (
                    not end_time or not isinstance(end_time, str)
                ):
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
        header = [
            col.strip() if col else None for col in header
        ]  # no empty or none header
        # since pdfplumber return None and camelot return '' this works for both

        output: list[str] = []
        for i in range(len(header)):
            val = header[i]
            if isinstance(val, str):
                output.append(val)
            else:
                if i == 0 or not output:
                    logger.critical(
                        "got empty header at first col", header=header)
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

        # df = df[df.apply(lambda row: not all(x == '' for x in row), axis=1)]
        df = df.replace("", None)
        df = df.dropna(how="all")  # Remove completely empty rows
        df = df.reset_index(drop=True)

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

        df.rename(columns=column_mapping, inplace=True)
        try:
            headers_eng = [column_mapping[col] for col in header]
        except KeyError as e:
            logger.critical("unknown column in header",
                            column=str(e), header=header)
            raise

        headers_eng.reverse()
        df = df[headers_eng]  # Reorder
        for col in df.columns:
            df[col] = df[col].apply(self._reverse_row)
            df[col] = df[col].apply(
                lambda val: val.replace(
                    "ي", "ی") if isinstance(val, str) else val
            )
            df[col] = df[col].apply(
                lambda val: val.replace(
                    "ﺒ", "ب") if isinstance(val, str) else val
            )
            df[col] = df[col].apply(
                lambda val: val.replace(
                    "ﺼ", "ص") if isinstance(val, str) else val
            )
            df[col] = df[col].apply(
                lambda val: val.replace(
                    "ﻋ", "ع") if isinstance(val, str) else val
            )
            df[col] = df[col].apply(
                lambda val: val.replace(
                    "ك", "ک") if isinstance(val, str) else val
            )
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

        semester, update_date = self._read_metadata(pdf_path)

        start = time.time()
        match configs.PDF_ENGINE:
            case "pdfplumber":
                data, header = self._read_data_with_pdfplumber(
                    pdf_path=pdf_path)
            case "camelot":
                data, header = self._read_data_with_camelot(pdf_path=pdf_path)
            case _:
                raise ValueError(f"unknown pdf engine {configs.PDF_ENGINE}")
        logger.debug("pdf_parsing_time", duration=time.time() - start)
        if not data:
            raise ValueError("No data found in the PDF")

        if header is None:
            raise ValueError("No header found in the PDF")

        normalized_header = self._normalize_header(header)
        df = pd.DataFrame(data, columns=normalized_header)
        df = self._normalize_dataframe(
            df=df, semester=semester, update_date=update_date, header=normalized_header
        )
        return df


schedule_reader = ScheduleReader()
