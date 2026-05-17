"""
审计事件数据模型

定义统一的审计事件结构，用于记录用户操作和系统变更
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Any, Optional, Literal
from datetime import datetime
from uuid import uuid4


_AUDIT_EXAMPLE = {
    "event_id": "evt_abc123",
    "timestamp": "2026-05-14T08:32:11.342Z",
    "user_id": "u_123",
    "username": "charlie@example.com",
    "role": "admin",
    "session_id": "sess_xyz",
    "ip": "203.0.113.42",
    "user_agent": "Mozilla/5.0...",
    "geo": {"country": "CN", "city": "Shanghai"},
    "action": "document.delete",
    "method": "DELETE",
    "path": "/api/v1/documents/456",
    "resource_type": "document",
    "resource_id": "doc_456",
    "before": {"status": "active"},
    "after": {"status": None},
    "status": "success",
    "http_status": 200,
    "error_code": None,
    "error_message": None,
    "duration_ms": 42,
    "service": "document-service",
    "env": "production",
    "trace_id": "trace_abc",
    "tenant_id": "tenant_001",
    "request_id": "req_789"
}


class AuditEvent(BaseModel):
    """
    审计事件模型

    用于记录所有需要审计的操作，包括：
    - 用户登录/登出
    - 数据创建、更新、删除
    - 敏感操作（如批量删除、权限变更）
    - 访问控制决策
    """

    event_id: str = Field(
        default_factory=lambda: str(uuid4()),
        description="事件唯一ID"
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.utcnow(),
        description="事件发生时间"
    )
    user_id: Optional[str] = Field(None, description="用户ID")
    username: Optional[str] = Field(None, description="用户名")
    role: Optional[str] = Field(None, description="用户角色")
    session_id: Optional[str] = Field(None, description="会话ID")
    ip: Optional[str] = Field(None, description="客户端IP")
    user_agent: Optional[str] = Field(None, description="User Agent")
    geo: Optional[dict[str, Any]] = Field(None, description="地理位置信息")
    action: str = Field(..., description="操作类型，格式: resource.verb (如: document.delete)")
    method: Optional[str] = Field(None, description="HTTP方法")
    path: Optional[str] = Field(None, description="请求路径")
    resource_type: Optional[str] = Field(None, description="资源类型")
    resource_id: Optional[str] = Field(None, description="资源ID")
    before: Optional[dict[str, Any]] = Field(None, description="操作前的状态快照")
    after: Optional[dict[str, Any]] = Field(None, description="操作后的状态快照")
    status: Literal["success", "failed", "denied"] = Field(
        default="success",
        description="操作状态"
    )
    http_status: Optional[int] = Field(None, description="HTTP状态码")
    error_code: Optional[str] = Field(None, description="错误代码")
    error_message: Optional[str] = Field(None, description="错误消息")
    duration_ms: Optional[float] = Field(None, description="操作耗时(毫秒)")
    service: str = Field(default="ai-news-backend", description="服务名称")
    env: str = Field(default="production", description="环境")
    trace_id: Optional[str] = Field(None, description="分布式追踪ID")
    tenant_id: Optional[str] = Field(None, description="租户ID")
    request_id: Optional[str] = Field(None, description="请求ID")

    model_config = ConfigDict(json_schema_extra={"example": _AUDIT_EXAMPLE})


class AuditEventCreate(BaseModel):
    """创建审计事件的输入模型"""
    action: str
    resource_type: Optional[str] = None
    resource_id: Optional[str] = None
    method: Optional[str] = None
    path: Optional[str] = None
    before: Optional[dict[str, Any]] = None
    after: Optional[dict[str, Any]] = None
    status: Literal["success", "failed", "denied"] = "success"
    http_status: Optional[int] = None
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    duration_ms: Optional[float] = None


class ClientLogEvent(BaseModel):
    """
    前端客户端日志事件模型

    用于接收来自前端的错误日志和用户行为日志
    """
    event_id: str = Field(
        default_factory=lambda: str(uuid4()),
        description="事件唯一ID"
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.utcnow(),
        description="事件发生时间"
    )
    user_id: Optional[str] = Field(None, description="用户ID")
    username: Optional[str] = Field(None, description="用户名")
    session_id: str = Field(..., description="会话ID")
    user_agent: str = Field(..., description="User Agent")
    ip: Optional[str] = Field(None, description="IP (由服务端添加)")
    action: str = Field(..., description="操作类型")
    resource_type: Optional[str] = Field(None, description="资源类型")
    resource_id: Optional[str] = Field(None, description="资源ID")
    status: Literal["success", "failed", "denied"] = Field(
        default="success",
        description="操作状态"
    )
    error_code: Optional[str] = Field(None, description="错误代码")
    error_message: Optional[str] = Field(None, description="错误消息")
    stack_trace: Optional[str] = Field(None, description="堆栈跟踪")
    duration_ms: Optional[float] = Field(None, description="操作耗时")
    service: str = Field(default="ai-news-frontend", description="服务名称")
    env: str = Field(default="production", description="环境")
    trace_id: Optional[str] = Field(None, description="分布式追踪ID")
    request_id: Optional[str] = Field(None, description="请求ID")
    page_url: Optional[str] = Field(None, description="页面URL")
    page_name: Optional[str] = Field(None, description="页面名称")
