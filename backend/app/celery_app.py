from celery import Celery
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

# 自动发现任务
celery_app.autodiscover_tasks(["app.services"])
