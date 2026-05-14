from celery import Celery, signals
from celery.schedules import crontab
from app.config import settings

celery_app = Celery(
    "ai_news",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=[
        "app.services.celery_tasks",
        "app.services.ai_tasks",
        "app.services.sse_tasks",
    ]
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,
    task_soft_time_limit=25 * 60,
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    result_expires=3600,
    broker_connection_retry_on_startup=True,
)

celery_app.conf.beat_schedule = {
    # RSS 抓取 - 每 15 分钟
    "crawl-rss-sources": {
        "task": "app.services.celery_tasks.crawl_rss_sources",
        "schedule": crontab(minute="*/15"),
    },
    # GitHub 抓取 - 每 30 分钟
    "crawl-github-sources": {
        "task": "app.services.celery_tasks.crawl_github_sources",
        "schedule": crontab(minute="*/30"),
    },
    # Nitter 抓取 - 每 5 分钟
    "crawl-nitter-sources": {
        "task": "app.services.celery_tasks.crawl_nitter_sources",
        "schedule": crontab(minute="*/5"),
    },
    # Twitter 抓取 - 每 5 分钟（通过 Nitter RSS，无需 API Key）
    "crawl-twitter-sources": {
        "task": "app.services.celery_tasks.crawl_twitter_sources",
        "schedule": crontab(minute="*/5"),
    },
    # 热榜缓存刷新 - 每 5 分钟
    "refresh-hot-articles-cache": {
        "task": "app.services.celery_tasks.refresh_hot_articles_cache",
        "schedule": crontab(minute="*/5"),
    },
    # AI 分析待处理文章 - 每分钟
    "process-pending-ai-analysis": {
        "task": "app.services.ai_tasks.process_pending_articles",
        "schedule": crontab(minute="*"),
    },
    # 健康检查 - 每小时
    "health-check": {
        "task": "app.services.celery_tasks.health_check",
        "schedule": crontab(minute=0),
    },
}

# ============================================================
# Celery Task Signal Handlers for Context Propagation
# ============================================================

@signals.task_prerun.connect
def on_task_prerun(sender=None, task_id=None, task=None, *args, **kwargs):
    """
    Task pre-run signal handler

    Sets up logging context for the task before it runs
    """
    from app.logging_config import set_request_context, generate_trace_id

    # Extract context from task request
    request = task.request if hasattr(task, 'request') else None
    trace_context = {}

    if request:
        # Try to get trace context from task headers/kwargs
        headers = getattr(request, 'headers', {}) or {}
        trace_context = headers.get('trace_context', {})

    # Set up logging context
    set_request_context(
        request_id=task_id,
        trace_id=trace_context.get('trace_id') or generate_trace_id(),
        tenant_id=trace_context.get('tenant_id'),
        user_id=trace_context.get('user_id'),
        username=trace_context.get('username'),
        session_id=trace_context.get('session_id'),
    )


@signals.task_postrun.connect
def on_task_postrun(sender=None, task_id=None, task=None, *args, **kwargs):
    """
    Task post-run signal handler

    Cleans up logging context after task completes
    """
    from app.logging_config import clear_request_context
    clear_request_context()


@signals.task_success.connect
def on_task_success(sender=None, result=None, *args, **kwargs):
    """
    Task success signal handler

    Logs successful task completion as an audit event
    """
    from app.logging.audit_logger import get_audit_logger_instance
    from app.logging_config import get_request_context
    import time

    task = sender
    context = get_request_context()

    audit_logger = get_audit_logger_instance()
    audit_logger.log(
        action=f"task.{task.name}.success",
        resource_type="task",
        resource_id=task_id,
        status="success",
        duration_ms=getattr(task, '_start_time', None),
    )


@signals.task_failure.connect
def on_task_failure(sender=None, exception=None, *args, **kwargs):
    """
    Task failure signal handler

    Logs task failure as an audit event
    """
    from app.logging.audit_logger import get_audit_logger_instance
    from app.logging_config import get_request_context

    task = sender
    context = get_request_context()

    audit_logger = get_audit_logger_instance()
    audit_logger.log(
        action=f"task.{task.name}.failed",
        resource_type="task",
        resource_id=task.request.id if hasattr(task, 'request') else None,
        status="failed",
        error_code=type(exception).__name__ if exception else "UnknownError",
        error_message=str(exception) if exception else "Task failed without exception",
    )


@signals.task_revoked.connect
def on_task_revoked(sender=None, *args, **kwargs):
    """
    Task revoked signal handler

    Logs task revocation
    """
    from app.logging.audit_logger import get_audit_logger_instance
    from app.logging_config import get_request_context

    task = sender
    audit_logger = get_audit_logger_instance()
    audit_logger.log(
        action=f"task.{task.name}.revoked",
        resource_type="task",
        resource_id=task.request.id if hasattr(task, 'request') else None,
        status="failed",
        error_code="TaskRevoked",
        error_message="Task was revoked",
    )


# ============================================================
# Helper Functions for Task Context Propagation
# ============================================================

def get_task_trace_context() -> dict:
    """
    Get the current trace context for propagating to child tasks

    Returns:
        dict: Trace context dictionary with trace_id, tenant_id, etc.
    """
    from app.logging_config import get_request_context
    context = get_request_context()
    return {
        'trace_id': context.get('trace_id'),
        'tenant_id': context.get('tenant_id'),
        'user_id': context.get('user_id'),
        'username': context.get('username'),
        'session_id': context.get('session_id'),
    }


def create_task_with_context(task_func, *args, **kwargs):
    """
    Create a task call that includes trace context

    Usage:
        # Instead of:
        task_func.delay(arg1, arg2)

        # Use:
        create_task_with_context(task_func, arg1, arg2)
    """
    trace_context = get_task_trace_context()
    kwargs.setdefault('headers', {})['trace_context'] = trace_context
    return task_func.delay(*args, **kwargs)


# 自动发现任务
celery_app.autodiscover_tasks(["app.services"])
