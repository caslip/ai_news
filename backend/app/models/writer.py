import uuid
from sqlalchemy import Column, String, Text, DateTime, JSON, ForeignKey
from app.database import Base
from datetime import datetime


class GeneratedContent(Base):
    __tablename__ = "generated_content"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    source_article_ids = Column(JSON, default=list)
    source_article_titles = Column(JSON, default=list)
    prompt = Column(Text, nullable=True)
    content = Column(Text, nullable=False)
    platform = Column(String(20), default="article")
    status = Column(String(20), default="draft")
    created_by = Column(String(36), ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
