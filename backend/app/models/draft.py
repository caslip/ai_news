"""
Writer Draft Model - AI 写作草稿
"""
import uuid
import re
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Integer, JSON
from app.database import Base
from datetime import datetime


def extract_title_from_content(content: str) -> str:
    """Extract title from content - looks for # Title or first line"""
    if not content:
        return "Untitled"
    
    # Try to find # Title format first
    match = re.search(r'^#\s+(.+)$', content.strip(), re.MULTILINE)
    if match:
        return match.group(1).strip()
    
    # Try first non-empty line that doesn't start with special chars
    lines = content.strip().split('\n')
    for line in lines:
        line = line.strip()
        if line and not line.startswith(('#', '*', '-', '>', '|', '=')):
            # Clean up the title
            title = re.sub(r'^[#*\-\s]+', '', line)
            if title and len(title) <= 100:
                return title[:100]
    
    return "Untitled"


class Draft(Base):
    __tablename__ = "writer_drafts"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(500), nullable=False, default="Untitled")
    content = Column(Text, nullable=False, default="")
    
    # Generation status
    status = Column(String(20), default="generating")  # generating, completed, failed
    
    # Metadata
    word_count = Column(Integer, default=0)
    style = Column(String(50), default="technical")  # technical, news_analysis, tutorial, opinion, product_review
    tone = Column(String(50), default="professional")  # professional, casual, concise, storytelling
    length = Column(String(20), default="medium")  # short, medium, long
    
    # Source info
    source_url = Column(Text, nullable=True)
    source_content = Column(Text, nullable=True)
    
    # Chat history for multi-turn conversations
    messages = Column(JSON, nullable=True)  # Store chat history as JSON
    
    # Error tracking
    error_message = Column(Text, nullable=True)
    
    # User reference
    created_by = Column(String(36), ForeignKey("users.id"), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def calculate_word_count(self) -> int:
        """Calculate word count from content"""
        if not self.content:
            return 0
        return len(self.content.split())

    def extract_title(self) -> str:
        """Extract and set title from content"""
        self.title = extract_title_from_content(self.content)
        return self.title
