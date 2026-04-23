"""
test_ai_service.py - AI 服务测试（Mock 测试）
"""

import pytest
from unittest.mock import patch, MagicMock


class TestAIServiceMocked:
    """AI 服务 Mock 测试"""
    
    def test_score_article_success(self, mock_openrouter):
        """测试成功评分"""
        import asyncio
        
        async def run_test():
            from app.services.openrouter import score_article
            
            result = await score_article(
                title="Test Article",
                content="This is a test article about AI.",
                metadata={"source": "test", "author": "tester"}
            )
            
            assert result["quality"] == 7.5
            assert result["hotness"] == 8.0
            assert result["spread_potential"] == 6.5
            assert "AI" in result["tags"]
            assert "LLM" in result["tags"]
        
        asyncio.run(run_test())
    
    def test_generate_summary_success(self, mock_openrouter):
        """测试成功生成摘要"""
        import asyncio
        
        async def run_test():
            from app.services.openrouter import generate_summary
            
            result = await generate_summary(
                content="This is a long article content..." * 10,
                max_length=500
            )
            
            assert len(result) <= 500
            assert isinstance(result, str)
        
        asyncio.run(run_test())


class TestAIServiceWithoutApiKey:
    """无 API Key 测试"""
    
    def test_score_article_no_api_key(self, monkeypatch):
        """测试无 API Key 时抛出异常"""
        import asyncio
        
        # Mock 配置，不设置 API key
        monkeypatch.setattr("app.config.settings.openrouter_api_key", "")
        
        async def run_test():
            from app.services.openrouter import score_article, AIServiceError
            
            with pytest.raises(AIServiceError) as exc_info:
                await score_article(
                    title="Test",
                    content="Test",
                    metadata={}
                )
            
            assert "API key not configured" in str(exc_info.value)
        
        asyncio.run(run_test())


class TestAIServiceErrorHandling:
    """AI 服务错误处理测试"""
    
    def test_score_article_network_error(self, monkeypatch):
        """测试网络错误处理"""
        import asyncio
        
        async def mock_post(*args, **kwargs):
            raise Exception("Network error")
        
        monkeypatch.setattr("httpx.AsyncClient.post", mock_post)
        
        async def run_test():
            from app.services.openrouter import score_article, AIServiceError
            
            # 重新导入以获取 mock
            from app.config import settings
            monkeypatch.setattr("app.config.settings.openrouter_api_key", "fake_key")
            
            with pytest.raises(AIServiceError):
                await score_article(
                    title="Test",
                    content="Test",
                    metadata={}
                )
        
        asyncio.run(run_test())
