"""
AI News Aggregator - Test Suite
运行命令: pytest tests/ -v
"""

# Backend Tests
BACKEND_TESTS = """
test_auth.py       - 用户认证测试（注册/登录/JWT）
test_articles.py   - 文章 API 测试
test_sources.py    - 信源管理测试
test_crawler.py    - 爬虫服务测试
test_ai_service.py - AI 评分服务测试（Mock）
"""

# Frontend Tests
FRONTEND_TESTS = """
test_api_client.ts - API 客户端测试
test_auth_store.ts - 认证状态管理测试
"""

# Integration Tests
INTEGRATION_TESTS = """
test_e2e.py        - 端到端测试
test_api_flow.py   - API 流程测试
"""

print("=" * 60)
print("AI News Aggregator - Test Suite")
print("=" * 60)
print()
print("Backend Tests (Python/pytest):")
print("  cd backend && pip install -r requirements.txt")
print("  pytest tests/ -v")
print()
print("Frontend Tests (Vitest/Jest):")
print("  cd frontend && npm install")
print("  npm test")
print()
print("=" * 60)
