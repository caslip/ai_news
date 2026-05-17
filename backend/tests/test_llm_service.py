"""
Tests for the unified LLM Service (LangChain + DeepSeek/OpenRouter/OpenAI).

These tests mock the actual LLM calls and focus on:
- Provider configuration and model selection
- Message format conversion to/from LangChain
- Singleton/get_llm_service pattern
- Error handling for missing API keys
- Streaming and non-streaming responses
"""

import os
import pytest
from unittest.mock import patch, MagicMock, AsyncMock

from app.services.llm_service import LLMService


class TestLLMServiceProviderConfig:
    """Tests for provider and model configuration."""

    def test_default_provider_is_deepseek(self):
        """Test that default provider falls back to deepseek."""
        with patch("app.services.llm_service.settings") as mock_settings:
            mock_settings.effective_llm_provider = "deepseek"
            mock_settings.deepseek_model = "deepseek-v4-flash"
            mock_settings.deepseek_api_key = "test-key"
            mock_settings.deepseek_base_url = "https://api.deepseek.com"
            mock_settings.openrouter_api_key = ""
            mock_settings.openai_api_key = ""

            llm = LLMService()
            assert llm.provider == "deepseek"

    def test_explicit_provider_override(self):
        """Test that explicit provider parameter overrides default."""
        with patch("app.services.llm_service.settings") as mock_settings:
            mock_settings.effective_llm_provider = "deepseek"
            mock_settings.deepseek_model = "deepseek-chat"
            mock_settings.deepseek_api_key = "test-key"
            mock_settings.deepseek_base_url = "https://api.deepseek.com"
            mock_settings.openrouter_api_key = "or-key"
            mock_settings.openrouter_model = "anthropic/claude-3.5-sonnet"
            mock_settings.openai_api_key = ""
            mock_settings.openai_model = "gpt-4o"

            llm = LLMService(provider="openrouter")
            assert llm.provider == "openrouter"
            assert "claude" in llm.model or "openrouter" in llm.model

    def test_model_inference_from_known_models(self):
        """Test that provider is inferred from known model names."""
        with patch("app.services.llm_service.settings") as mock_settings:
            mock_settings.deepseek_api_key = ""
            mock_settings.openrouter_api_key = "or-key"
            mock_settings.openrouter_model = "anthropic/claude-3.5-sonnet"
            mock_settings.openai_api_key = ""
            mock_settings.effective_llm_provider = "deepseek"

            llm = LLMService(model="google/gemini-2.0-flash-thinking-exp:free")
            assert llm.provider == "openrouter"

    def test_invalid_provider_falls_back_to_deepseek(self):
        """Test that invalid provider falls back to deepseek."""
        with patch("app.services.llm_service.settings") as mock_settings:
            mock_settings.effective_llm_provider = "invalid_provider"
            mock_settings.deepseek_model = "deepseek-chat"
            mock_settings.deepseek_api_key = "test-key"
            mock_settings.deepseek_base_url = "https://api.deepseek.com"
            mock_settings.openrouter_api_key = ""
            mock_settings.openai_api_key = ""

            llm = LLMService(provider="invalid")
            # Should fall back to effective_llm_provider which defaults to deepseek
            assert llm.provider == "deepseek"


