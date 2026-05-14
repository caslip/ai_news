import uuid
from sqlalchemy import Column, String, Text, DateTime, JSON, ForeignKey, Integer
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


class WriterTemplate(Base):
    """
    Writing templates for different content styles
    Used to provide pre-configured writing parameters
    """
    __tablename__ = "writer_templates"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(50), nullable=False, default="general")  # general, tech, news, social
    
    # Writing parameters
    style = Column(String(50), nullable=False, default="technical")
    tone = Column(String(50), nullable=False, default="professional")
    length = Column(String(20), nullable=False, default="medium")
    
    # Usage tracking
    use_count = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)

