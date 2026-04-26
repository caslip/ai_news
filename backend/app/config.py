from pydantic_settings import BaseSettings
from functools import lru_cache
import os


class Settings(BaseSettings):
    database_url: str = "sqlite:///./ai_news.db"
    database_url_async: str = "sqlite+aiosqlite:///./ai_news.db"

    redis_url: str = "redis://localhost:6379/0"

    secret_key: str = "change-me-in-production-use-strong-random-key-here"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 1440

    openrouter_api_key: str = os.getenv("OPENROUTER_API_KEY", "")

    allowed_origins: list[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
    ]

    class Config:
        env_file = ".env"
        extra = "allow"


@lru_cache()
def get_settings():
    return Settings()


settings = get_settings()