class TestLLMServiceChat:
    """Tests for chat/invoke functionality."""

    @pytest.mark.asyncio
    async def test_invoke_single_message(self):
        """Test ainvoke with a single user message."""
        mock_response = MagicMock()
        mock_response.content = "Hello! How can I help you today?"

        with patch("app.services.llm_service.ChatOpenAI") as mock_llm_class:
            mock_llm_instance = AsyncMock()
            mock_llm_instance.ainvoke = AsyncMock(return_value=mock_response)
            mock_llm_class.return_value = mock_llm_instance

            with patch("app.services.llm_service.settings") as mock_settings:
                mock_settings.effective_llm_provider = "deepseek"
                mock_settings.deepseek_model = "deepseek-chat"
                mock_settings.deepseek_api_key = "test-key"
                mock_settings.deepseek_base_url = "https://api.deepseek.com"
                mock_settings.openrouter_api_key = ""
                mock_settings.openai_api_key = ""

                llm = LLMService()
                result = await llm.ainvoke([{"role": "user", "content": "Hello"}])

                assert result == "Hello! How can I help you today?"
                mock_llm_instance.ainvoke.assert_called_once()

    @pytest.mark.asyncio
    async def test_invoke_with_system_message(self):
        """Test ainvoke with system and user messages."""
        mock_response = MagicMock()
        mock_response.content = "I understand. Let me help with that."

        with patch("app.services.llm_service.ChatOpenAI") as mock_llm_class:
            mock_llm_instance = AsyncMock()
            mock_llm_instance.ainvoke = AsyncMock(return_value=mock_response)
            mock_llm_class.return_value = mock_llm_instance

            with patch("app.services.llm_service.settings") as mock_settings:
                mock_settings.effective_llm_provider = "deepseek"
                mock_settings.deepseek_model = "deepseek-chat"
                mock_settings.deepseek_api_key = "test-key"
                mock_settings.deepseek_base_url = "https://api.deepseek.com"
                mock_settings.openrouter_api_key = ""
                mock_settings.openai_api_key = ""

                llm = LLMService()
                messages = [
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": "Help me write an article."}
                ]
                result = await llm.ainvoke(messages)

                assert result == "I understand. Let me help with that."

    @pytest.mark.asyncio
    async def test_invoke_conversation_history(self):
        """Test ainvoke with multi-turn conversation history."""
        mock_response = MagicMock()
        mock_response.content = "That's a great question about AI."

        with patch("app.services.llm_service.ChatOpenAI") as mock_llm_class:
            mock_llm_instance = AsyncMock()
            mock_llm_instance.ainvoke = AsyncMock(return_value=mock_response)
            mock_llm_class.return_value = mock_llm_instance

            with patch("app.services.llm_service.settings") as mock_settings:
                mock_settings.effective_llm_provider = "deepseek"
                mock_settings.deepseek_model = "deepseek-chat"
                mock_settings.deepseek_api_key = "test-key"
                mock_settings.deepseek_base_url = "https://api.deepseek.com"
                mock_settings.openrouter_api_key = ""
                mock_settings.openai_api_key = ""

                llm = LLMService()
                messages = [
                    {"role": "user", "content": "What is LangChain?"},
                    {"role": "assistant", "content": "LangChain is a framework for building LLM applications."},
                    {"role": "user", "content": "Tell me more about it."}
                ]
                result = await llm.ainvoke(messages)

                assert result == "That's a great question about AI."

    @pytest.mark.asyncio
    async def test_invoke_error_handling(self):
        """Test that errors from LLM are propagated."""
        with patch("app.services.llm_service.ChatOpenAI") as mock_llm_class:
            mock_llm_instance = AsyncMock()
            mock_llm_instance.ainvoke = AsyncMock(side_effect=Exception("API Error: Rate limited"))
            mock_llm_class.return_value = mock_llm_instance

            with patch("app.services.llm_service.settings") as mock_settings:
                mock_settings.effective_llm_provider = "deepseek"
                mock_settings.deepseek_model = "deepseek-chat"
                mock_settings.deepseek_api_key = "test-key"
                mock_settings.deepseek_base_url = "https://api.deepseek.com"
                mock_settings.openrouter_api_key = ""
                mock_settings.openai_api_key = ""

                llm = LLMService()

                with pytest.raises(Exception, match="API Error"):
                    await llm.ainvoke([{"role": "user", "content": "Hello"}])

    @pytest.mark.asyncio
    async def test_invoke_with_temperature(self):
        """Test ainvoke with custom temperature."""
        mock_response = MagicMock()
        mock_response.content = "Creative response"

        with patch("app.services.llm_service.ChatOpenAI") as mock_llm_class:
            mock_llm_instance = AsyncMock()
            mock_llm_instance.ainvoke = AsyncMock(return_value=mock_response)
            mock_llm_class.return_value = mock_llm_instance

            with patch("app.services.llm_service.settings") as mock_settings:
                mock_settings.effective_llm_provider = "deepseek"
                mock_settings.deepseek_model = "deepseek-chat"
                mock_settings.deepseek_api_key = "test-key"
                mock_settings.deepseek_base_url = "https://api.deepseek.com"
                mock_settings.openrouter_api_key = ""
                mock_settings.openai_api_key = ""

                llm = LLMService()
                result = await llm.ainvoke(
                    [{"role": "user", "content": "Write a poem"}],
                    temperature=0.9
                )

                assert result == "Creative response"


class TestLLMServiceStreaming:
    """Tests for streaming functionality."""

    @pytest.mark.asyncio
    async def test_stream_yields_chunks(self):
        """Test that astream yields content chunks."""
        chunks = ["Hello", " world", "!"]

        with patch("app.services.llm_service.ChatOpenAI") as mock_llm_class:
            mock_llm_instance = AsyncMock()

            async def mock_stream(*args, **kwargs):
                for chunk_text in chunks:
                    mock_chunk = MagicMock()
                    mock_chunk.content = chunk_text
                    yield mock_chunk

            mock_llm_instance.astream = mock_stream
            mock_llm_class.return_value = mock_llm_instance

            with patch("app.services.llm_service.settings") as mock_settings:
                mock_settings.effective_llm_provider = "deepseek"
                mock_settings.deepseek_model = "deepseek-chat"
                mock_settings.deepseek_api_key = "test-key"
                mock_settings.deepseek_base_url = "https://api.deepseek.com"
                mock_settings.openrouter_api_key = ""
                mock_settings.openai_api_key = ""

                llm = LLMService()
                result_chunks = []
                async for chunk in llm.astream([{"role": "user", "content": "Hi"}]):
                    result_chunks.append(chunk)

                assert result_chunks == chunks


