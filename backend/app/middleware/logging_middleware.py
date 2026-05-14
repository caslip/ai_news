"""
日志中间件

为每个请求添加唯一 request_id 和 trace_id，便于追踪和关联日志
支持从 JWT 提取用户信息和租户 ID
"""

import uuid
import time
import logging
import os
from typing import Callable, Optional
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.logging_config import (
    RequestContext,
    set_request_context,
    clear_request_context,
    generate_trace_id,
)

logger = logging.getLogger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    请求日志中间件

    功能：
    - 为每个请求生成唯一的 request_id 和 trace_id
    - 支持从请求头提取 trace_id (OpenTelemetry 或自定义)
    - 从 JWT 提取用户信息和租户 ID
    - 记录请求开始/结束的详细信息
    - 记录响应状态码和响应时间
    - 将 request_id 和 trace_id 添加到响应头，便于前端调试
    """

    REQUEST_ID_HEADER = "X-Request-ID"
    TRACE_ID_HEADER = "X-Trace-ID"
    TENANT_ID_HEADER = "X-Tenant-ID"

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # 生成或使用现有的 request_id
        request_id = request.headers.get(self.REQUEST_ID_HEADER) or str(uuid.uuid4())

        # 生成或使用现有的 trace_id
        trace_id = request.headers.get(self.TRACE_ID_HEADER) or generate_trace_id()

        # 获取客户端 IP (支持代理)
        client_ip = self._get_client_ip(request)

        # 获取用户代理
        user_agent = request.headers.get("user-agent", "")

        # 提取用户信息和租户 ID (从 JWT)
        user_id, username, role, tenant_id, session_id = self._extract_user_info(request)

        # 设置请求上下文
        set_request_context(
            request_id=request_id,
            trace_id=trace_id,
            user_id=user_id,
            username=username,
            role=role,
            tenant_id=tenant_id,
            session_id=session_id,
            ip=client_ip,
            user_agent=user_agent,
        )

        # 记录请求开始
        start_time = time.time()

        logger.info(
            "Request started",
            extra={
                "request_id": request_id,
                "trace_id": trace_id,
                "method": request.method,
                "path": request.url.path,
                "query_params": str(request.query_params),
                "client_ip": client_ip,
                "user_agent": user_agent,
                "user_id": user_id,
                "username": username,
                "tenant_id": tenant_id,
            }
        )

        try:
            # 处理请求
            response = await call_next(request)

            # 计算响应时间
            duration_ms = (time.time() - start_time) * 1000

            # 记录请求结束
            logger.info(
                "Request completed",
                extra={
                    "request_id": request_id,
                    "trace_id": trace_id,
                    "method": request.method,
                    "path": request.url.path,
                    "status_code": response.status_code,
                    "duration_ms": round(duration_ms, 2),
                    "user_id": user_id,
                    "username": username,
                }
            )

            # 将 request_id 和 trace_id 添加到响应头
            response.headers[self.REQUEST_ID_HEADER] = request_id
            response.headers[self.TRACE_ID_HEADER] = trace_id

            return response

        except Exception as e:
            # 计算响应时间
            duration_ms = (time.time() - start_time) * 1000

            # 记录异常
            logger.error(
                "Request failed",
                extra={
                    "request_id": request_id,
                    "trace_id": trace_id,
                    "method": request.method,
                    "path": request.url.path,
                    "duration_ms": round(duration_ms, 2),
                    "error": str(e),
                    "error_type": type(e).__name__,
                    "user_id": user_id,
                    "username": username,
                },
                exc_info=True
            )

            raise

        finally:
            # 清除请求上下文
            clear_request_context()

    def _get_client_ip(self, request: Request) -> str:
        """获取客户端真实 IP (支持代理)"""
        # 检查 X-Forwarded-For 头
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            # 取第一个 IP
            return forwarded_for.split(",")[0].strip()

        # 检查 X-Real-IP 头
        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip

        # 回退到直接连接的 IP
        return request.client.host if request.client else "unknown"

    def _extract_user_info(self, request: Request) -> tuple:
        """
        从请求中提取用户信息

        Returns:
            tuple: (user_id, username, role, tenant_id, session_id)
        """
        auth_header = request.headers.get("authorization", "")

        if not auth_header.startswith("Bearer "):
            return None, None, None, None, None

        token = auth_header[7:]  # 去掉 "Bearer " 前缀

        try:
            # 尝试从 JWT 中提取信息
            import jwt
            from app.config import settings

            # 解码 JWT (不验证签名，仅提取信息)
            payload = jwt.decode(
                token,
                options={"verify_signature": False},
                algorithms=["HS256", "RS256"],
            )

            return (
                payload.get("sub") or payload.get("user_id"),
                payload.get("email") or payload.get("username"),
                payload.get("role"),
                payload.get("tenant_id"),
                payload.get("session_id") or payload.get("sid"),
            )
        except Exception:
            # JWT 解码失败，返回默认值
            return None, None, None, None, None


def get_request_id() -> str:
    """
    获取当前请求的 request_id

    Returns:
        当前请求的 request_id，如果没有则返回空字符串
    """
    return RequestContext.get_request_id()


def get_trace_id() -> str:
    """
    获取当前请求的 trace_id

    Returns:
        当前请求的 trace_id，如果没有则返回空字符串
    """
    from app.logging_config import trace_id_var
    return trace_id_var.get()


def get_tenant_id() -> str:
    """
    获取当前请求的 tenant_id

    Returns:
        当前请求的 tenant_id，如果没有则返回空字符串
    """
    from app.logging_config import tenant_id_var
    return tenant_id_var.get()


def get_user_id() -> str:
    """
    获取当前请求的 user_id

    Returns:
        当前请求的 user_id，如果没有则返回空字符串
    """
    from app.logging_config import user_id_var
    return user_id_var.get()


def get_username() -> str:
    """
    获取当前请求的 username

    Returns:
        当前请求的 username，如果没有则返回空字符串
    """
    from app.logging_config import username_var
    return username_var.get()


def get_logger_with_context(name: str) -> logging.LoggerAdapter:
    """
    获取带有请求上下文的 logger adapter

    Args:
        name: logger 名称

    Returns:
        LoggerAdapter 实例，自动添加请求上下文到日志
    """
    base_logger = logging.getLogger(name)
    from app.logging_config import get_request_context

    context = get_request_context()

    class ContextAdapter(logging.LoggerAdapter):
        def process(self, msg, kwargs):
            extra = kwargs.get("extra", {})
            extra.update({k: v for k, v in context.items() if v})
            kwargs["extra"] = extra
            return msg, kwargs

    return ContextAdapter(base_logger, context)


def get_audit_logger(name: str = "audit") -> logging.Logger:
    """
    获取审计日志记录器

    Args:
        name: logger 名称

    Returns:
        Logger 实例
    """
    from app.logging_config import get_audit_logger as _get_audit_logger
    return _get_audit_logger(name)
