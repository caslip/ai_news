"""
日志配置模块

配置 JSON 格式的结构化日志，支持：
- 文件日志 (写入 /app/logs/)
- 控制台日志 (Docker stdout)
- Celery worker 专用日志 (包含 task_id, task_name)
- 审计日志 (包含 before/after 状态快照)
"""

import logging
import logging.handlers
import sys
import os
from contextvars import ContextVar
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4
from pythonjsonlogger import jsonlogger

# ============================================================
# Async-Safe Context Variables for Request Tracing
# ============================================================

request_id_var: ContextVar[str] = ContextVar("request_id", default="")
trace_id_var: ContextVar[str] = ContextVar("trace_id", default="")
tenant_id_var: ContextVar[str] = ContextVar("tenant_id", default="")
user_id_var: ContextVar[str] = ContextVar("user_id", default="")
username_var: ContextVar[str] = ContextVar("username", default="")
session_id_var: ContextVar[str] = ContextVar("session_id", default="")
ip_var: ContextVar[str] = ContextVar("ip", default="")
user_agent_var: ContextVar[str] = ContextVar("user_agent", default="")
role_var: ContextVar[str] = ContextVar("role", default="")

# ============================================================
# Context Manager Functions
# ============================================================

def set_request_context(
    request_id: str = "",
    trace_id: str = "",
    tenant_id: str = "",
    user_id: str = "",
    username: str = "",
    session_id: str = "",
    ip: str = "",
    user_agent: str = "",
    role: str = "",
):
    """设置请求上下文变量"""
    if request_id:
        request_id_var.set(request_id)
    if trace_id:
        trace_id_var.set(trace_id)
    if tenant_id:
        tenant_id_var.set(tenant_id)
    if user_id:
        user_id_var.set(user_id)
    if username:
        username_var.set(username)
    if session_id:
        session_id_var.set(session_id)
    if ip:
        ip_var.set(ip)
    if user_agent:
        user_agent_var.set(user_agent)
    if role:
        role_var.set(role)


def get_request_context() -> dict:
    """获取当前请求上下文字典"""
    return {
        "request_id": request_id_var.get(),
        "trace_id": trace_id_var.get(),
        "tenant_id": tenant_id_var.get(),
        "user_id": user_id_var.get(),
        "username": username_var.get(),
        "session_id": session_id_var.get(),
        "ip": ip_var.get(),
        "user_agent": user_agent_var.get(),
        "role": role_var.get(),
    }


def clear_request_context():
    """清除请求上下文"""
    request_id_var.set("")
    trace_id_var.set("")
    tenant_id_var.set("")
    user_id_var.set("")
    username_var.set("")
    session_id_var.set("")
    ip_var.set("")
    user_agent_var.set("")
    role_var.set("")


def generate_trace_id() -> str:
    """生成新的 trace_id"""
    return str(uuid4())

# 日志目录
LOG_DIR = Path("/app/logs")
LOG_DIR.mkdir(parents=True, exist_ok=True)

# 日志文件路径
APP_LOG_FILE = LOG_DIR / "app.log"
CELERY_LOG_FILE = LOG_DIR / "celery.log"
AUDIT_LOG_FILE = LOG_DIR / "audit.log"

# 默认日志级别
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()


