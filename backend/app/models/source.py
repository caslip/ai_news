import uuid
import enum
from sqlalchemy import Column, String, Boolean, DateTime, Enum as SQLEnum, JSON, Index, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class SourceType(str, enum.Enum):
    RSS = "rss"
    TWITTER = "twitter"
    GITHUB = "github"
    NETTER = "nitter"
    # 监控类型：通过 type='keyword' 表示关键词监控，type='account' 表示账号监控
    # 配合 monitor_type 字段区分：'keyword' | 'account' | null（null = 普通信源）


class Source(Base):
    __tablename__ = "sources"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    type = Column(String(20), nullable=False)
    config = Column(JSON, nullable=False, default=dict)
    is_active = Column(Boolean, default=True, nullable=False)
    last_fetched_at = Column(DateTime, nullable=True)
    # 用户关联：普通信源 created_by 为 admin/系统用户，监控配置关联到具体 user_id
    user_id = Column(String(36), nullable=True)
    # 监控类型：'keyword'（关键词监控）、'account'（账号监控）、null（普通信源）
    monitor_type = Column(String(20), nullable=True)
    created_by = Column(String(36), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    articles = relationship("Article", back_populates="source", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_sources_type", "type"),
        Index("ix_sources_user", "user_id"),
        Index("ix_sources_monitor_type", "monitor_type"),
    )

    def __repr__(self):
        return f"<Source(id={self.id}, name={self.name}, type={self.type}, monitor_type={self.monitor_type})>"
