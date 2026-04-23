import uuid
import enum
from sqlalchemy import Column, String, Boolean, DateTime, Enum as SQLEnum, Text, JSON, Index
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class UserRole(str, enum.Enum):
    USER = "user"
    ADMIN = "admin"


class OAuthProvider(str, enum.Enum):
    GITHUB = "github"
    GOOGLE = "google"


class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=True)
    nickname = Column(String(100), nullable=False)
    avatar_url = Column(String(500), nullable=True)
    role = Column(String(20), default=UserRole.USER.value, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    push_config = Column(JSON, nullable=True, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_login_at = Column(DateTime, nullable=True)
    oauth_provider = Column(String(20), nullable=True)
    oauth_id = Column(String(255), nullable=True)

    bookmarks = relationship("Bookmark", back_populates="user", cascade="all, delete-orphan")
    tags = relationship("Tag", back_populates="user", cascade="all, delete-orphan")
    strategies = relationship("Strategy", back_populates="user", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_users_oauth", "oauth_provider", "oauth_id"),
        Index("ix_users_created_at", "created_at"),
    )

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, nickname={self.nickname})>"
