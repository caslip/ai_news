"""
Celery Beat 调度任务配置
定义所有定时抓取任务
"""

from celery.schedules import crontab
from app.celery_app import celery_app


# Celery Beat 调度表
# ====================

# Nitter 抓取 - 每 5 分钟（无需 API Key）
celery_app.conf.beat_schedule["crawl-netter-sources"] = {
    "task": "app.services.celery_tasks.crawl_netter_sources",
    "schedule": crontab(minute="*/5"),  # 每 5 分钟
}

# RSS 抓取 - 每 15 分钟
celery_app.conf.beat_schedule["crawl-rss-feeds"] = {
    "task": "app.services.celery_tasks.crawl_all_rss_feeds",
    "schedule": crontab(minute="*/15"),  # 每 15 分钟
}

# Twitter 抓取 - 每天早上 8 点
celery_app.conf.beat_schedule["crawl-twitter-accounts"] = {
    "task": "app.services.celery_tasks.crawl_all_twitter_accounts",
    "schedule": crontab(hour=8, minute=0),  # 每天早上 8 点
}

# GitHub Release 抓取 - 每 30 分钟
celery_app.conf.beat_schedule["crawl-github-releases"] = {
    "task": "app.services.celery_tasks.crawl_all_github_sources",
    "schedule": crontab(minute="*/30"),  # 每 30 分钟
}

# 热榜缓存刷新 - 每 5 分钟
celery_app.conf.beat_schedule["refresh-hot-articles-cache"] = {
    "task": "app.services.celery_tasks.refresh_hot_articles_cache",
    "schedule": crontab(minute="*/5"),  # 每 5 分钟
}

# AI 分析任务 - 每分钟检查待处理文章
celery_app.conf.beat_schedule["process-pending-articles"] = {
    "task": "app.services.celery_tasks.process_pending_articles",
    "schedule": crontab(minute="*"),  # 每分钟
}

# 健康检查 - 每小时
celery_app.conf.beat_schedule["health-check"] = {
    "task": "app.services.celery_tasks.health_check",
    "schedule": crontab(minute=0),  # 每小时整点
}

# 清理过期数据 - 每天凌晨 3 点
celery_app.conf.beat_schedule["cleanup-old-data"] = {
    "task": "app.services.celery_tasks.cleanup_old_data",
    "schedule": crontab(hour=3, minute=0),  # 每天凌晨 3 点
}
