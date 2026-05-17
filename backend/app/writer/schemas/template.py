"""
Writer Template Schemas - Pydantic models for Template API
"""
from pydantic import BaseModel, ConfigDict
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

    model_config = ConfigDict(from_attributes=True)


class TemplateListResponse(BaseModel):
    """Response model for template list"""
    items: list[TemplateResponse]
    total: int
