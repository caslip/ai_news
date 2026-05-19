import uuid
from sqlalchemy import Column, String, Text, DateTime, Integer, JSON, Index
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class ZhihuQuestion(Base):
    __tablename__ = "zhihu_questions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    zhihu_id = Column(String(64), nullable=False, unique=True)  # 索引在 __table_args__ 中定义

    title = Column(String(1000), nullable=False)
    excerpt = Column(Text, nullable=True)
    answer_count = Column(Integer, default=0, nullable=False)
    follower_count = Column(Integer, default=0, nullable=False)
    view_count = Column(Integer, default=0, nullable=False)

    tags = Column(JSON, default=[], nullable=False)
    label = Column(String(32), nullable=False, default="recommend")  # surging | new | recommend

    author_name = Column(String(255), nullable=True)
    author_url = Column(Text, nullable=True)
    url = Column(Text, nullable=False)

    content_hash = Column(String(64), nullable=True)

    raw_metadata = Column(JSON, nullable=True)

    fetched_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    __table_args__ = (
        Index("ix_zhihu_questions_zhihu_id", "zhihu_id"),
        Index("ix_zhihu_questions_label", "label"),
        Index("ix_zhihu_questions_fetched_at", "fetched_at"),
    )

    def __repr__(self):
        return f"<ZhihuQuestion(id={self.id}, zhihu_id={self.zhihu_id}, title={self.title[:50]})>"