class CustomJsonFormatter(jsonlogger.JsonFormatter):
    """
    自定义 JSON 日志格式化器

    添加以下标准字段：
    - timestamp: ISO 格式时间戳
    - level: 日志级别
    - message: 日志消息
    - module: 模块名
    - function: 函数名
    - line: 行号
    - service: 服务名称
    - request_id: 请求追踪 ID (可选)
    - trace_id: 分布式追踪 ID (可选)
    - tenant_id: 租户 ID (可选)
    - user_id: 用户 ID (可选)
    """

    def __init__(self, *args, **kwargs):
        self.service_name = kwargs.pop("service_name", "ai-news-backend")
        self.service_type = kwargs.pop("service_type", "api")
        self.log_file = kwargs.pop("log_file", None)
        super().__init__(*args, **kwargs)

    def add_fields(self, log_record, record, message_dict):
        super().add_fields(log_record, record, message_dict)

        # 添加时间戳
        log_record["timestamp"] = datetime.now(timezone.utc).isoformat()

        # 添加日志级别
        log_record["level"] = record.levelname

        # 添加标准字段
        log_record["module"] = record.module
        log_record["function"] = record.funcName
        log_record["line"] = record.lineno

        # 添加服务信息
        log_record["service"] = self.service_name
        log_record["service_type"] = self.service_type

        # 添加请求上下文字段 (从 contextvars 读取)
        log_record["request_id"] = request_id_var.get() or None
        log_record["trace_id"] = trace_id_var.get() or None
        log_record["tenant_id"] = tenant_id_var.get() or None
        log_record["user_id"] = user_id_var.get() or None
        log_record["username"] = username_var.get() or None
        log_record["session_id"] = session_id_var.get() or None
        log_record["ip"] = ip_var.get() or None
        log_record["user_agent"] = user_agent_var.get() or None
        log_record["role"] = role_var.get() or None

        # 重命名 message 字段
        if "message" not in log_record and record.getMessage():
            log_record["message"] = record.getMessage()

        # 标记审计日志
        if self.log_file == AUDIT_LOG_FILE:
            log_record["event_type"] = "audit"


class CeleryJsonFormatter(CustomJsonFormatter):
    """
    Celery 专用的 JSON 日志格式化器

    额外添加：
    - task_id: Celery 任务 ID
    - task_name: Celery 任务名称
    """

    def __init__(self, *args, **kwargs):
        kwargs["service_type"] = "celery"
        super().__init__(*args, **kwargs)

    def add_fields(self, log_record, record, message_dict):
        super().add_fields(log_record, record, message_dict)

        # 从 record 中提取 Celery 任务信息
        if hasattr(record, "task_id"):
            log_record["task_id"] = record.task_id
        if hasattr(record, "task_name"):
            log_record["task_name"] = record.task_name


class AuditJsonFormatter(CustomJsonFormatter):
    """
    审计日志专用的 JSON 格式化器

    所有字段与 CustomJsonFormatter 相同，但固定为审计日志
    """

    def __init__(self, *args, **kwargs):
        kwargs["service_type"] = "audit"
        super().__init__(*args, **kwargs)

    def add_fields(self, log_record, record, message_dict):
        super().add_fields(log_record, record, message_dict)
        log_record["event_type"] = "audit"


def setup_logging(service_name: str = "ai-news-backend", service_type: str = "api"):
    """
    初始化日志配置

    Args:
        service_name: 服务名称 (用于日志标签)
        service_type: 服务类型 (api/celery-worker/celery-beat)
    """
    # 获取 root logger
    root_logger = logging.getLogger()

    # 避免重复配置
    if root_logger.handlers:
        root_logger.handlers.clear()

    root_logger.setLevel(getattr(logging, LOG_LEVEL, logging.INFO))

    # JSON formatter
    json_formatter = CustomJsonFormatter(
        "%(timestamp)s %(level)s %(name)s %(message)s",
        service_name=service_name,
        service_type=service_type
    )

    # 文件 handler
    file_handler = logging.handlers.RotatingFileHandler(
        filename=APP_LOG_FILE,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
        encoding="utf-8"
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(json_formatter)

    # 控制台 handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(json_formatter)

    # 添加 handlers
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)

    # 配置 uvicorn 日志
    configure_uvicorn_logging(service_name, service_type)

    # 配置第三方库日志级别
    configure_third_party_logging()

    # 配置审计日志 (独立 logger)
    setup_audit_logging(service_name)

    root_logger.info(f"Logging initialized for {service_name} ({service_type})")


