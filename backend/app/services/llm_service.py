"""
Unified LLM Service using LangChain.
Supports DeepSeek, OpenRouter, and direct OpenAI APIs.
"""
import logging
from typing import AsyncIterator, Optional

from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain_core.outputs import ChatGenerationChunk

from app.config import settings

logger = logging.getLogger(__name__)


def get_user_api_key(user_id: str, provider: str) -> Optional[str]:
    """
    Get user's API key from database for the specified provider.
    Returns the decrypted API key or None if not found.
    """
    try:
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        
        from app.config import settings as app_settings
        engine = create_engine(app_settings.database_url)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        
        try:
            from app.models.api_key import ApiKey
            from app.services.encryption import get_encryption_service
            
            api_key_record = db.query(ApiKey).filter(
                ApiKey.user_id == user_id,
                ApiKey.provider == provider,
                ApiKey.is_active == True
            ).first()
            
            if api_key_record:
                encryption_service = get_encryption_service()
                return encryption_service.decrypt(api_key_record.encrypted_key)
            return None
        finally:
            db.close()
    except Exception as e:
        logger.warning(f"Failed to get user API key from database: {e}")
        return None


class LLMService:
    """
    Unified LLM service using LangChain.
    Supports DeepSeek, OpenRouter, and direct OpenAI APIs.
    
    Usage:
        # Non-streaming
        llm = LLMService()
        response = await llm.ainvoke([{"role": "user", "content": "Hello"}])
        
        # With specific model
        llm = LLMService(model="google/gemini-2.0-flash-thinking-exp:free")
        response = await llm.ainvoke([{"role": "user", "content": "Hello"}])
        
        # With specific provider
        llm = LLMService(provider="openai")
        response = await llm.ainvoke([{"role": "user", "content": "Hello"}])
        
        # Streaming
        async for chunk in llm.astream([{"role": "user", "content": "Hello"}]):
            print(chunk, end="")
    """
    
    # Model to provider mapping
    MODEL_PROVIDER = {
        "anthropic/claude-3.5-sonnet": "openrouter",
        "openai/gpt-4o": "openrouter",
        "google/gemini-2.0-flash-thinking-exp:free": "openrouter",
        "deepseek-chat": "deepseek",
        "deepseek-v4-flash": "deepseek",
        "deepseek-v4-pro": "deepseek",
        "deepseek-coder": "deepseek",
    }
    
    def __init__(self, model: Optional[str] = None, provider: Optional[str] = None, user_id: Optional[str] = None):
        """
        Initialize LLM service.
        
        Args:
            model: Optional model name. If not provided, uses config's default_model.
                   If provider is specified, uses provider's default model.
            provider: Optional provider override. If not provided, infers from model
                     or uses config's llm_provider. Options: "deepseek", "openrouter", "openai"
            user_id: Optional user ID to fetch user-specific API key from database.
        """
        self._model = model
        self._provider = provider
        self._user_id = user_id
        
        # Determine effective provider
        if provider:
            # Validate provider
            valid_providers = ["deepseek", "openrouter", "openai", "moonshot", "minimax", "gemini", "anthropic"]
            if provider not in valid_providers:
                logger.warning(f"Invalid provider '{provider}', defaulting to 'deepseek'")
                self.provider = "deepseek"
            else:
                self.provider = provider
        elif model and model in self.MODEL_PROVIDER:
            self.provider = self.MODEL_PROVIDER[model]
        else:
            self.provider = settings.effective_llm_provider
        
        # Determine effective model
        if model:
            self.model = model
        elif self.provider == "deepseek":
            self.model = settings.deepseek_model
        elif self.provider == "openai":
            self.model = settings.openai_model
        else:
            self.model = settings.openrouter_model
        
        logger.info(f"LLM: {self.model} via {self.provider}, user_id={user_id}")
    
    def _get_api_key(self) -> str:
        """Get API key - first try user-specific key, then fall back to global config."""
        # Try user-specific API key first
        if self._user_id:
            user_key = get_user_api_key(self._user_id, self.provider)
            if user_key:
                logger.info(f"Using user-specific API key for {self.provider}")
                return user_key
        
        # Fall back to global config
        if self.provider == "deepseek":
            return settings.deepseek_api_key
        elif self.provider == "openai":
            return settings.openai_api_key
        elif self.provider == "openrouter":
            return settings.openrouter_api_key
        elif self.provider == "moonshot":
            return settings.openai_api_key  # Moonshot uses OpenAI-compatible API
        elif self.provider == "minimax":
            return settings.openai_api_key  # MiniMax uses OpenAI-compatible API
        elif self.provider == "gemini":
            return settings.openai_api_key  # Gemini can use OpenAI-compatible API
        elif self.provider == "anthropic":
            return settings.openai_api_key  # Anthropic uses different API
        
        raise ValueError(f"Unknown provider: {self.provider}")
    
    def _get_base_url(self) -> Optional[str]:
        """Get base URL for the provider."""
        if self.provider == "deepseek":
            return settings.deepseek_base_url
        elif self.provider == "kimi":
            return "https://api.moonshot.cn/v1"
        elif self.provider == "minimax":
            return "https://api.minimax.chat/v1"
        elif self.provider == "openrouter":
            return "https://openrouter.ai/api/v1"
        elif self.provider == "gemini":
            return "https://generativelanguage.googleapis.com/v1beta"
        elif self.provider == "anthropic":
            return "https://api.anthropic.com/v1"
        return None  # OpenAI and others use default base URL
    
    def _get_llm(self, streaming: bool = False, **kwargs):
        """Get the appropriate LLM instance based on provider."""
        api_key = self._get_api_key()
        
        if not api_key:
            raise ValueError(f"{self.provider} API key not configured. Please add it in settings.")
        
        base_url = self._get_base_url()
        
        extra_headers = {}
        if self.provider == "openrouter":
            extra_headers = {
                "HTTP-Referer": "https://ai-news-aggregator",
                "X-Title": "AI News Aggregator Writer",
            }
        
        return ChatOpenAI(
            model=self.model,
            api_key=api_key,
            base_url=base_url,
            streaming=streaming,
            extra_headers=extra_headers if extra_headers else None,
            **kwargs
        )
    
    async def ainvoke(self, messages: list[dict], **kwargs) -> str:
        """
        Async invoke — returns full response string.
        
        Args:
            messages: List of message dicts with 'role' and 'content' keys.
                     Roles: 'system', 'user', 'assistant'
            **kwargs: Additional arguments passed to LLM (temperature, max_tokens, etc.)
        
        Returns:
            Response content as string.
        """
        llm = self._get_llm(streaming=False)
        langchain_messages = self._to_langchain_messages(messages)
        
        logger.debug(f"Invoking LLM, messages={len(messages)}")
        response = await llm.ainvoke(langchain_messages)
        
        content = response.content if hasattr(response, 'content') else str(response)
        return content
    
    async def astream(self, messages: list[dict], **kwargs) -> AsyncIterator[str]:
        """
        Async stream — yields content chunks for SSE.
        
        Args:
            messages: List of message dicts with 'role' and 'content' keys.
            **kwargs: Additional arguments passed to LLM.
        
        Yields:
            Content chunks as they arrive.
        """
        llm = self._get_llm(streaming=True)
        langchain_messages = self._to_langchain_messages(messages)
        
        logger.debug(f"Streaming LLM with {len(messages)} messages")
        async for chunk in llm.astream(langchain_messages):
            if hasattr(chunk, 'content') and chunk.content:
                yield chunk.content
    
    def _to_langchain_messages(self, messages: list[dict]) -> list[BaseMessage]:
        """
        Convert our dict messages to LangChain messages.
        
        Args:
            messages: List of dicts with 'role' and 'content'.
        
        Returns:
            List of LangChain BaseMessage objects.
        """
        result = []
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            
            if role == "system":
                result.append(SystemMessage(content=content))
            elif role == "assistant":
                result.append(AIMessage(content=content))
            else:  # user or any other role
                result.append(HumanMessage(content=content))
        
        return result
    
    @staticmethod
    def is_deepseek_model(model: str) -> bool:
        """Check if a model is a DeepSeek model."""
        return "deepseek" in model.lower()
    
    @staticmethod
    def get_available_providers() -> dict[str, list[str]]:
        """Get available providers and their models."""
        return {
            "deepseek": ["deepseek-chat", "deepseek-coder"],
            "openai": ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo"],
            "openrouter": settings.available_models,
        }
