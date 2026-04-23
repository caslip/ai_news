import uuid
import enum
from sqlalchemy import Column, String, Boolean, DateTime, Enum as SQLEnum, JSON, Index
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class SourceType(str, enum.Enum):
    RSS = "rss"
    TWITTER = "twitter"
    GITHUB = "github"
    NETTER = "netter"


class Source(Base):
    __tablename__ = "sources"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    type = Column(String(20), nullable=False)
    config = Column(JSON, nullable=False, default=dict)
    is_active = Column(Boolean, default=True, nullable=False)
    last_fetched_at = Column(DateTime, nullable=True)
    created_by = Column(String(36), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    articles = relationship("Article", back_populates="source", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_sources_type", "type"),
    )

    def __repr__(self):
        return f"<Source(id={self.id}, name={self.name}, type={self.type})>"
