from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class ContentCreate(BaseModel):
    source_article_ids: list[str]
    source_article_titles: list[str]
    content: str
    platform: str = "article"
    prompt: Optional[str] = None


class ContentUpdate(BaseModel):
    content: Optional[str] = None
    status: Optional[str] = None
    prompt: Optional[str] = None


class ContentResponse(BaseModel):
    id: str
    source_article_ids: list[str]
    source_article_titles: list[str]
    content: str
    platform: str
    prompt: Optional[str]
    status: str
    created_by: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class ContentListResponse(BaseModel):
    items: list[ContentResponse]
    total: int
    page: int
    page_size: int
