from pydantic import field_validator
from pydantic_settings import BaseSettings
from functools import lru_cache
import os
import logging

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    database_url: str = "sqlite:///./ai_news.db"
    database_url_async: str = "sqlite+aiosqlite:///./ai_news.db"

    redis_url: str = "redis://localhost:6379/0"

    secret_key: str = "change-me-in-production-use-strong-random-key-here"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 1440

    # LLM Provider selection: "deepseek" | "openrouter" | "openai"
    llm_provider: str = os.getenv("LLM_PROVIDER", "deepseek")

    # DeepSeek configuration
    deepseek_api_key: str = os.getenv("DEEPSEEK_API_KEY", "")
    deepseek_base_url: str = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
    deepseek_model: str = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")

    # OpenRouter configuration (existing)
    openrouter_api_key: str = os.getenv("OPENROUTER_API_KEY", "")
    openrouter_model: str = os.getenv("OPENROUTER_MODEL", "anthropic/claude-3.5-sonnet")

    # OpenAI configuration (direct)
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4o")

    # Model configuration
    default_model: str = os.getenv("DEFAULT_MODEL", "deepseek/deepseek-chat-v3-5:free")
    available_models: list[str] = [
        "deepseek/deepseek-chat-v3-5:free",
        "anthropic/claude-3.5-sonnet",
        "openai/gpt-4o",
    ]

    allowed_origins: list[str] | str = [
        # Local development
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:3002",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
        "http://127.0.0.1:3002",
        # Vercel production
        "https://ai-news-nine-phi.vercel.app",
        # Vercel preview deployments (wildcard pattern not supported, list common patterns)
        "https://ai-news-git-main-caslips-projects.vercel.app",
    ]

    @field_validator("allowed_origins", mode="before")
    @classmethod
    def parse_origins(cls, v):
        if isinstance(v, list):
            return v
        if isinstance(v, str):
            if not v.strip():
                return [
                    "http://localhost:3000",
                    "http://localhost:3001",
                    "http://localhost:3002",
                    "http://127.0.0.1:3000",
                    "http://127.0.0.1:3001",
                    "http://127.0.0.1:3002",
                ]
            return [o.strip() for o in v.split(",") if o.strip()]
        return v

    @property
    def effective_llm_provider(self) -> str:
        """Get the effective LLM provider, defaulting to deepseek."""
        providers = ["deepseek", "openrouter", "openai"]
        if self.llm_provider not in providers:
            logger.warning(f"Invalid llm_provider '{self.llm_provider}', defaulting to 'deepseek'")
            return "deepseek"
        return self.llm_provider

    @property
    def current_llm_model(self) -> str:
        """Get the current LLM model based on provider."""
        if self.effective_llm_provider == "deepseek":
            return self.deepseek_model
        elif self.effective_llm_provider == "openai":
            return self.openai_model
        else:
            return self.openrouter_model

    class Config:
        env_file = ".env"
        extra = "allow"


@lru_cache()
def get_settings():
    return Settings()


settings = get_settings()
