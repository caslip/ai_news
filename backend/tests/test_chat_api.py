"""
Tests for the Chat API endpoints (floating window).

These tests cover:
- POST /api/writer/chat - Non-streaming chat
- POST /api/writer/chat/stream - Streaming chat
- GET /api/writer/chat/history/{session_id} - Chat history
- GET /api/writer/chat/sessions - List sessions
- POST /api/writer/chat/sessions - Create session
- DELETE /api/writer/chat/sessions/{session_id} - Delete session

All tests mock the LLM service to avoid external API calls.
"""

import pytest
from unittest.mock import patch, AsyncMock, MagicMock


class TestChatEndpoint:
    """Tests for POST /api/writer/chat - non-streaming chat."""

    def test_chat_requires_auth(self, client):
        """Test that chat endpoint requires authentication."""
        response = client.post(
            "/api/writer/chat",
            json={"message": "Hello"}
        )
        assert response.status_code == 401

    def test_chat_missing_message(self, client, auth_headers):
        """Test that chat requires a message field."""
        response = client.post(
            "/api/writer/chat",
            json={},
            headers=auth_headers
        )
        # Should return 422 (validation error) for missing required field
        assert response.status_code == 422

    def test_chat_basic_message(self, client, auth_headers):
        """Test a basic chat message returns response."""
        mock_response = "Hello! I'm your AI writing assistant. How can I help you today?"

        with patch("app.writer.routers.chat.LLMService") as MockLLM:
            mock_llm_instance = AsyncMock()
            mock_llm_instance.ainvoke = AsyncMock(return_value=mock_response)
            MockLLM.return_value = mock_llm_instance

            with patch("app.writer.routers.chat.settings") as mock_settings:
                mock_settings.default_model = "google/gemini-2.0-flash-thinking-exp:free"
                mock_settings.effective_llm_provider = "deepseek"

                response = client.post(
                    "/api/writer/chat",
                    json={"message": "Hello"},
                    headers=auth_headers
                )

                assert response.status_code == 200
                data = response.json()
                assert "session_id" in data
                assert "message" in data
                assert data["message"] == mock_response
                assert data.get("error") is None

    def test_chat_with_model_override(self, client, auth_headers):
        """Test chat with a specific model override."""
        mock_response = "Here is my response."

        with patch("app.writer.routers.chat.LLMService") as MockLLM:
            mock_llm_instance = AsyncMock()
            mock_llm_instance.ainvoke = AsyncMock(return_value=mock_response)
            MockLLM.return_value = mock_llm_instance

            with patch("app.writer.routers.chat.settings") as mock_settings:
                mock_settings.default_model = "google/gemini-2.0-flash-thinking-exp:free"
                mock_settings.effective_llm_provider = "deepseek"

                response = client.post(
                    "/api/writer/chat",
                    json={
                        "message": "Hello",
                        "model": "anthropic/claude-3.5-sonnet"
                    },
                    headers=auth_headers
                )

                assert response.status_code == 200
                data = response.json()
                assert data["message"] == mock_response

    def test_chat_maintains_conversation_history(self, client, auth_headers):
        """Test that chat maintains conversation history across messages."""
        mock_response = "This is my second response."

        with patch("app.writer.routers.chat.LLMService") as MockLLM:
            mock_llm_instance = AsyncMock()
            mock_llm_instance.ainvoke = AsyncMock(return_value=mock_response)
            MockLLM.return_value = mock_llm_instance

            with patch("app.writer.routers.chat.settings") as mock_settings:
                mock_settings.default_model = "google/gemini-2.0-flash-thinking-exp:free"
                mock_settings.effective_llm_provider = "deepseek"

                # First message
                response1 = client.post(
                    "/api/writer/chat",
                    json={"message": "First message"},
                    headers=auth_headers
                )
                assert response1.status_code == 200
                session_id = response1.json()["session_id"]

                # Second message with same session
                response2 = client.post(
                    "/api/writer/chat",
                    json={
                        "message": "Second message",
                        "session_id": session_id
                    },
                    headers=auth_headers
                )
                assert response2.status_code == 200
                assert response2.json()["session_id"] == session_id

    def test_chat_llm_error_returns_error_in_response(self, client, auth_headers):
        """Test that LLM errors are caught and returned in response."""
        with patch("app.writer.routers.chat.LLMService") as MockLLM:
            mock_llm_instance = AsyncMock()
            mock_llm_instance.ainvoke = AsyncMock(
                side_effect=Exception("API Error: Rate limited")
            )
            MockLLM.return_value = mock_llm_instance

            with patch("app.writer.routers.chat.settings") as mock_settings:
                mock_settings.default_model = "google/gemini-2.0-flash-thinking-exp:free"
                mock_settings.effective_llm_provider = "deepseek"

                response = client.post(
                    "/api/writer/chat",
                    json={"message": "Hello"},
                    headers=auth_headers
                )

                # Should return 200 with error field rather than 500
                assert response.status_code == 200
                data = response.json()
                assert "session_id" in data
                assert data["message"] == ""
                assert data.get("error") is not None
                assert "API Error" in data["error"]

    def test_chat_creates_new_session_if_not_exists(self, client, auth_headers):
        """Test that new session is created if session_id not provided."""
        mock_response = "Response"

        with patch("app.writer.routers.chat.LLMService") as MockLLM:
            mock_llm_instance = AsyncMock()
            mock_llm_instance.ainvoke = AsyncMock(return_value=mock_response)
            MockLLM.return_value = mock_llm_instance

            with patch("app.writer.routers.chat.settings") as mock_settings:
                mock_settings.default_model = "google/gemini-2.0-flash-thinking-exp:free"
                mock_settings.effective_llm_provider = "deepseek"

                response = client.post(
                    "/api/writer/chat",
                    json={"message": "Hello"},
                    headers=auth_headers
                )

                assert response.status_code == 200
                data = response.json()
                # Session ID should be generated
                assert data["session_id"] is not None
                assert len(data["session_id"]) > 0


