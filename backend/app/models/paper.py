import uuid
from sqlalchemy import Column, String, Text, DateTime, Integer, JSON, ForeignKey, Index
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class Paper(Base):
    __tablename__ = "papers"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    source_id = Column(String(36), ForeignKey("sources.id", ondelete="SET NULL"), nullable=True)

    # 论文标识（二选一，取决于来源）
    arxiv_id = Column(String(50), nullable=True)
    hf_paper_id = Column(String(50), nullable=True)

    title = Column(String(1000), nullable=False)
    url = Column(Text, nullable=False)
    summary = Column(Text, nullable=True)
    content_hash = Column(String(64), nullable=False)

    author = Column(String(500), nullable=True)
    upvotes = Column(Integer, default=0, nullable=False)

    # 论文专属元数据
    thumbnail_url = Column(Text, nullable=True)
    github_repo = Column(Text, nullable=True)
    project_page = Column(Text, nullable=True)
    hf_url = Column(Text, nullable=True)

    # 分类与标签
    primary_category = Column(String(50), nullable=True)
    categories = Column(JSON, default=[], nullable=False)
    tags = Column(JSON, default=[], nullable=False)

    fetched_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    published_at = Column(DateTime, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    source = relationship("Source", back_populates="papers")

    __table_args__ = (
        Index("ix_papers_content_hash", "content_hash"),
        Index("ix_papers_arxiv_id", "arxiv_id"),
        Index("ix_papers_hf_id", "hf_paper_id"),
        Index("ix_papers_published", "published_at"),
    )

    def __repr__(self):
        return f"<Paper(id={self.id}, arxiv_id={self.arxiv_id}, title={self.title[:50]})>"
