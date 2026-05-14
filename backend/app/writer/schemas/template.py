"""
Writer Template Schemas - Pydantic models for Template API
"""
from pydantic import BaseModel
from datetime import datetime


class TemplateResponse(BaseModel):
    """Response model for a template"""
    id: str
    name: str
    description: str | None
    category: str
    style: str
    tone: str
    length: str
    use_count: int
    created_at: datetime

    class Config:
        from_attributes = True


class TemplateListResponse(BaseModel):
    """Response model for template list"""
    items: list[TemplateResponse]
    total: int
