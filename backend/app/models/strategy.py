import uuid
from sqlalchemy import Column, String, Text, DateTime, Integer, Boolean, JSON, ForeignKey, Index
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class Strategy(Base):
    __tablename__ = "strategies"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    version = Column(Integer, nullable=False, default=1)
    params = Column(JSON, nullable=False, default=dict)
    is_active = Column(Boolean, default=False, nullable=False)
    created_by = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="strategies")

    __table_args__ = (
        Index("ix_strategies_name_version", "name", "version"),
    )

    def __repr__(self):
        return f"<Strategy(id={self.id}, name={self.name}, version={self.version})>"


class MonitorConfig(Base):
    """
    [已废弃] 关键词和账号监控配置已迁移到 sources 表。
    请使用 Source 模型（monitor_type='keyword' 或 'account'）代替。
    此模型保留用于向后兼容，将在后续版本中删除。
    """
    __tablename__ = "monitor_configs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    config_type = Column(String(50), nullable=False, default="keyword")
    name = Column(String(255), nullable=False)
    value = Column(String(500), nullable=False)
    params = Column(JSON, default=dict, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    user = relationship("User")

    __table_args__ = (
        Index("ix_monitor_configs_user", "user_id"),
        Index("ix_monitor_configs_type", "config_type"),
    )

    def __repr__(self):
        return f"<MonitorConfig(id={self.id}, config_type={self.config_type}, name={self.name})>"
