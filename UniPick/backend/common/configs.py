from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class WebserverSettings(BaseModel):
    HOST: str = Field("0.0.0.0")
    PORT: int = Field(8000)
    WSGI: str = Field("flask")
    THREADS: int = Field(4)
    CONNECTION_LIMIT: int = Field(100)


class JwtSettings(BaseModel):
    ENCRYPT_KEY: str = Field(min_length=32)
    DECRYPT_KEY: str = Field(min_length=32)
    ALGORITHM: str = Field("HS256")
    TTL: int = Field(24 * 60 * 3600)


class Settings(BaseSettings):
    DATABASE_URL: str = Field("sqlite:////tmp/unipick.db")

    JWT: JwtSettings = Field(default_factory=lambda _: JwtSettings())
    WEBSERVER: WebserverSettings = Field(default_factory=lambda _: WebserverSettings())

    BCRYPT_ROUNDS: int = 12
    PDF_ENGINE: str = Field("pdfplumber", pattern="pdfplumber|camelot")
    CORS_ORIGINS: list[str] = Field(["http://localhost:5173"])

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        env_nested_delimiter="__",
    )


def load_settings() -> Settings:
    """
    This doesn't do much for now. its main goal is to avoid mypy to raise errors
    """
    return Settings()
