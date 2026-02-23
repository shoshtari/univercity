from utils.read_schedule import read_schedule_pdf
import common.configs as configs


def add_pdf(pdf_path: str):
    """Add courses from PDF file to database"""
    df = read_schedule_pdf(pdf_path)
    df.to_sql("course", f"sqlite:///{configs.DB_FILE}", if_exists="append", index=False)
    print(df.shape)
