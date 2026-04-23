"""
后台管理 Schema
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class AdminStatsResponse(BaseModel):
    """管理员统计响应"""
    total_users: int = 0
    total_articles: int = 0
    total_sources: int = 0
    active_sources: int = 0
    articles_today: int = 0
    articles_this_week: int = 0
    articles_this_month: int = 0
    low_fan_viral_count: int = 0
    bookmarks_count: int = 0
    active_strategies: int = 0
    queue_pending_tasks: int = 0
    queue_running_tasks: int = 0
    last_crawl_at: Optional[datetime] = None
    system_uptime: str = ""


class UserManagementResponse(BaseModel):
    """用户管理响应"""
    id: str
    email: str
    nickname: str
    role: str
    is_active: bool
    created_at: datetime
    last_login_at: Optional[datetime] = None
    articles_count: int = 0
    bookmarks_count: int = 0
    
    class Config:
        from_attributes = True


class UserRoleUpdate(BaseModel):
    """用户角色更新"""
    role: str = Field(..., description="用户角色: user, admin")
    is_active: Optional[bool] = None


class SourceHealthResponse(BaseModel):
    """信源健康状态"""
    id: str
    name: str
    type: str
    url: str
    is_active: bool
    last_fetched_at: Optional[datetime] = None
    last_error: Optional[str] = None
    success_count: int = 0
    error_count: int = 0
    success_rate: float = 0.0
    avg_response_time_ms: int = 0
    articles_count: int = 0


class QueueStatusResponse(BaseModel):
    """队列状态"""
    worker_status: List[Dict[str, Any]] = []
    pending_tasks: int = 0
    running_tasks: int = 0
    scheduled_tasks: int = 0
    failed_tasks_recent: int = 0
    tasks_by_type: Dict[str, int] = {}
    memory_usage_mb: Optional[int] = None
    cpu_usage_percent: Optional[float] = None


class SystemHealthResponse(BaseModel):
    """系统健康状态"""
    status: str  # healthy, degraded, unhealthy
    components: Dict[str, Dict[str, Any]] = {}
    timestamp: datetime
    version: str
    uptime_seconds: int
