from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional


class ZhihuQuestionBase(BaseModel):
    title: str
    url: str


class ZhihuQuestionCreate(ZhihuQuestionBase):
    zhihu_id: str
    excerpt: Optional[str] = ""
    answer_count: int = 0
    follower_count: int = 0
    view_count: int = 0
    tags: list[str] = []
    label: str = "recommend"
    author_name: Optional[str] = ""
    author_url: Optional[str] = ""
    content_hash: Optional[str] = ""
    raw_metadata: Optional[dict] = {}


class ZhihuQuestionBatchCreate(BaseModel):
    questions: list[dict]


class ZhihuQuestionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    zhihu_id: str
    title: str
    excerpt: Optional[str] = ""
    answer_count: int = 0
    follower_count: int = 0
    view_count: int = 0
    tags: list[str] = []
    label: str = "recommend"
    author_name: Optional[str] = ""
    author_url: Optional[str] = ""
    url: str = ""
    content_hash: Optional[str] = ""
    raw_metadata: Optional[dict] = None
    fetched_at: datetime
    created_at: datetime
    updated_at: datetime


class ZhihuQuestionListResponse(BaseModel):
    items: list[ZhihuQuestionResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class ZhihuQuestionStatsResponse(BaseModel):
    total: int
    surging: int
    new: int
    recommend: int
    last_fetch_at: Optional[str] = None


class ZhihuQuestionSaveResponse(BaseModel):
    created: int
    updated: int
    skipped: int
    total: int
    message: str = ""


class ZhihuQuestionRefreshResponse(BaseModel):
    message: str
    last_fetch_at: Optional[str] = None
    hours_since_fetch: Optional[float] = None
