"""
Tests for the Generate endpoint using LangChain LLMService.

These tests cover:
- POST /api/writer/generate - Content generation
- Prompt building and message formatting
- Source URL fetching
- Error handling and draft status updates
- Integration with LangChain LLMService

All tests mock the LLM service to avoid external API calls.
"""

import pytest
import asyncio
from unittest.mock import patch, AsyncMock, MagicMock


def run_async(coro):
    """Run an async coroutine in a sync test context."""
    try:
        loop = asyncio.get_running_loop()
        # If we're already in an async context, we can't nest
        # Fall back to new event loop
        loop = asyncio.new_event_loop()
        return loop.run_until_complete(coro)
    except RuntimeError:
        # No running loop
        loop = asyncio.new_event_loop()
        return loop.run_until_complete(coro)
    finally:
        try:
            loop.close()
        except Exception:
            pass


class TestGenerateEndpointLangChain:
    """Tests for POST /api/writer/generate using LangChain LLMService."""

    def test_generate_requires_auth(self, client):
        """Test that generate endpoint requires authentication."""
        response = client.post(
            "/api/writer/generate",
            json={
                "source_content": "Test content",
                "style": "technical",
                "tone": "professional",
                "length": "medium"
            }
        )
        assert response.status_code == 401

    def test_generate_validation_error_no_source(self, client, auth_headers):
        """Test that generate requires either source_content or source_url."""
        response = client.post(
            "/api/writer/generate",
            json={
                "style": "technical",
                "tone": "professional",
                "length": "medium"
            },
            headers=auth_headers
        )
        assert response.status_code == 400
        assert "source" in response.json().get("detail", "").lower()

    def test_generate_with_source_content(self, client, auth_headers):
        """Test generating content with direct source content."""
        generated_content = """# Understanding LangChain

LangChain is a powerful framework for building LLM applications.

## Key Features

- Chain components
- Agent abstraction
- Memory management

## Getting Started

This guide will help you get started with LangChain.
"""

        with patch("app.writer.routers.generate.LLMService") as MockLLM:
            mock_llm_instance = AsyncMock()
            mock_llm_instance.ainvoke = AsyncMock(return_value=generated_content)
            MockLLM.return_value = mock_llm_instance

            with patch("app.writer.routers.generate.settings") as mock_settings:
                mock_settings.default_model = "deepseek/deepseek-chat-v3-5:free"

                response = client.post(
                    "/api/writer/generate",
                    json={
                        "source_content": "LangChain is a framework for building LLM applications with chains, agents, and memory.",
                        "style": "technical",
                        "tone": "professional",
                        "length": "medium"
                    },
                    headers=auth_headers
                )

                assert response.status_code == 200
                data = response.json()
                assert "id" in data
                assert data["status"] == "completed"
                assert data["content"] is not None
                assert "LangChain" in data["content"]
                assert data["word_count"] is not None
                assert data["word_count"] > 0

    def test_generate_creates_draft_in_db(self, client, auth_headers, db_session):
        """Test that generate creates a draft record in the database."""
        generated_content = "# Test Article\n\nThis is test content."

        with patch("app.writer.routers.generate.LLMService") as MockLLM:
            mock_llm_instance = AsyncMock()
            mock_llm_instance.ainvoke = AsyncMock(return_value=generated_content)
            MockLLM.return_value = mock_llm_instance

            with patch("app.writer.routers.generate.settings") as mock_settings:
                mock_settings.default_model = "deepseek/deepseek-chat-v3-5:free"

                response = client.post(
                    "/api/writer/generate",
                    json={
                        "source_content": "Test source content",
                        "style": "technical",
                        "tone": "professional",
                        "length": "medium"
                    },
                    headers=auth_headers
                )

                assert response.status_code == 200
                data = response.json()

                # Verify draft was created in DB
                from app.models.draft import Draft
                draft = db_session.query(Draft).filter(
                    Draft.id == data["id"]
                ).first()

                assert draft is not None
                assert draft.status == "completed"
                assert draft.content is not None
                assert draft.source_content is not None

    def test_generate_with_topic(self, client, auth_headers):
        """Test generate with a specific topic."""
        generated_content = "# AI in Healthcare\n\nAI is transforming healthcare."

        with patch("app.writer.routers.generate.LLMService") as MockLLM:
            mock_llm_instance = AsyncMock()
            mock_llm_instance.ainvoke = AsyncMock(return_value=generated_content)
            MockLLM.return_value = mock_llm_instance

            with patch("app.writer.routers.generate.settings") as mock_settings:
                mock_settings.default_model = "deepseek/deepseek-chat-v3-5:free"

                response = client.post(
                    "/api/writer/generate",
                    json={
                        "source_content": "Various AI applications in medical field.",
                        "topic": "AI in Healthcare",
                        "style": "news_analysis",
                        "tone": "professional",
                        "length": "medium"
                    },
                    headers=auth_headers
                )

                assert response.status_code == 200
                data = response.json()
                assert data["status"] == "completed"

    def test_generate_with_source_url(self, client, auth_headers):
        """Test generate with source URL (mocked fetch)."""
        generated_content = "# Fetched Content\n\nThis was fetched from a URL."

        with patch("app.writer.routers.generate.fetch_url_content") as mock_fetch:
            mock_fetch.return_value = "This is content fetched from the URL."

            with patch("app.writer.routers.generate.LLMService") as MockLLM:
                mock_llm_instance = AsyncMock()
                mock_llm_instance.ainvoke = AsyncMock(return_value=generated_content)
                MockLLM.return_value = mock_llm_instance

                with patch("app.writer.routers.generate.settings") as mock_settings:
                    mock_settings.default_model = "deepseek/deepseek-chat-v3-5:free"

                    response = client.post(
                        "/api/writer/generate",
                        json={
                            "source_url": "https://example.com/article",
                            "style": "technical",
                            "tone": "professional",
                            "length": "medium"
                        },
                        headers=auth_headers
                    )

                    assert response.status_code == 200
                    data = response.json()
                    assert data["status"] == "completed"
                    mock_fetch.assert_called_once_with("https://example.com/article")

    def test_generate_url_fetch_failure(self, client, auth_headers):
        """Test generate handles URL fetch failure gracefully by creating a failed draft."""
        from fastapi import HTTPException

        with patch("app.writer.routers.generate.fetch_url_content") as mock_fetch:
            mock_fetch.side_effect = HTTPException(
                status_code=400,
                detail="Failed to fetch URL"
            )

            with patch("app.writer.routers.generate.settings") as mock_settings:
                mock_settings.default_model = "deepseek/deepseek-chat-v3-5:free"

                response = client.post(
                    "/api/writer/generate",
                    json={
                        "source_url": "https://invalid-url-that-fails.com",
                        "style": "technical",
                        "tone": "professional",
                        "length": "medium"
                    },
                    headers=auth_headers
                )

                # The endpoint creates a failed draft and returns 200 with failed status
                # The HTTPException is caught and a draft with status="failed" is created
                assert response.status_code == 200
                data = response.json()
                assert data["status"] == "failed"
                assert data["error_message"] is not None

    def test_generate_llm_failure_returns_failed_status(self, client, auth_headers):
        """Test that LLM errors result in failed status."""
        with patch("app.writer.routers.generate.LLMService") as MockLLM:
            mock_llm_instance = AsyncMock()
            mock_llm_instance.ainvoke = AsyncMock(
                side_effect=Exception("LLM API Error: Connection timeout")
            )
            MockLLM.return_value = mock_llm_instance

            with patch("app.writer.routers.generate.settings") as mock_settings:
                mock_settings.default_model = "deepseek/deepseek-chat-v3-5:free"

                response = client.post(
                    "/api/writer/generate",
                    json={
                        "source_content": "Test content",
                        "style": "technical",
                        "tone": "professional",
                        "length": "medium"
                    },
                    headers=auth_headers
                )

                assert response.status_code == 200
                data = response.json()
                assert data["status"] == "failed"
                assert data["error_message"] is not None

    def test_generate_different_styles(self, client, auth_headers):
        """Test generate with different style options."""
        styles = ["technical", "news_analysis", "tutorial", "opinion", "product_review"]

        for style in styles:
            generated_content = f"# {style.title()} Article\n\nContent in {style} style."

            with patch("app.writer.routers.generate.LLMService") as MockLLM:
                mock_llm_instance = AsyncMock()
                mock_llm_instance.ainvoke = AsyncMock(return_value=generated_content)
                MockLLM.return_value = mock_llm_instance

                with patch("app.writer.routers.generate.settings") as mock_settings:
                    mock_settings.default_model = "deepseek/deepseek-chat-v3-5:free"

                    response = client.post(
                        "/api/writer/generate",
                        json={
                            "source_content": f"Test content for {style}",
                            "style": style,
                            "tone": "professional",
                            "length": "medium"
                        },
                        headers=auth_headers
                    )

                    assert response.status_code == 200
                    data = response.json()
                    assert data["status"] == "completed"

    def test_generate_different_tones(self, client, auth_headers):
        """Test generate with different tone options."""
        tones = ["professional", "casual", "concise", "storytelling"]

        for tone in tones:
            generated_content = f"# {tone.title()} Tone Article\n\nContent with {tone} tone."

            with patch("app.writer.routers.generate.LLMService") as MockLLM:
                mock_llm_instance = AsyncMock()
                mock_llm_instance.ainvoke = AsyncMock(return_value=generated_content)
                MockLLM.return_value = mock_llm_instance

                with patch("app.writer.routers.generate.settings") as mock_settings:
                    mock_settings.default_model = "deepseek/deepseek-chat-v3-5:free"

                    response = client.post(
                        "/api/writer/generate",
                        json={
                            "source_content": "Test content",
                            "style": "technical",
                            "tone": tone,
                            "length": "medium"
                        },
                        headers=auth_headers
                    )

                    assert response.status_code == 200
                    data = response.json()
                    assert data["status"] == "completed"

    def test_generate_different_lengths(self, client, auth_headers):
        """Test generate with different length options."""
        lengths = ["short", "medium", "long"]

        for length in lengths:
            generated_content = f"# {length.title()} Article\n\nContent for {length} length."

            with patch("app.writer.routers.generate.LLMService") as MockLLM:
                mock_llm_instance = AsyncMock()
                mock_llm_instance.ainvoke = AsyncMock(return_value=generated_content)
                MockLLM.return_value = mock_llm_instance

                with patch("app.writer.routers.generate.settings") as mock_settings:
                    mock_settings.default_model = "deepseek/deepseek-chat-v3-5:free"

                    response = client.post(
                        "/api/writer/generate",
                        json={
                            "source_content": "Test content",
                            "style": "technical",
                            "tone": "professional",
                            "length": length
                        },
                        headers=auth_headers
                    )

                    assert response.status_code == 200
                    data = response.json()
                    assert data["status"] == "completed"


