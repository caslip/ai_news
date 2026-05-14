"""
审计日志服务

提供统一的审计事件记录功能
"""

import logging
from typing import Any, Optional
from datetime import datetime
from uuid import uuid4

from app.logging_config import get_audit_logger, get_request_context
from app.logging.schemas.audit import AuditEvent, AuditEventCreate


class AuditLogger:
    """
    审计日志记录器

    提供便捷的方法来记录各种类型的审计事件
    """

    def __init__(self, name: str = "audit"):
        self.logger = get_audit_logger(name)
        self._context = get_request_context()

    def log(
        self,
        action: str,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        method: Optional[str] = None,
        path: Optional[str] = None,
        before: Optional[dict[str, Any]] = None,
        after: Optional[dict[str, Any]] = None,
        status: str = "success",
        http_status: Optional[int] = None,
        error_code: Optional[str] = None,
        error_message: Optional[str] = None,
        duration_ms: Optional[float] = None,
        **extra_fields,
    ):
        """
        记录审计事件

        Args:
            action: 操作类型 (如: document.create, user.login)
            resource_type: 资源类型 (如: document, user, draft)
            resource_id: 资源ID
            method: HTTP方法 (GET, POST, PUT, DELETE等)
            path: 请求路径
            before: 操作前的状态快照
            after: 操作后的状态快照
            status: 操作状态 (success, failed, denied)
            http_status: HTTP状态码
            error_code: 错误代码
            error_message: 错误消息
            duration_ms: 操作耗时(毫秒)
            **extra_fields: 额外的自定义字段
        """
        context = get_request_context()

        event = AuditEvent(
            event_id=str(uuid4()),
            timestamp=datetime.utcnow(),
            user_id=context.get("user_id") or None,
            username=context.get("username") or None,
            role=context.get("role") or None,
            session_id=context.get("session_id") or None,
            ip=context.get("ip") or None,
            user_agent=context.get("user_agent") or None,
            action=action,
            method=method,
            path=path,
            resource_type=resource_type,
            resource_id=resource_id,
            before=before,
            after=after,
            status=status,
            http_status=http_status,
            error_code=error_code,
            error_message=error_message,
            duration_ms=duration_ms,
            trace_id=context.get("trace_id") or None,
            tenant_id=context.get("tenant_id") or None,
            request_id=context.get("request_id") or None,
        )

        # 记录事件
        self.logger.info(
            f"Audit: {action}",
            extra={
                **event.model_dump(mode="json"),
                **extra_fields,
            }
        )

    def log_create(
        self,
        resource_type: str,
        resource_id: str,
        after: dict[str, Any],
        path: Optional[str] = None,
        method: str = "POST",
        duration_ms: Optional[float] = None,
    ):
        """记录创建操作"""
        self.log(
            action=f"{resource_type}.create",
            resource_type=resource_type,
            resource_id=resource_id,
            method=method,
            path=path,
            before=None,
            after=after,
            status="success",
            http_status=201 if path else None,
            duration_ms=duration_ms,
        )

    def log_read(
        self,
        resource_type: str,
        resource_id: str,
        path: Optional[str] = None,
        method: str = "GET",
    ):
        """记录读取操作"""
        self.log(
            action=f"{resource_type}.read",
            resource_type=resource_type,
            resource_id=resource_id,
            method=method,
            path=path,
            status="success",
            http_status=200,
        )

    def log_update(
        self,
        resource_type: str,
        resource_id: str,
        before: dict[str, Any],
        after: dict[str, Any],
        path: Optional[str] = None,
        method: str = "PUT",
        duration_ms: Optional[float] = None,
    ):
        """记录更新操作"""
        self.log(
            action=f"{resource_type}.update",
            resource_type=resource_type,
            resource_id=resource_id,
            method=method,
            path=path,
            before=before,
            after=after,
            status="success",
            http_status=200,
            duration_ms=duration_ms,
        )

    def log_delete(
        self,
        resource_type: str,
        resource_id: str,
        before: dict[str, Any],
        path: Optional[str] = None,
        method: str = "DELETE",
        duration_ms: Optional[float] = None,
    ):
        """记录删除操作"""
        self.log(
            action=f"{resource_type}.delete",
            resource_type=resource_type,
            resource_id=resource_id,
            method=method,
            path=path,
            before=before,
            after=None,
            status="success",
            http_status=204,
            duration_ms=duration_ms,
        )

    def log_batch_delete(
        self,
        resource_type: str,
        resource_ids: list[str],
        count: int,
        path: Optional[str] = None,
        duration_ms: Optional[float] = None,
    ):
        """记录批量删除操作"""
        self.log(
            action=f"{resource_type}.batch_delete",
            resource_type=resource_type,
            resource_id=f"batch:{count}",
            method="POST",
            path=path,
            before={"ids": resource_ids, "count": count},
            after={"deleted_count": count},
            status="success",
            http_status=200,
            duration_ms=duration_ms,
        )

    def log_login(
        self,
        username: str,
        success: bool = True,
        error_message: Optional[str] = None,
        duration_ms: Optional[float] = None,
    ):
        """记录登录操作"""
        self.log(
            action="auth.login",
            resource_type="session",
            username=username,
            status="success" if success else "failed",
            error_message=error_message,
            duration_ms=duration_ms,
        )

    def log_logout(
        self,
        user_id: Optional[str] = None,
        username: Optional[str] = None,
        duration_ms: Optional[float] = None,
    ):
        """记录登出操作"""
        self.log(
            action="auth.logout",
            resource_type="session",
            user_id=user_id,
            username=username,
            status="success",
            duration_ms=duration_ms,
        )

    def log_access_denied(
        self,
        resource_type: str,
        resource_id: Optional[str] = None,
        path: Optional[str] = None,
        reason: Optional[str] = None,
    ):
        """记录访问被拒绝"""
        self.log(
            action=f"{resource_type}.access_denied",
            resource_type=resource_type,
            resource_id=resource_id,
            path=path,
            status="denied",
            error_message=reason,
        )

    def log_error(
        self,
        action: str,
        error_message: str,
        error_code: Optional[str] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        duration_ms: Optional[float] = None,
    ):
        """记录错误"""
        self.log(
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            status="failed",
            error_code=error_code,
            error_message=error_message,
            duration_ms=duration_ms,
        )


# 全局审计日志记录器实例
_audit_logger: Optional[AuditLogger] = None


def get_audit_logger_instance() -> AuditLogger:
    """获取全局审计日志记录器实例"""
    global _audit_logger
    if _audit_logger is None:
        _audit_logger = AuditLogger()
    return _audit_logger


def audit_log(
    action: str,
    resource_type: Optional[str] = None,
    resource_id: Optional[str] = None,
    **kwargs,
):
    """便捷函数：记录审计事件"""
    return get_audit_logger_instance().log(
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        **kwargs,
    )
