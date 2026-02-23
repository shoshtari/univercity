import pdfplumber
from rich.progress import track
import jdatetime
import pandas as pd
from typing import Optional

import logging
from pythonjsonlogger import jsonlogger

logger = logging.getLogger(__name__)

handler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter()
handler.setFormatter(formatter)
logger.addHandler(handler)


def reverse_row(line: Optional[str]):
    if not line:
        return line
    parts = line.split()
    ans = ""
    for part in reversed(parts):
        if part.isnumeric():
            ans += part + " "
        else:
            ans += part[::-1] + " "
    return ans.strip()


def parse_exam_date(date_str):
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
        return parsed_date.isoformat()
    except ValueError:
        logger.warning(
            "Failed to parse exam date",
            extra={"date_str": date_str, "parsed_date": parsed_date},
        )
        return date_str.strip() if date_str else None


def read_schedule_pdf(pdf_path: str) -> pd.DataFrame:
    """
    Read a PDF file containing a course schedule table and return a DataFrame.

    Args:
        pdf_path: Path to the PDF file

    Returns:
        pandas DataFrame containing the course schedule
    """
    all_data = []
    header = None
    title = None

    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in track(
            enumerate(pdf.pages, 1),
            total=len(pdf.pages),
            description="Processing PDF pages...",
        ):
            logger.info(f"Processing page {page_num}...")

            # Extract tables from the page
            table_settings = {
                "vertical_strategy": "lines",
                "horizontal_strategy": "lines",
                "intersection_tolerance": 3,
            }
            tables = page.extract_tables(table_settings=table_settings)
            if not tables:
                logger.warning(f"No tables found on page {page_num}")
                continue

            for table_num, table in enumerate(tables):
                if not table:
                    continue

                logger.info(f"  Found table {table_num + 1} with {len(table)} rows")
                assert len(table) > 2

                if table_num == 0:
                    title = table[0]
                    header = table[1]

                assert (
                    title == table[0]
                ), f"Title mismatch on page {page_num}, table {table_num + 1}"
                assert (
                    header == table[1]
                ), f"Header mismatch on page {page_num}, table {table_num + 1}"

                table = table[3:]  # title, header, start - end
                for row in table:
                    assert len(row) == len(
                        header
                    ), f"Row length mismatch on page {page_num}, table {table_num + 1}"
                all_data.extend(table[2:])

    if not all_data:
        raise ValueError("No data found in the PDF")

    if header is None:
        raise ValueError("No header found in the PDF")

    header = [col.strip() if col else None for col in header]
    for i in range(len(header)):
        if header[i] is None:
            assert i > 0
            before = header[i - 1]
            assert before in [
                "هﺒنش",
                "هﺒنشكي",
                "هﺒنشود",
                "هﺒنش هس",
                "هﺒنشراهچ",
            ], f"Unexpected header value: {before}"
            weekday = header[i - 1]
            header[i] = f"{weekday} شروع"
            header[i - 1] = f"{weekday} پایان"

    df = pd.DataFrame(all_data, columns=header)

    df = df.dropna(how="all")  # Remove completely empty rows
    df = df.reset_index(drop=True)

    column_mapping = {
        "زاينمه*/زاين شيپ": "Prerequisite/Corequisite",
        "ناحتما خيرات": "Exam Date",
        "شيارگ": "Major",
        "سﻼك": "Class",
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
        "سردم": "Instructor",
        "دحاو": "Units",
        "هورگ": "Group",
        "سرد هرامش": "Course Number",
        "سرد مان": "Course Name",
    }

    df = df.rename(columns=column_mapping)
    headers_eng = [column_mapping[col] for col in header]
    headers_eng.reverse()
    df = df[headers_eng]  # Reorder
    for col in df.columns:
        df[col] = df[col].apply(reverse_row)
    df["Exam Date"] = df["Exam Date"].apply(parse_exam_date)
    return df
