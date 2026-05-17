"""
Writer Draft Schemas - Pydantic models for Draft API
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Any
from datetime import datetime


class DraftResponse(BaseModel):
    """Response model for a single draft"""
    id: str
    title: str
    content: str
    status: str = Field(pattern="^(generating|completed|failed)$")
    word_count: int
    style: str
    tone: str
    length: str
    source_url: Optional[str] = None
    source_content: Optional[str] = None
    messages: Optional[list[dict[str, Any]]] = None  # Chat history
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DraftListResponse(BaseModel):
    """Paginated list response for drafts"""
    items: list[DraftResponse]
    total: int
    page: int
    page_size: int


class BatchDeleteRequest(BaseModel):
    """Request model for batch delete"""
    draft_ids: list[str]


class BatchDeleteResponse(BaseModel):
    """Response model for batch delete"""
    deleted_count: int


class GenerateRequest(BaseModel):
    """Request model for content generation"""
    source_url: Optional[str] = None
    source_content: Optional[str] = None
    topic: Optional[str] = None
    style: str = Field(
        default="technical",
        pattern="^(technical|news_analysis|tutorial|opinion|product_review)$"
    )
    tone: str = Field(
        default="professional",
        pattern="^(professional|casual|concise|storytelling)$"
    )
    length: str = Field(
        default="medium",
        pattern="^(short|medium|long)$"
    )


class GenerateResponse(BaseModel):
    """Response model for content generation"""
    id: str
    status: str = Field(pattern="^(generating|completed|failed)$")
    content: Optional[str] = None
    title: Optional[str] = None
    word_count: Optional[int] = None
    error_message: Optional[str] = None


class WriterStats(BaseModel):
    """Writer statistics response"""
    today_count: int
    total_drafts: int
    total_words: int
    avg_duration_seconds: float
