from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional


class BookmarkBase(BaseModel):
    article_id: str
    notes: Optional[str] = None


class BookmarkCreate(BookmarkBase):
    pass


class BookmarkResponse(BookmarkBase):
    id: str
    user_id: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class BookmarkWithArticle(BookmarkResponse):
    article_title: str
    article_url: str
    article_image_url: Optional[str] = None
    source_name: str
