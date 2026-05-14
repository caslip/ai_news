"""
日志管理路由

提供前端日志接收端点和日志查询功能
"""

import logging
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.logging.schemas.audit import ClientLogEvent, AuditEventCreate
from app.logging.audit_logger import get_audit_logger_instance
from app.middleware import get_user_id, get_username
from app.news.routers.auth import get_current_user
from app.news.schemas.user import UserResponse

router = APIRouter(prefix="/logging", tags=["日志管理"])

logger = logging.getLogger(__name__)


class BatchLogRequest(BaseModel):
    events: list[ClientLogEvent]


class BatchLogResponse(BaseModel):
    received: int
    logged: int


class LogQueryRequest(BaseModel):
    action: Optional[str] = None
    resource_type: Optional[str] = None
    status: Optional[str] = None
    limit: int = 100


class LogQueryResponse(BaseModel):
    events: list[dict]
    total: int


@router.post("/client-event", status_code=201)
async def log_client_event(
    event: ClientLogEvent,
    current_user: Optional[UserResponse] = Depends(get_current_user),
):
    """
    接收前端客户端事件日志

    前端通过此端点将错误日志和用户行为日志发送到后端
    """
    audit_logger = get_audit_logger_instance()

    # 如果用户已登录，覆盖客户端提供的用户信息
    if current_user:
        event.user_id = str(current_user.id)
        event.username = current_user.email or current_user.username

    # 记录事件
    audit_logger.log(
        action=f"client.{event.action}",
        resource_type=event.resource_type,
        resource_id=event.resource_id,
        status=event.status,
        error_code=event.error_code,
        error_message=event.error_message,
        duration_ms=event.duration_ms,
        # 额外的客户端信息
        **{"client_user_agent": event.user_agent},
    )

    return {"status": "logged", "event_id": event.event_id}


@router.post("/client-event/batch", status_code=201)
async def log_client_events_batch(
    request: BatchLogRequest,
    current_user: Optional[UserResponse] = Depends(get_current_user),
):
    """
    批量接收前端客户端事件日志

    适用于批量发送日志以减少网络请求
    """
    audit_logger = get_audit_logger_instance()
    logged = 0

    for event in request.events:
        try:
            # 如果用户已登录，覆盖客户端提供的用户信息
            if current_user:
                event.user_id = str(current_user.id)
                event.username = current_user.email or current_user.username

            audit_logger.log(
                action=f"client.{event.action}",
                resource_type=event.resource_type,
                resource_id=event.resource_id,
                status=event.status,
                error_code=event.error_code,
                error_message=event.error_message,
                duration_ms=event.duration_ms,
            )
            logged += 1
        except Exception as e:
            logger.warning(f"Failed to log client event: {e}")

    return BatchLogResponse(received=len(request.events), logged=logged)


@router.post("/audit", status_code=201)
async def log_audit_event(
    event: AuditEventCreate,
    current_user: UserResponse = Depends(get_current_user),
):
    """
    手动记录审计事件

    用于在后端代码中记录业务审计事件
    """
    audit_logger = get_audit_logger_instance()

    audit_logger.log(
        action=event.action,
        resource_type=event.resource_type,
        resource_id=event.resource_id,
        method=event.method,
        path=event.path,
        before=event.before,
        after=event.after,
        status=event.status,
        http_status=event.http_status,
        error_code=event.error_code,
        error_message=event.error_message,
        duration_ms=event.duration_ms,
    )

    return {"status": "logged"}


@router.get("/health")
async def logging_health_check():
    """
    日志系统健康检查

    返回日志系统的健康状态
    """
    from app.logging_config import (
        AUDIT_LOG_FILE,
        APP_LOG_FILE,
        CELERY_LOG_FILE,
        LOG_DIR,
    )
    from pathlib import Path

    logs = {
        "audit_log_exists": AUDIT_LOG_FILE.exists(),
        "app_log_exists": APP_LOG_FILE.exists(),
        "celery_log_exists": CELERY_LOG_FILE.exists(),
        "log_dir_exists": LOG_DIR.exists(),
    }

    all_exist = all(logs.values())

    return {
        "status": "healthy" if all_exist else "degraded",
        "logs": logs,
        "log_dir": str(LOG_DIR),
    }


@router.get("/stats")
async def get_logging_stats(
    current_user: UserResponse = Depends(get_current_user),
):
    """
    获取日志统计信息

    返回日志相关的统计数据
    """
    # This would typically query Loki or the log files
    # For now, return basic info
    return {
        "status": "ok",
        "message": "Log stats endpoint - connect to Loki for detailed stats",
    }
