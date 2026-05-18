"""
API Key Model - Stores encrypted API keys for various LLM providers
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, Index
from app.database import Base


class ApiKey(Base):
    __tablename__ = "api_keys"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), nullable=False, index=True)
    provider = Column(String(50), nullable=False)
    encrypted_key = Column(String(500), nullable=False)
    label = Column(String(100), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    __table_args__ = (
        Index("ix_api_keys_user_provider", "user_id", "provider", unique=True),
    )

    def __repr__(self):
        return f"<ApiKey(id={self.id}, user_id={self.user_id}, provider={self.provider})>"