class TestGenerateCoreFunction:
    """Tests for the generate_content_core function."""

    def test_core_generates_title_and_content(self):
        """Test that generate_content_core returns title, content, and word count."""
        generated_text = """# Understanding AI Agents

AI agents are autonomous systems that can perceive, decide, and act.

## Introduction

Artificial Intelligence agents represent a new paradigm...
"""

        with patch("app.writer.routers.generate.LLMService") as MockLLM:
            mock_llm_instance = AsyncMock()
            mock_llm_instance.ainvoke = AsyncMock(return_value=generated_text)
            MockLLM.return_value = mock_llm_instance

            with patch("app.writer.routers.generate.settings") as mock_settings:
                mock_settings.default_model = "deepseek/deepseek-chat-v3-5:free"

                from app.writer.routers.generate import generate_content_core

                title, content, word_count = run_async(
                    generate_content_core(
                        source_content="AI agents and their capabilities.",
                        style="technical",
                        tone="professional",
                        length="medium"
                    )
                )

                assert title == "Understanding AI Agents"
                assert "AI agents are" in content
                assert word_count > 0

    def test_core_extracts_title_from_first_line(self):
        """Test title extraction when # is not used."""
        generated_text = """My Article Title

This is the content of the article without a markdown header.
"""

        with patch("app.writer.routers.generate.LLMService") as MockLLM:
            mock_llm_instance = AsyncMock()
            mock_llm_instance.ainvoke = AsyncMock(return_value=generated_text)
            MockLLM.return_value = mock_llm_instance

            with patch("app.writer.routers.generate.settings") as mock_settings:
                mock_settings.default_model = "deepseek/deepseek-chat-v3-5:free"

                from app.writer.routers.generate import generate_content_core

                title, content, word_count = run_async(
                    generate_content_core(
                        source_content="Test source",
                        style="technical",
                        tone="professional",
                        length="medium"
                    )
                )

                assert title == "My Article Title"
                assert "content" in content.lower()