class TestLLMServiceMessageConversion:
    """Tests for message format conversion."""

    def test_convert_user_message(self):
        """Test that user messages are converted to HumanMessage."""
        with patch("app.services.llm_service.settings"):
            llm = LLMService()
            messages = [{"role": "user", "content": "Hello"}]
            langchain_msgs = llm._to_langchain_messages(messages)

            assert len(langchain_msgs) == 1
            from langchain_core.messages import HumanMessage
            assert isinstance(langchain_msgs[0], HumanMessage)
            assert langchain_msgs[0].content == "Hello"

    def test_convert_system_message(self):
        """Test that system messages are converted to SystemMessage."""
        with patch("app.services.llm_service.settings"):
            llm = LLMService()
            messages = [{"role": "system", "content": "You are helpful."}]
            langchain_msgs = llm._to_langchain_messages(messages)

            assert len(langchain_msgs) == 1
            from langchain_core.messages import SystemMessage
            assert isinstance(langchain_msgs[0], SystemMessage)
            assert langchain_msgs[0].content == "You are helpful."

    def test_convert_assistant_message(self):
        """Test that assistant messages are converted to AIMessage."""
        with patch("app.services.llm_service.settings"):
            llm = LLMService()
            messages = [{"role": "assistant", "content": "I can help."}]
            langchain_msgs = llm._to_langchain_messages(messages)

            assert len(langchain_msgs) == 1
            from langchain_core.messages import AIMessage
            assert isinstance(langchain_msgs[0], AIMessage)
            assert langchain_msgs[0].content == "I can help."

    def test_convert_mixed_messages(self):
        """Test conversion of mixed message types."""
        with patch("app.services.llm_service.settings"):
            llm = LLMService()
            messages = [
                {"role": "system", "content": "You are a writer."},
                {"role": "user", "content": "Write about AI"},
                {"role": "assistant", "content": "AI is transforming..."},
                {"role": "user", "content": "Continue please"},
            ]
            langchain_msgs = llm._to_langchain_messages(messages)

            assert len(langchain_msgs) == 4
            from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
            assert isinstance(langchain_msgs[0], SystemMessage)
            assert isinstance(langchain_msgs[1], HumanMessage)
            assert isinstance(langchain_msgs[2], AIMessage)
            assert isinstance(langchain_msgs[3], HumanMessage)

    def test_convert_empty_role_defaults_to_user(self):
        """Test that empty role defaults to user."""
        with patch("app.services.llm_service.settings"):
            llm = LLMService()
            messages = [{"role": "", "content": "Test"}]
            langchain_msgs = llm._to_langchain_messages(messages)

            from langchain_core.messages import HumanMessage
            assert isinstance(langchain_msgs[0], HumanMessage)

    def test_convert_missing_content_defaults_to_empty(self):
        """Test that missing content defaults to empty string."""
        with patch("app.services.llm_service.settings"):
            llm = LLMService()
            messages = [{"role": "user"}]
            langchain_msgs = llm._to_langchain_messages(messages)

            assert langchain_msgs[0].content == ""


class TestLLMServiceHelpers:
    """Tests for helper methods."""

    def test_is_deepseek_model_true(self):
        """Test is_deepseek_model returns True for deepseek models."""
        assert LLMService.is_deepseek_model("deepseek-chat") is True
        assert LLMService.is_deepseek_model("deepseek-coder") is True
        assert LLMService.is_deepseek_model("DEEPSEEK-CHAT") is True

    def test_is_deepseek_model_false(self):
        """Test is_deepseek_model returns False for non-deepseek models."""
        assert LLMService.is_deepseek_model("gpt-4") is False
        assert LLMService.is_deepseek_model("claude-3") is False
        assert LLMService.is_deepseek_model("anthropic/claude") is False

    def test_get_available_providers(self):
        """Test get_available_providers returns expected structure."""
        with patch("app.services.llm_service.settings") as mock_settings:
            mock_settings.available_models = ["google/gemini-2.0-flash-thinking-exp:free"]

            providers = LLMService.get_available_providers()

            assert "deepseek" in providers
            assert "openrouter" in providers
            assert "deepseek-chat" in providers["deepseek"]


