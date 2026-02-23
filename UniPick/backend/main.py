import typer

app = typer.Typer(help="UniPick - Course selection tool for Golestan")
import commands


@app.command()
def add_pdf(pdf_path: str):
    """Add courses from PDF file to database"""
    commands.add_pdf(pdf_path)


@app.command()
def flush():
    """Flush the database and add courses"""
    commands.flush()


if __name__ == "__main__":
    app()
