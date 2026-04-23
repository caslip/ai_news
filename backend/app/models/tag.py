from sqlalchemy import Column, String, DateTime, Integer, Index, Table, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class Tag(Base):
    __tablename__ = "tags"

    id = Column(String(36), primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True, index=True)
    slug = Column(String(100), nullable=False, unique=True, index=True)
    color = Column(String(7))
    usage_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    articles = relationship(
        "Article",
        secondary="article_tags",
        back_populates="tags"
    )

    __table_args__ = (
        Index("ix_tags_name_lower", "name"),
    )
