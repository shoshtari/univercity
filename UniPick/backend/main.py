import structlog
import typer

import commands

logger = structlog.getLogger()
structlog.configure(
    wrapper_class=structlog.make_filtering_bound_logger("INFO"),
    # processors=[
    #     structlog.processors.TimeStamper(fmt="iso"),
    #     structlog.processors.JSONRenderer(),
    # ],
)

app = typer.Typer(help="UniPick - Course selection tool for Golestan")


@app.command()
def add_pdf(pdf_path: str) -> None:
    """Add courses from PDF file to database"""
    commands.add_pdf(pdf_path)


@app.command()
def flush() -> None:
    """Flush the database and add courses"""
    commands.flush()


@app.command()
def runserver() -> None:
    """Run the backend server"""
    commands.runserver()


@app.command()
def migrate() -> None:
    """Run Database migrations"""
    commands.migrate()


if __name__ == "__main__":
    app()