class TestGeneratePromptBuilding:
    """Tests for prompt building utilities."""

    def test_build_prompt_includes_length_info(self):
        """Test that prompt building includes length configuration."""
        from app.writer.routers.generate import build_generation_prompt

        prompt = build_generation_prompt(
            source_content="Test source",
            style="technical",
            tone="professional",
            length="long"
        )

        # Check length info is included (either "long" or "3000")
        assert "long" in prompt.lower() or "3000" in prompt
        # Check style description is included (Chinese for "technical")
        assert "技术细节" in prompt or "technical" in prompt.lower()

    def test_build_prompt_includes_topic(self):
        """Test that prompt building includes topic when provided."""
        from app.writer.routers.generate import build_generation_prompt

        prompt = build_generation_prompt(
            source_content="Test source",
            style="technical",
            tone="professional",
            length="medium",
            topic="AI in 2024"
        )

        assert "AI in 2024" in prompt

    def test_build_prompt_includes_source(self):
        """Test that prompt building includes source content."""
        from app.writer.routers.generate import build_generation_prompt

        prompt = build_generation_prompt(
            source_content="This is the source content to write about.",
            style="technical",
            tone="professional",
            length="medium"
        )

        assert "This is the source content" in prompt


class TestGenerateIntegration:
    """Integration tests for the generate workflow."""

    def test_full_generate_workflow(self, client, auth_headers, db_session):
        """Test complete generate workflow: request -> draft creation -> completion."""
        generated_content = "# Complete Workflow Test\n\nThis tests the full generation workflow."

        with patch("app.writer.routers.generate.LLMService") as MockLLM:
            mock_llm_instance = AsyncMock()
            mock_llm_instance.ainvoke = AsyncMock(return_value=generated_content)
            MockLLM.return_value = mock_llm_instance

            with patch("app.writer.routers.generate.settings") as mock_settings:
                mock_settings.default_model = "deepseek/deepseek-chat-v3-5:free"

                # Make generate request
                response = client.post(
                    "/api/writer/generate",
                    json={
                        "source_content": "Source material for the article.",
                        "style": "technical",
                        "tone": "professional",
                        "length": "medium",
                        "topic": "Workflow Test"
                    },
                    headers=auth_headers
                )

                # Verify response
                assert response.status_code == 200
                data = response.json()
                draft_id = data["id"]

                # Verify draft in database
                from app.models.draft import Draft
                db_session.expire_all()
                draft = db_session.query(Draft).filter(Draft.id == draft_id).first()

                assert draft is not None
                assert draft.status == "completed"
                assert draft.title == "Complete Workflow Test"
                assert draft.style == "technical"
                assert draft.tone == "professional"
                assert draft.length == "medium"

    def test_generate_with_all_style_combinations(self, client, auth_headers):
        """Test generate with all valid style/tone/length combinations."""
        styles = ["technical", "news_analysis", "tutorial", "opinion", "product_review"]
        tones = ["professional", "casual", "concise", "storytelling"]
        lengths = ["short", "medium", "long"]

        generated_content = "# Combination Test\n\nTesting all combinations."

        for style in styles:
            for tone in tones:
                for length in lengths:
                    with patch("app.writer.routers.generate.LLMService") as MockLLM:
                        mock_llm_instance = AsyncMock()
                        mock_llm_instance.ainvoke = AsyncMock(return_value=generated_content)
                        MockLLM.return_value = mock_llm_instance

                        with patch("app.writer.routers.generate.settings") as mock_settings:
                            mock_settings.default_model = "deepseek/deepseek-chat-v3-5:free"

                            response = client.post(
                                "/api/writer/generate",
                                json={
                                    "source_content": "Test source",
                                    "style": style,
                                    "tone": tone,
                                    "length": length
                                },
                                headers=auth_headers
                            )

                            assert response.status_code == 200, f"Failed for {style}/{tone}/{length}"
                            assert response.json()["status"] == "completed"
