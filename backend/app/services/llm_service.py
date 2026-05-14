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


class LLMService:
    """
    Unified LLM service using LangChain.
    Supports DeepSeek, OpenRouter, and direct OpenAI APIs.
    
    Usage:
        # Non-streaming
        llm = LLMService()
        response = await llm.ainvoke([{"role": "user", "content": "Hello"}])
        
        # With specific model
        llm = LLMService(model="deepseek/deepseek-chat-v3-5:free")
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
        "deepseek/deepseek-chat-v3-5:free": "openrouter",
        "anthropic/claude-3.5-sonnet": "openrouter",
        "openai/gpt-4o": "openrouter",
        "deepseek-chat": "deepseek",
        "deepseek-coder": "deepseek",
    }
    
    def __init__(self, model: Optional[str] = None, provider: Optional[str] = None):
        """
        Initialize LLM service.
        
        Args:
            model: Optional model name. If not provided, uses config's default_model.
                   If provider is specified, uses provider's default model.
            provider: Optional provider override. If not provided, infers from model
                     or uses config's llm_provider. Options: "deepseek", "openrouter", "openai"
        """
        self._model = model
        self._provider = provider
        
        # Determine effective provider
        if provider:
            # Validate provider
            valid_providers = ["deepseek", "openrouter", "openai"]
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
        
        logger.info(f"LLMService initialized with model={self.model}, provider={self.provider}")
    
    def _get_llm(self, streaming: bool = False, **kwargs):
        """Get the appropriate LLM instance based on provider."""
        if self.provider == "deepseek":
            if not settings.deepseek_api_key:
                raise ValueError("DeepSeek API key not configured. Set DEEPSEEK_API_KEY in environment.")
            return ChatOpenAI(
                model=self.model,
                api_key=settings.deepseek_api_key,
                base_url=settings.deepseek_base_url,
                streaming=streaming,
                **kwargs
            )
        elif self.provider == "openai":
            if not settings.openai_api_key:
                raise ValueError("OpenAI API key not configured. Set OPENAI_API_KEY in environment.")
            return ChatOpenAI(
                model=self.model,
                api_key=settings.openai_api_key,
                streaming=streaming,
                **kwargs
            )
        else:  # openrouter
            if not settings.openrouter_api_key:
                raise ValueError("OpenRouter API key not configured. Set OPENROUTER_API_KEY in environment.")
            return ChatOpenAI(
                model=self.model,
                api_key=settings.openrouter_api_key,
                base_url="https://openrouter.ai/api/v1",
                streaming=streaming,
                extra_headers={
                    "HTTP-Referer": "https://ai-news-aggregator",
                    "X-Title": "AI News Aggregator Writer",
                },
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
        
        logger.debug(f"Invoking LLM with {len(messages)} messages")
        response = await llm.ainvoke(langchain_messages)
        
        content = response.content if hasattr(response, 'content') else str(response)
        logger.debug(f"LLM response received, length={len(content)}")
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
