from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DatabaseUrl: str = Field("sqlite:////tmp/unipick.db")

    WebserverHost: str = Field("0.0.0.0")
    WebserverPort: int = Field(8000)
    WebserverThreads: int = Field(4)
    WebserverConnectionLimit: int = Field(100)

    JwtEncryptKey: str = Field("a" * 32)
    JwtDecryptKey: str = Field("a" * 32)
    JwtAlgorithm: str = Field("HS256")
    JwtTTL: int = Field(24 * 60 * 3600)
    BcryptRounds: int = Field(12)
    PDFEngine: str = Field("pdfplumber")
    RunHeavyTests: bool = Field(False)
    WSGIServer: str = Field("flask")
    CorsOrigin: str = Field("http://localhost:5173")
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )


settings = Settings()
