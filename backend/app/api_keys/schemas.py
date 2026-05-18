"""
API Key Schemas - Pydantic models for API key operations
"""
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional


class ApiKeyCreate(BaseModel):
    """Schema for creating or updating an API key"""
    provider: str = Field(..., description="Provider identifier (e.g., 'deepseek', 'openai')")
    api_key: str = Field(..., description="The actual API key to store")
    label: Optional[str] = Field(None, max_length=100, description="Optional label for the API key")


class ApiKeyUpdate(BaseModel):
    """Schema for updating an API key"""
    api_key: Optional[str] = Field(None, description="New API key value (if changing)")
    label: Optional[str] = Field(None, max_length=100, description="New label")
    is_active: Optional[bool] = Field(None, description="Active status")


class ApiKeyResponse(BaseModel):
    """Schema for API key response (with masked key)"""
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    user_id: str
    provider: str
    label: Optional[str] = None
    masked_key: str = Field(..., description="Masked API key showing first 4 and last 4 characters")
    is_active: bool
    created_at: datetime
    updated_at: datetime


class ProviderInfo(BaseModel):
    """Schema for provider information"""
    id: str
    name: str
    base_url: str
    models: list[str]
    supports_function_calling: bool
    supports_vision: bool
    website: str
    description: str


class ApiKeyListResponse(BaseModel):
    """Schema for listing API keys"""
    items: list[ApiKeyResponse]
    total: int


class ApiKeyTestRequest(BaseModel):
    """Schema for testing an API key"""
    provider: str
    api_key: str


class ApiKeyTestResponse(BaseModel):
    """Schema for API key test response"""
    success: bool
    message: str
    model: Optional[str] = None
