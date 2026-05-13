from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from uuid import UUID


class StrategyBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    params: dict = Field(default_factory=dict)


class StrategyCreate(StrategyBase):
    pass


class StrategyUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    params: Optional[dict] = None


class StrategyResponse(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    version: int
    params: dict
    is_active: bool
    created_by: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class StrategyListResponse(BaseModel):
    items: list[StrategyResponse]
    total: int
    page: int
    page_size: int