class TestChatHistoryEndpoint:
    """Tests for GET /api/writer/chat/history/{session_id}."""

    def test_history_requires_auth(self, client):
        """Test that history endpoint requires authentication."""
        response = client.get("/api/writer/chat/history/test-session-123")
        assert response.status_code == 401

    def test_history_returns_empty_for_new_session(self, client, auth_headers):
        """Test that history returns empty messages for new session."""
        response = client.get(
            "/api/writer/chat/history/nonexistent-session",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "messages" in data
        assert data["messages"] == []

    def test_history_after_chat(self, client, auth_headers):
        """Test that history returns messages after chat conversation."""
        mock_response = "AI response"

        with patch("app.writer.routers.chat.LLMService") as MockLLM:
            mock_llm_instance = AsyncMock()
            mock_llm_instance.ainvoke = AsyncMock(return_value=mock_response)
            MockLLM.return_value = mock_llm_instance

            with patch("app.writer.routers.chat.settings") as mock_settings:
                mock_settings.default_model = "google/gemini-2.0-flash-thinking-exp:free"
                mock_settings.effective_llm_provider = "deepseek"

                # Start a chat
                chat_response = client.post(
                    "/api/writer/chat",
                    json={"message": "Hello"},
                    headers=auth_headers
                )
                session_id = chat_response.json()["session_id"]

                # Get history
                history_response = client.get(
                    f"/api/writer/chat/history/{session_id}",
                    headers=auth_headers
                )

                assert history_response.status_code == 200
                history = history_response.json()
                assert "messages" in history
                # Should have user and assistant messages (no system)
                assert len(history["messages"]) == 2
                assert history["messages"][0]["role"] == "user"
                assert history["messages"][1]["role"] == "assistant"


class TestChatSessionsEndpoint:
    """Tests for session management endpoints."""

    def test_list_sessions_requires_auth(self, client):
        """Test that list sessions requires authentication."""
        response = client.get("/api/writer/chat/sessions")
        assert response.status_code == 401

    def test_list_sessions_empty(self, client, auth_headers):
        """Test listing sessions when none exist."""
        response = client.get("/api/writer/chat/sessions", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "sessions" in data
        assert isinstance(data["sessions"], list)

    def test_create_session(self, client, auth_headers):
        """Test creating a new chat session."""
        response = client.post(
            "/api/writer/chat/sessions",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "session_id" in data
        # Session ID should be prefixed with user ID
        assert "_" in data["session_id"]

    def test_delete_session(self, client, auth_headers):
        """Test deleting a chat session."""
        # First create a session
        create_response = client.post(
            "/api/writer/chat/sessions",
            headers=auth_headers
        )
        session_id = create_response.json()["session_id"]

        # Delete it
        delete_response = client.delete(
            f"/api/writer/chat/sessions/{session_id}",
            headers=auth_headers
        )
        assert delete_response.status_code == 200
        assert delete_response.json()["status"] == "ok"


class TestChatModelsEndpoint:
    """Tests for available models endpoint."""

    def test_list_models(self, client):
        """Test listing available models (should not require auth)."""
        with patch("app.writer.routers.chat.settings") as mock_settings:
            mock_settings.available_models = [
                "google/gemini-2.0-flash-thinking-exp:free",
                "anthropic/claude-3.5-sonnet",
                "openai/gpt-4o"
            ]
            mock_settings.effective_llm_provider = "deepseek"

            # Note: The current chat.py doesn't have a /models endpoint
            # This test documents expected behavior for future implementation
            pass


class TestChatStreamingEndpoint:
    """Tests for POST /api/writer/chat/stream - streaming chat."""

    def test_stream_requires_auth(self, client):
        """Test that streaming chat requires authentication."""
        response = client.post(
            "/api/writer/chat/stream",
            json={"message": "Hello"}
        )
        assert response.status_code == 401

    def test_stream_missing_message(self, client, auth_headers):
        """Test that streaming chat requires message field."""
        response = client.post(
            "/api/writer/chat/stream",
            json={},
            headers=auth_headers
        )
        assert response.status_code == 422

    def test_stream_basic(self, client, auth_headers):
        """Test basic streaming chat."""
        mock_chunks = ["Hello", " there", "!"]

        with patch("app.writer.routers.chat.LLMService") as MockLLM:
            mock_llm_instance = AsyncMock()

            async def mock_stream(*args, **kwargs):
                for chunk in mock_chunks:
                    yield chunk

            mock_llm_instance.astream = mock_stream
            MockLLM.return_value = mock_llm_instance

            with patch("app.writer.routers.chat.settings") as mock_settings:
                mock_settings.default_model = "google/gemini-2.0-flash-thinking-exp:free"
                mock_settings.effective_llm_provider = "deepseek"

                response = client.post(
                    "/api/writer/chat/stream",
                    json={"message": "Hello"},
                    headers=auth_headers
                )

                # SSE endpoint returns 200 with event stream
                assert response.status_code == 200
                assert "text/event-stream" in response.headers.get("content-type", "")


class TestChatIntegration:
    """Integration tests for chat workflows."""

    def test_full_chat_workflow(self, client, auth_headers):
        """Test complete chat workflow: create session, chat, get history."""
        mock_response = "AI response text"

        with patch("app.writer.routers.chat.LLMService") as MockLLM:
            mock_llm_instance = AsyncMock()
            mock_llm_instance.ainvoke = AsyncMock(return_value=mock_response)
            MockLLM.return_value = mock_llm_instance

            with patch("app.writer.routers.chat.settings") as mock_settings:
                mock_settings.default_model = "google/gemini-2.0-flash-thinking-exp:free"
                mock_settings.effective_llm_provider = "deepseek"

                # 1. Create a new session
                session_response = client.post(
                    "/api/writer/chat/sessions",
                    headers=auth_headers
                )
                assert session_response.status_code == 200
                session_id = session_response.json()["session_id"]

                # 2. Send a message in that session
                chat_response = client.post(
                    "/api/writer/chat",
                    json={
                        "message": "Help me write an article",
                        "session_id": session_id
                    },
                    headers=auth_headers
                )
                assert chat_response.status_code == 200
                assert chat_response.json()["session_id"] == session_id

                # 3. Get history
                history_response = client.get(
                    f"/api/writer/chat/history/{session_id}",
                    headers=auth_headers
                )
                assert history_response.status_code == 200
                assert len(history_response.json()["messages"]) == 2

    def test_multiple_sessions_isolated(self, client, auth_headers):
        """Test that multiple sessions maintain separate histories."""
        mock_response = "Response"

        with patch("app.writer.routers.chat.LLMService") as MockLLM:
            mock_llm_instance = AsyncMock()
            mock_llm_instance.ainvoke = AsyncMock(return_value=mock_response)
            MockLLM.return_value = mock_llm_instance

            with patch("app.writer.routers.chat.settings") as mock_settings:
                mock_settings.default_model = "google/gemini-2.0-flash-thinking-exp:free"
                mock_settings.effective_llm_provider = "deepseek"

                # Create two separate sessions
                session1_response = client.post(
                    "/api/writer/chat/sessions",
                    headers=auth_headers
                )
                session1_id = session1_response.json()["session_id"]

                session2_response = client.post(
                    "/api/writer/chat/sessions",
                    headers=auth_headers
                )
                session2_id = session2_response.json()["session_id"]

                # Chat in session 1
                client.post(
                    "/api/writer/chat",
                    json={"message": "Session 1 message", "session_id": session1_id},
                    headers=auth_headers
                )

                # Chat in session 2
                client.post(
                    "/api/writer/chat",
                    json={"message": "Session 2 message", "session_id": session2_id},
                    headers=auth_headers
                )

                # History should be isolated
                history1 = client.get(
                    f"/api/writer/chat/history/{session1_id}",
                    headers=auth_headers
                ).json()
                history2 = client.get(
                    f"/api/writer/chat/history/{session2_id}",
                    headers=auth_headers
                ).json()

                assert history1["messages"][0]["content"] == "Session 1 message"
                assert history2["messages"][0]["content"] == "Session 2 message"
