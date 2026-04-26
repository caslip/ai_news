from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from uuid import UUID
from enum import Enum


class SourceType(str, Enum):
    RSS = "rss"
    TWITTER = "twitter"
    GITHUB = "github"
    NETTER = "nitter"
    # 监控类型：type='keyword' 或 'account' 配合 monitor_type 字段
    KEYWORD = "keyword"
    ACCOUNT = "account"


class SourceBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    type: SourceType
    config: dict = Field(default_factory=dict, description="信源配置，如 feed_url, account, org/repo, keyword")


class SourceCreate(SourceBase):
    type: Optional[SourceType] = Field(None, description="信源类型，留空由后端自动设置")
    config: dict = Field(default_factory=dict, description="信源配置，如 feed_url, account, org/repo, keyword")
    value: Optional[str] = Field(None, description="监控值（关键词或账号名），会自动填入 config")
    params: Optional[dict] = Field(None, description="额外参数")
    user_id: Optional[str] = Field(None, description="关联的用户 ID")
    monitor_type: Optional[str] = Field(None, description="监控类型：'keyword' | 'account'")
    is_active: bool = Field(True, description="是否激活")


class SourceUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    is_active: Optional[bool] = None
    config: Optional[dict] = None
    user_id: Optional[str] = None
    monitor_type: Optional[str] = None


class SourceResponse(BaseModel):
    id: str
    name: str
    type: SourceType
    config: dict
    is_active: bool
    last_fetched_at: Optional[datetime] = None
    user_id: Optional[str] = None
    monitor_type: Optional[str] = None
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
