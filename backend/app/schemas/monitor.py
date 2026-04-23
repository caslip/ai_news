"""
Monitor 配置 Schema
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime


class MonitorConfigCreate(BaseModel):
    """创建监控配置"""
    name: str = Field(..., description="名称")
    value: str = Field(..., description="值（关键词或账号名）")
    is_active: bool = Field(default=True, description="是否启用")
    params: Optional[Dict[str, Any]] = Field(default=None, description="额外参数")


class MonitorConfigUpdate(BaseModel):
    """更新监控配置"""
    name: Optional[str] = None
    value: Optional[str] = None
    is_active: Optional[bool] = None
    params: Optional[Dict[str, Any]] = None


class MonitorConfigResponse(BaseModel):
    """监控配置响应"""
    id: str
    config_type: str
    name: str
    value: str
    is_active: bool
    params: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
