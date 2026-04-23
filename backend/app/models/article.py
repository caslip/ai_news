import uuid
from sqlalchemy import Column, String, Text, DateTime, Float, Boolean, Integer, JSON, ForeignKey, Index
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class Article(Base):
    __tablename__ = "articles"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    source_id = Column(String(36), ForeignKey("sources.id", ondelete="SET NULL"), nullable=True)
    
    title = Column(String(1000), nullable=False)
    url = Column(Text, nullable=False)
    summary = Column(Text, nullable=True)
    content_hash = Column(String(64), nullable=False, unique=True)
    
    author = Column(String(255), nullable=True)
    
    hot_score = Column(Float, default=0, nullable=False)
    fan_count = Column(Integer, default=0, nullable=False)
    engagement = Column(JSON, default={"likes": 0, "retweets": 0, "comments": 0}, nullable=False)
    is_low_fan_viral = Column(Boolean, default=False, nullable=False)
    
    tags = Column(JSON, default=[], nullable=False)
    raw_metadata = Column(JSON, nullable=True)
    
    fetched_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    published_at = Column(DateTime, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    source = relationship("Source", back_populates="articles")
    bookmarks = relationship("Bookmark", back_populates="article", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_articles_content_hash", "content_hash"),
    )

    def __repr__(self):
        return f"<Article(id={self.id}, title={self.title[:50]})>"
