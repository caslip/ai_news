from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from uuid import UUID


class ArticleBase(BaseModel):
    title: str
    url: str


class ArticleCreate(ArticleBase):
    source_id: Optional[str] = None
    summary: Optional[str] = None
    author: Optional[str] = None
    tags: list[str] = []
    published_at: Optional[datetime] = None


class ArticleUpdate(BaseModel):
    title: Optional[str] = None
    summary: Optional[str] = None
    tags: Optional[list[str]] = None
    hot_score: Optional[float] = None
    is_low_fan_viral: Optional[bool] = None


class ArticleResponse(BaseModel):
    id: str
    source_id: Optional[str] = None
    source_name: Optional[str] = None
    source_type: Optional[str] = None
    title: str
    url: str
    summary: Optional[str] = None
    content_hash: Optional[str] = None
    author: Optional[str] = None
    hot_score: float = 0
    fan_count: int = 0
    engagement: dict = {}
    is_low_fan_viral: bool = False
    tags: list[str] = []
    raw_metadata: Optional[dict] = None
    fetched_at: datetime
    published_at: Optional[datetime] = None
    created_at: datetime
    is_bookmarked: bool = False

    class Config:
        from_attributes = True


class ArticleListResponse(BaseModel):
    items: list[ArticleResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class ArticleStatsResponse(BaseModel):
    today_count: int
    week_count: int
    month_count: int
    total_count: int


class ArticleFilter(BaseModel):
    source: Optional[str] = None
    source_type: Optional[str] = None
    time_range: Optional[str] = "today"
    sort: Optional[str] = "hot"
    q: Optional[str] = None
    page: int = 1
    page_size: int = 20
    is_low_fan_viral: Optional[bool] = None
