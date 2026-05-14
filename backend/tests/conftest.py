"""
Pytest fixtures for writer module tests

This module provides:
- Test client fixture for FastAPI app
- Database session management with test isolation
- Authentication fixtures (test user, auth headers)
- Data fixtures (drafts, templates, etc.)
- Mock utilities for external services
"""

import pytest
import uuid
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
from typing import Generator
import asyncio

from httpx import AsyncClient, ASGITransport, Response
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.models.user import User
from app.models.draft import Draft
from app.models.writer import WriterTemplate, GeneratedContent


# Create in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)


# Enable foreign keys for SQLite
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session() -> Generator[Session, None, None]:
    """Create a fresh database session for each test"""
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    db = TestingSessionLocal()
    
    yield db
    
    db.close()
    # Clean up tables
    for table in reversed(Base.metadata.sorted_tables):
        db.execute(table.delete())
    db.commit()


class SyncClient:
    """Synchronous wrapper for httpx AsyncClient with ASGITransport"""
    
    def __init__(self, app, db_session: Session):
        self.app = app
        self.db_session = db_session
        self._transport = ASGITransport(app=app)
        self._client = None
    
    def _get_client(self):
        """Get or create the httpx client"""
        if self._client is None:
            self._client = AsyncClient(transport=self._transport, base_url="http://test")
        return self._client
    
    def _make_sync(self, coro):
        """Convert async coroutine to sync"""
        loop = asyncio.new_event_loop()
        try:
            return loop.run_until_complete(coro)
        finally:
            loop.close()
    
    def request(self, method: str, url: str, **kwargs) -> Response:
        """Make a synchronous request"""
        # Override database dependency
        def override_get_db():
            try:
                yield self.db_session
            finally:
                pass
        
        self.app.dependency_overrides[get_db] = override_get_db
        
        client = self._get_client()
        coro = client.request(method, url, **kwargs)
        return self._make_sync(coro)
    
    def get(self, url: str, **kwargs) -> Response:
        return self.request("GET", url, **kwargs)
    
    def post(self, url: str, **kwargs) -> Response:
        return self.request("POST", url, **kwargs)
    
    def put(self, url: str, **kwargs) -> Response:
        return self.request("PUT", url, **kwargs)
    
    def delete(self, url: str, **kwargs) -> Response:
        return self.request("DELETE", url, **kwargs)
    
    def patch(self, url: str, **kwargs) -> Response:
        return self.request("PATCH", url, **kwargs)
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._client:
            self._make_sync(self._client.aclose())
        self.app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def client(db_session: Session):
    """Create a test client with dependency overrides"""
    with SyncClient(app, db_session) as test_client:
        yield test_client


@pytest.fixture(scope="function")
def test_user(db_session: Session) -> User:
    """Create a test user"""
    user = User(
        id="test-user-id-123",
        email="test@example.com",
        nickname="Test User",
        password_hash="$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4.S0QIk8pV8QKIzu",
    )
    db_session.add(user)
    db_session.commit()
    return user


@pytest.fixture(scope="function")
def auth_headers(db_session: Session, test_user: User) -> dict:
    """Get authentication headers for test user"""
    from app.services.auth import AuthService
    
    auth_service = AuthService(db_session)
    token = auth_service.create_access_token(
        data={"sub": test_user.id, "email": test_user.email, "role": "user"}
    )
    
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def test_draft(db_session: Session, test_user: User) -> Draft:
    """Create a test draft"""
    draft = Draft(
        id="draft-123",
        title="Test Draft",
        content="# Test Draft Content\n\nThis is a test draft.",
        status="completed",
        word_count=10,
        style="technical",
        tone="professional",
        length="medium",
        created_by=test_user.id,
    )
    db_session.add(draft)
    db_session.commit()
    return draft


@pytest.fixture
def test_drafts(db_session: Session, test_user: User) -> list:
    """Create multiple test drafts"""
    drafts = []
    for i in range(5):
        draft = Draft(
            id=f"draft-{i+1}",
            title=f"Test Draft {i+1}",
            content=f"# Draft {i+1}\n\nContent for draft {i+1}.",
            status="completed" if i % 2 == 0 else "generating",
            word_count=10 + i,
            style="technical",
            tone="professional",
            length="medium",
            created_by=test_user.id,
        )
        db_session.add(draft)
        drafts.append(draft)
    db_session.commit()
    return drafts


@pytest.fixture
def test_template(db_session: Session) -> WriterTemplate:
    """Create a test template"""
    template = WriterTemplate(
        id="template-123",
        name="Test Template",
        description="A test template for testing",
        category="tech",
        style="technical",
        tone="professional",
        length="medium",
        use_count=5,
    )
    db_session.add(template)
    db_session.commit()
    return template


@pytest.fixture
def test_templates(db_session: Session) -> list:
    """Create multiple test templates"""
    templates = []
    categories = ["tech", "general", "product", "social"]
    for i, cat in enumerate(categories):
        template = WriterTemplate(
            id=f"template-{i+1}",
            name=f"{cat.title()} Template",
            description=f"A {cat} template",
            category=cat,
            style="technical",
            tone="professional",
            length="medium",
            use_count=i,
        )
        db_session.add(template)
        templates.append(template)
    db_session.commit()
    return templates


@pytest.fixture
def test_content(db_session: Session, test_user: User) -> GeneratedContent:
    """Create a test generated content"""
    content = GeneratedContent(
        id="content-123",
        source_article_ids=["article-1"],
        source_article_titles=["Test Article"],
        content="# Test Content\n\nThis is test content.",
        platform="article",
        prompt="Test prompt",
        status="draft",
        created_by=test_user.id,
    )
    db_session.add(content)
    db_session.commit()
    return content


@pytest.fixture
def test_contents(db_session: Session, test_user: User) -> list:
    """Create multiple test generated contents"""
    contents = []
    for i in range(3):
        content = GeneratedContent(
            id=f"content-{i+1}",
            source_article_ids=[f"article-{i}"],
            source_article_titles=[f"Title {i}"],
            content=f"# Content {i}\n\nContent number {i}.",
            platform="article",
            status="draft",
            created_by=test_user.id,
        )
        db_session.add(content)
        contents.append(content)
    db_session.commit()
    return contents
