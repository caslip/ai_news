"""
审计日志装饰器和上下文管理器

提供便捷的装饰器来自动记录 API 端点的审计事件
"""

import functools
import time
import logging
from typing import Any, Callable, Optional, TypeVar, Union

from app.logging.audit_logger import get_audit_logger_instance
from app.logging_config import get_request_context

logger = logging.getLogger(__name__)

F = TypeVar("F", bound=Callable[..., Any])


def audit(
    action: str,
    resource_type: Optional[str] = None,
    capture_before: bool = False,
    capture_after: bool = True,
    capture_response: bool = False,
    get_resource_id: Optional[Callable[..., str]] = None,
):
    """
    审计日志装饰器

    自动为异步函数添加审计日志记录功能

    Args:
        action: 操作类型 (如: "draft.delete", "user.login")
        resource_type: 资源类型 (如: "draft", "user")
        capture_before: 是否捕获操作前的状态
        capture_after: 是否捕获操作后的状态
        capture_response: 是否将响应作为 after 状态
        get_resource_id: 从函数参数提取资源ID的函数

    Usage:
        @audit(action="draft.delete", resource_type="draft")
        async def delete_draft(draft_id: str):
            ...

        @audit(action="draft.create", resource_type="draft", capture_response=True)
        async def create_draft(data: DraftCreate):
            return await db.create(data)
    """
    def decorator(func: F) -> F:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            audit_logger = get_audit_logger_instance()
            start_time = time.time()

            # 提取资源ID
            resource_id = None
            if get_resource_id:
                try:
                    resource_id = get_resource_id(*args, **kwargs)
                except Exception:
                    pass

            # 尝试从 kwargs 提取
            if not resource_id:
                resource_id = kwargs.get("id") or kwargs.get("draft_id") or kwargs.get("resource_id")

            # 捕获 before 状态
            before_state = None
            if capture_before and resource_id:
                try:
                    # 调用 before_capture 钩子 (如果存在)
                    before_hook = kwargs.get("_before_capture")
                    if before_hook and callable(before_hook):
                        before_state = before_hook(resource_id)
                except Exception as e:
                    logger.warning(f"Failed to capture before state: {e}")

            try:
                # 执行函数
                result = await func(*args, **kwargs)

                # 计算耗时
                duration_ms = (time.time() - start_time) * 1000

                # 提取资源ID (可能从返回结果中获取)
                if not resource_id and result:
                    if isinstance(result, dict):
                        resource_id = result.get("id")
                    elif hasattr(result, "id"):
                        resource_id = str(result.id)

                # 捕获 after 状态
                after_state = None
                if capture_after:
                    if capture_response and result:
                        if isinstance(result, dict):
                            after_state = result
                        elif hasattr(result, "model_dump"):
                            after_state = result.model_dump()
                        elif hasattr(result, "dict"):
                            after_state = result.dict()

                # 记录审计日志
                audit_logger.log(
                    action=action,
                    resource_type=resource_type,
                    resource_id=resource_id,
                    before=before_state,
                    after=after_state,
                    status="success",
                    duration_ms=duration_ms,
                )

                return result

            except Exception as e:
                # 计算耗时
                duration_ms = (time.time() - start_time) * 1000

                # 记录错误审计日志
                audit_logger.log_error(
                    action=action,
                    error_message=str(e),
                    error_code=type(e).__name__,
                    resource_type=resource_type,
                    resource_id=resource_id,
                    duration_ms=duration_ms,
                )

                raise

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            audit_logger = get_audit_logger_instance()
            start_time = time.time()

            # 提取资源ID
            resource_id = None
            if get_resource_id:
                try:
                    resource_id = get_resource_id(*args, **kwargs)
                except Exception:
                    pass

            if not resource_id:
                resource_id = kwargs.get("id") or kwargs.get("draft_id") or kwargs.get("resource_id")

            before_state = None
            if capture_before and resource_id:
                try:
                    before_hook = kwargs.get("_before_capture")
                    if before_hook and callable(before_hook):
                        before_state = before_hook(resource_id)
                except Exception as e:
                    logger.warning(f"Failed to capture before state: {e}")

            try:
                result = func(*args, **kwargs)
                duration_ms = (time.time() - start_time) * 1000

                if not resource_id and result:
                    if isinstance(result, dict):
                        resource_id = result.get("id")
                    elif hasattr(result, "id"):
                        resource_id = str(result.id)

                after_state = None
                if capture_after:
                    if capture_response and result:
                        if isinstance(result, dict):
                            after_state = result
                        elif hasattr(result, "model_dump"):
                            after_state = result.model_dump()
                        elif hasattr(result, "dict"):
                            after_state = result.dict()

                audit_logger.log(
                    action=action,
                    resource_type=resource_type,
                    resource_id=resource_id,
                    before=before_state,
                    after=after_state,
                    status="success",
                    duration_ms=duration_ms,
                )

                return result

            except Exception as e:
                duration_ms = (time.time() - start_time) * 1000

                audit_logger.log_error(
                    action=action,
                    error_message=str(e),
                    error_code=type(e).__name__,
                    resource_type=resource_type,
                    resource_id=resource_id,
                    duration_ms=duration_ms,
                )

                raise

        # 返回适当的包装器
        if functools.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


class AuditContext:
    """
    审计上下文管理器

    用于在代码块中临时设置审计上下文

    Usage:
        with AuditContext(user_id="u_123", username="john"):
            # 所有审计日志都会包含这些信息
            audit_log("document.create", resource_type="document")
    """

    def __init__(
        self,
        user_id: Optional[str] = None,
        username: Optional[str] = None,
        role: Optional[str] = None,
        session_id: Optional[str] = None,
        ip: Optional[str] = None,
        user_agent: Optional[str] = None,
        trace_id: Optional[str] = None,
        tenant_id: Optional[str] = None,
    ):
        from app.logging_config import set_request_context, clear_request_context

        self._user_id = user_id
        self._username = username
        self._role = role
        self._session_id = session_id
        self._ip = ip
        self._user_agent = user_agent
        self._trace_id = trace_id
        self._tenant_id = tenant_id
        self._clear = clear_request_context

    def __enter__(self):
        from app.logging_config import set_request_context
        set_request_context(
            user_id=self._user_id,
            username=self._username,
            role=self._role,
            session_id=self._session_id,
            ip=self._ip,
            user_agent=self._user_agent,
            trace_id=self._trace_id,
            tenant_id=self._tenant_id,
        )
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._clear()
        return False


def with_audit_context(
    user_id: Optional[str] = None,
    username: Optional[str] = None,
    **kwargs,
) -> Callable:
    """
    装饰器：临时设置审计上下文

    Usage:
        @with_audit_context(user_id="u_123", username="john")
        async def background_task():
            audit_log("data.export", resource_type="export")
    """
    def decorator(func: F) -> F:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            with AuditContext(
                user_id=user_id,
                username=username,
                **kwargs,
            ):
                return await func(*args, **kwargs)

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            with AuditContext(
                user_id=user_id,
                username=username,
                **kwargs,
            ):
                return func(*args, **kwargs)

        if functools.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator
