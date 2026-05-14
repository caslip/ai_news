"""Logging module"""

from app.logging_config import (
    setup_logging,
    setup_celery_logging,
    setup_audit_logging,
    get_logger,
    get_audit_logger,
    request_id_var,
    trace_id_var,
    tenant_id_var,
    user_id_var,
    username_var,
    session_id_var,
    ip_var,
    user_agent_var,
    role_var,
    set_request_context,
    get_request_context,
    clear_request_context,
    generate_trace_id,
    RequestContext,
    AUDIT_LOG_FILE,
    APP_LOG_FILE,
    CELERY_LOG_FILE,
    LOG_DIR,
)

from app.logging.audit_logger import AuditLogger, get_audit_logger_instance, audit_log
from app.logging.audit import audit, AuditContext, with_audit_context
from app.logging.router import router as logging_router

__all__ = [
    # Config
    "setup_logging",
    "setup_celery_logging",
    "setup_audit_logging",
    "get_logger",
    "get_audit_logger",
    "AUDIT_LOG_FILE",
    "APP_LOG_FILE",
    "CELERY_LOG_FILE",
    "LOG_DIR",
    # Context vars
    "request_id_var",
    "trace_id_var",
    "tenant_id_var",
    "user_id_var",
    "username_var",
    "session_id_var",
    "ip_var",
    "user_agent_var",
    "role_var",
    "set_request_context",
    "get_request_context",
    "clear_request_context",
    "generate_trace_id",
    "RequestContext",
    # Audit
    "AuditLogger",
    "get_audit_logger_instance",
    "audit_log",
    "audit",
    "AuditContext",
    "with_audit_context",
    # Router
    "logging_router",
]