def setup_celery_logging(service_name: str = "ai-news-celery"):
    """
    初始化 Celery 日志配置
    """
    root_logger = logging.getLogger()

    if root_logger.handlers:
        root_logger.handlers.clear()

    root_logger.setLevel(getattr(logging, LOG_LEVEL, logging.INFO))

    # Celery JSON formatter
    celery_formatter = CeleryJsonFormatter(
        "%(timestamp)s %(level)s %(name)s %(message)s",
        service_name=service_name,
        service_type="celery"
    )

    # 文件 handler
    file_handler = logging.handlers.RotatingFileHandler(
        filename=CELERY_LOG_FILE,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
        encoding="utf-8"
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(celery_formatter)

    # 控制台 handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(celery_formatter)

    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)

    # 配置第三方库日志
    configure_third_party_logging()

    # 配置审计日志 (独立 logger)
    setup_audit_logging(service_name)

    root_logger.info(f"Celery logging initialized for {service_name}")


def configure_uvicorn_logging(service_name: str, service_type: str):
    """
    配置 uvicorn 日志 (用于 FastAPI 应用)
    """
    # uvicorn access log
    access_logger = logging.getLogger("uvicorn.access")
    access_logger.setLevel(logging.WARNING)  # 默认关闭 access log
    
    # uvicorn error log
    error_logger = logging.getLogger("uvicorn.error")
    error_logger.setLevel(logging.INFO)
    
    # uvicorn 本身
    uvicorn_logger = logging.getLogger("uvicorn")
    uvicorn_logger.setLevel(logging.INFO)


def configure_third_party_logging():
    """
    配置第三方库的日志级别，避免过多噪音
    """
    # 降低第三方库日志级别
    third_party_loggers = {
        "uvicorn.access": logging.WARNING,
        "httpx": logging.WARNING,
        "httpcore": logging.WARNING,
        "urllib3": logging.WARNING,
        "apscheduler": logging.INFO,
        "sqlalchemy.engine": logging.WARNING,
        "celery": logging.INFO,
        "celery.worker": logging.INFO,
        "celery.tasks": logging.INFO,
    }

    for logger_name, level in third_party_loggers.items():
        logging.getLogger(logger_name).setLevel(level)


def get_logger(name: str) -> logging.Logger:
    """
    获取 logger 实例的便捷函数

    Args:
        name: logger 名称，通常使用 __name__

    Returns:
        Logger 实例
    """
    return logging.getLogger(name)


def setup_audit_logging(service_name: str = "ai-news-backend"):
    """
    初始化审计日志配置

    审计日志使用独立的 logger，写入 audit.log 文件
    """
    audit_logger = logging.getLogger("audit")
    audit_logger.setLevel(logging.INFO)

    # 避免重复添加 handlers
    if audit_logger.handlers:
        return

    # 审计日志 formatter
    audit_formatter = AuditJsonFormatter(
        "%(timestamp)s %(level)s %(name)s %(message)s",
        service_name=service_name,
        service_type="audit",
        log_file=AUDIT_LOG_FILE
    )

    # 审计日志文件 handler
    audit_file_handler = logging.handlers.RotatingFileHandler(
        filename=AUDIT_LOG_FILE,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
        encoding="utf-8"
    )
    audit_file_handler.setLevel(logging.INFO)
    audit_file_handler.setFormatter(audit_formatter)

    # 控制台 handler (可选，用于调试)
    audit_console_handler = logging.StreamHandler(sys.stdout)
    audit_console_handler.setLevel(logging.INFO)
    audit_console_handler.setFormatter(audit_formatter)

    audit_logger.addHandler(audit_file_handler)
    audit_logger.addHandler(audit_console_handler)


def get_audit_logger(name: str = "audit") -> logging.Logger:
    """
    获取审计 logger 实例

    Args:
        name: logger 名称

    Returns:
        Logger 实例
    """
    return logging.getLogger(f"audit.{name}" if name != "audit" else "audit")


# ============================================================
# Legacy RequestContext (保持向后兼容)
# ============================================================

class RequestContext:
    """
    请求上下文管理器 (向后兼容)

    注意: 推荐使用新的 contextvars 函数
    """

    @staticmethod
    def set_request_id(request_id: str):
        request_id_var.set(request_id)

    @staticmethod
    def get_request_id() -> str:
        return request_id_var.get()

    @staticmethod
    def clear_request_id():
        request_id_var.set("")