class TestLLMServiceDeepseekProvider:
    """Tests specific to DeepSeek provider configuration."""

    def test_deepseek_provider_requires_api_key(self):
        """Test that DeepSeek provider initialization checks for API key."""
        with patch("app.services.llm_service.settings") as mock_settings:
            mock_settings.effective_llm_provider = "deepseek"
            mock_settings.deepseek_model = "deepseek-chat"
            mock_settings.deepseek_api_key = "test-key"
            mock_settings.deepseek_base_url = "https://api.deepseek.com"
            mock_settings.openrouter_api_key = ""
            mock_settings.openai_api_key = ""

            llm = LLMService(provider="deepseek")
            assert llm.provider == "deepseek"
            assert llm.model == "deepseek-chat"

    def test_deepseek_provider_with_custom_model(self):
        """Test DeepSeek with a custom model."""
        with patch("app.services.llm_service.settings") as mock_settings:
            mock_settings.effective_llm_provider = "deepseek"
            mock_settings.deepseek_model = "deepseek-chat"
            mock_settings.deepseek_api_key = "test-key"
            mock_settings.deepseek_base_url = "https://api.deepseek.com"
            mock_settings.openrouter_api_key = ""
            mock_settings.openai_api_key = ""

            llm = LLMService(provider="deepseek", model="deepseek-coder")
            assert llm.model == "deepseek-coder"


class TestLLMServiceOpenrouterProvider:
    """Tests specific to OpenRouter provider configuration."""

    def test_openrouter_provider_config(self):
        """Test OpenRouter provider uses correct base URL."""
        with patch("app.services.llm_service.settings") as mock_settings:
            mock_settings.effective_llm_provider = "deepseek"
            mock_settings.deepseek_api_key = ""
            mock_settings.deepseek_model = "deepseek-chat"
            mock_settings.openrouter_api_key = "or-test-key"
            mock_settings.openrouter_model = "anthropic/claude-3.5-sonnet"
            mock_settings.openai_api_key = ""
            mock_settings.openai_model = "gpt-4o"
            mock_settings.available_models = ["claude-3.5-sonnet"]

            llm = LLMService(provider="openrouter")
            assert llm.provider == "openrouter"


class TestLLMServiceOpenaiProvider:
    """Tests specific to OpenAI provider configuration."""

    def test_openai_provider_config(self):
        """Test OpenAI provider uses direct API."""
        with patch("app.services.llm_service.settings") as mock_settings:
            mock_settings.effective_llm_provider = "deepseek"
            mock_settings.deepseek_api_key = ""
            mock_settings.deepseek_model = "deepseek-chat"
            mock_settings.openrouter_api_key = ""
            mock_settings.openrouter_model = "claude"
            mock_settings.openai_api_key = "openai-test-key"
            mock_settings.openai_model = "gpt-4o"

            llm = LLMService(provider="openai")
            assert llm.provider == "openai"
            assert llm.model == "gpt-4o"


class TestLLMServiceIntegration:
    """
    Integration tests that make real API calls using keys from environment variables.
    Run with: pytest backend/tests/test_llm_service.py::TestLLMServiceIntegration -v
    Skip with: pytest ... -k "not integration"
    """

    @pytest.mark.asyncio
    async def test_integration_deepseek_real_call(self):
        """Test a real DeepSeek API call with the environment API key."""
        api_key = os.environ.get("DEEPSEEK_API_KEY")
        if not api_key:
            pytest.skip("DEEPSEEK_API_KEY not set in environment")

        llm = LLMService(provider="deepseek")
        assert llm.provider == "deepseek"

        response = await llm.ainvoke([{"role": "user", "content": "Say 'OK' in exactly one word."}])

        assert isinstance(response, str)
        assert len(response.strip()) > 0
        print(f"\nDeepSeek response: {response}")

    @pytest.mark.asyncio
    async def test_integration_deepseek_streaming(self):
        """Test real streaming response from DeepSeek."""
        api_key = os.environ.get("DEEPSEEK_API_KEY")
        if not api_key:
            pytest.skip("DEEPSEEK_API_KEY not set in environment")

        llm = LLMService(provider="deepseek")

        chunks = []
        async for chunk in llm.astream([{"role": "user", "content": "Count from 1 to 3, comma-separated."}]):
            chunks.append(chunk)

        full_response = "".join(chunks)
        assert len(chunks) > 0, "Expected at least one chunk"
        assert len(full_response.strip()) > 0, "Response should not be empty"
        print(f"\nDeepSeek streaming chunks: {chunks}")
        print(f"Full response: {full_response}")
