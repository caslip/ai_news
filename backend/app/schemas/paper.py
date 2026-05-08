from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class PaperBase(BaseModel):
    arxiv_id: Optional[str] = None
    hf_paper_id: Optional[str] = None
    title: str
    url: str
    summary: Optional[str] = None
    author: Optional[str] = None
    upvotes: int = 0
    thumbnail_url: Optional[str] = None
    github_repo: Optional[str] = None
    project_page: Optional[str] = None
    hf_url: Optional[str] = None
    primary_category: Optional[str] = None
    categories: list[str] = []
    tags: list[str] = []
    published_at: Optional[datetime] = None


class PaperCreate(PaperBase):
    source_id: Optional[str] = None
    content_hash: str


class PaperResponse(PaperBase):
    id: str
    source_id: Optional[str] = None
    content_hash: str
    fetched_at: datetime
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class PaperListResponse(BaseModel):
    items: list[PaperResponse]
    total: int
    page: int
    page_size: int
