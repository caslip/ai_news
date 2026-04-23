"""
conftest.py - Pytest 配置和 fixtures
"""

import pytest
import sys
import os
from unittest.mock import MagicMock, AsyncMock

# 添加项目根目录到 path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool


@pytest.fixture(scope="session")
def test_db():
    """创建测试用 SQLite 数据库（内存模式）"""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    # 导入并创建表
    from app.database import Base
    from app.models import User, Source, Article, Bookmark, Tag, Strategy

    Base.metadata.create_all(bind=engine)

    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    yield TestingSessionLocal

    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session(test_db):
    """获取数据库会话 - 复用同一会话"""
    session = test_db()
    try:
        yield session
    finally:
        pass


@pytest.fixture
def client(db_session, test_db):
    """创建 FastAPI 测试客户端 - 使用同一会话"""
    from app.main import app
    from app.database import get_db

    # 创建一个工厂函数，返回同一个 session
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def test_user(db_session):
    """创建测试用户"""
    from app.models.user import User, UserRole
    from passlib.context import CryptContext

    # 检查是否已存在
    existing = db_session.query(User).filter(User.email == "test@example.com").first()
    if existing:
        return existing

    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    user = User(
        email="test@example.com",
        nickname="testuser",
        password_hash=pwd_context.hash("testpassword123"),
        role=UserRole.USER.value,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def auth_headers(client, test_user):
    """获取认证后的请求头"""
    response = client.post(
        "/api/auth/login",
        json={
            "email": "test@example.com",
            "password": "testpassword123"
        }
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def mock_openrouter(monkeypatch):
    """Mock OpenRouter API 调用"""
    async def mock_score_article(*args, **kwargs):
        return {
            "quality": 7.5,
            "hotness": 8.0,
            "spread_potential": 6.5,
            "reasoning": "Test analysis",
            "tags": ["AI", "LLM"]
        }
    
    async def mock_generate_summary(*args, **kwargs):
        return "这是一个测试摘要。"
    
    monkeypatch.setattr("app.services.openrouter.score_article", mock_score_article)
    monkeypatch.setattr("app.services.openrouter.generate_summary", mock_generate_summary)
    
    return {
        "score_article": mock_score_article,
        "generate_summary": mock_generate_summary
    }
