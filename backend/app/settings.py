from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


BASE_DIR = Path(__file__).resolve().parents[1]

class Settings(BaseSettings):
    API_PREFIX: str = "/api"
    PROJECT_NAME: str = "GenAI Clinical Assistant"
    VERSION: str = "1.0.0"
    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    CHROMA_DB_PATH: str = "/chroma-data"
    MED42_MODEL: str = "m42-health/med42-70b"
    GROQ_MODEL: str = "llama-3.1-8b-instant"
    GROQ_API_KEY: str
    SECRET_KEY: str
    DATABASE_URL: str
    MCP_SERVER_HOST: str = "127.0.0.1"
    MCP_SERVER_PORT: int = 9000
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    model_config = SettingsConfigDict(env_file=BASE_DIR / ".env", env_file_encoding="utf-8")

@lru_cache()
def get_settings():
    return Settings()