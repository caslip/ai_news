"""
日志中间件

为每个请求添加唯一 request_id 和 trace_id，便于追踪和关联日志
支持从 JWT 提取用户信息和租户 ID
"""

import uuid
import time
import logging
import os
from typing import Callable
from starlette.types import ASGIApp, Receive, Scope, Send

from app.logging_config import (
    RequestContext,
    set_request_context,
    clear_request_context,
    generate_trace_id,
)

logger = logging.getLogger(__name__)


class RequestLoggingMiddleware:
    """
    请求日志中间件 (原生 ASGI 形式)

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

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        headers_list = scope.get("headers", [])

        def decode_value(val):
            """Decode header value, handling both bytes and strings (and lists)."""
            if isinstance(val, bytes):
                return val.decode("utf-8", errors="replace")
            if isinstance(val, list):
                return [decode_value(v) for v in val]
            return str(val)

        headers_dict: dict[str, str | list[str]] = {}
        if isinstance(headers_list, list):
            for item in headers_list:
                if isinstance(item, tuple) and len(item) == 2:
                    k, v = item
                    k_str = decode_value(k)
                    v_val = decode_value(v)
                    lower_k = k_str.lower()
                    existing = headers_dict.get(lower_k)
                    if existing is not None:
                        if isinstance(existing, list):
                            existing.append(v_val)
                        else:
                            headers_dict[lower_k] = [existing, v_val]
                    else:
                        headers_dict[lower_k] = v_val

        def get_header(name: str, default: str = "") -> str:
            val = headers_dict.get(name.lower(), default)
            if isinstance(val, list):
                return ", ".join(str(v) for v in val)
            return val

        request_id = get_header(self.REQUEST_ID_HEADER) or str(uuid.uuid4())
        trace_id = get_header(self.TRACE_ID_HEADER) or generate_trace_id()

        method = scope.get("method", "UNKNOWN")
        path = scope.get("path", "/")
        client_ip = self._get_client_ip_from_headers(headers_dict)
        user_agent = get_header("user-agent")
        user_id, username, role, tenant_id, session_id = self._extract_user_info_from_headers(
            headers_dict
        )

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

        start_time = time.time()
        logger.info(f"{method} {path}")

        status_code = 500

        async def send_wrapper(message: dict) -> None:
            nonlocal status_code
            if message["type"] == "http.response.start":
                status_code = message["status"]
                headers = list(message.get("headers", []))
                headers.append(
                    (self.REQUEST_ID_HEADER.encode(), request_id.encode())
                )
                headers.append((self.TRACE_ID_HEADER.encode(), trace_id.encode()))
                await send({**message, "headers": headers})
            else:
                await send(message)

        try:
            await self.app(scope, receive, send_wrapper)
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            logger.error(
                f"{method} {path} ERROR: {type(e).__name__}: {e} ({duration_ms:.0f}ms)"
            )
            raise
        finally:
            duration_ms = (time.time() - start_time) * 1000
            logger.info(f"{method} {path} {status_code} {duration_ms:.0f}ms")
            clear_request_context()

    def _get_client_ip_from_headers(self, headers: dict) -> str:
        forwarded_for = headers.get("x-forwarded-for", "")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        real_ip = headers.get("x-real-ip", "")
        if real_ip:
            return real_ip
        return "unknown"

    def _extract_user_info_from_headers(self, headers: dict) -> tuple:
        auth_header = headers.get("authorization", "")

        if not auth_header.startswith("Bearer "):
            return None, None, None, None, None

        token = auth_header[7:]

        try:
            import jwt
            from app.config import settings

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
