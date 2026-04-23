from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from uuid import UUID
from enum import Enum


class SourceType(str, Enum):
    RSS = "rss"
    TWITTER = "twitter"
    GITHUB = "github"
    NETTER = "netter"


class SourceBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    type: SourceType
    config: dict = Field(..., description="信源配置，如 feed_url, account, org/repo")


class SourceCreate(SourceBase):
    pass


class SourceUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    is_active: Optional[bool] = None
    config: Optional[dict] = None


class SourceResponse(BaseModel):
    id: str
    name: str
    type: SourceType
    config: dict
    is_active: bool
    last_fetched_at: Optional[datetime] = None
    created_by: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class SourceTestResponse(BaseModel):
    success: bool
    message: str
    article_count: int = 0


class SourceListResponse(BaseModel):
    items: list[SourceResponse]
    total: int
    page: int
    page_size: int


class SourceBatchDeleteRequest(BaseModel):
    source_ids: list[str] = Field(..., min_length=1, description="要删除的信源 ID 列表")
