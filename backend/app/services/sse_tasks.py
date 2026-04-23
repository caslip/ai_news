"""
Celery 任务 - SSE 事件推送
"""

from celery import shared_task
import asyncio
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


@shared_task
def push_new_article_event(article_data: dict):
    """
    推送新文章事件
    
    这是一个同步任务，实际推送通过异步函数完成
    """
    try:
        from app.services.sse import notify_new_article, sse_manager
        
        # 使用 asyncio 在 Celery worker 中运行异步代码
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(notify_new_article(article_data))
        finally:
            loop.close()
        
        return {"status": "success", "article_id": article_data.get("id")}
    except Exception as e:
        logger.error(f"Failed to push new article event: {e}")
        return {"status": "error", "message": str(e)}


@shared_task
def push_trending_update(trending_articles: List[Dict[str, Any]]):
    """
    推送爆文更新事件
    """
    try:
        from app.services.sse import notify_trending_update
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(notify_trending_update(trending_articles))
        finally:
            loop.close()
        
        return {"status": "success", "count": len(trending_articles)}
    except Exception as e:
        logger.error(f"Failed to push trending update: {e}")
        return {"status": "error", "message": str(e)}


@shared_task
def push_monitor_alert(keyword: str, tweet_data: dict, matched_type: str = "keyword"):
    """
    推送监控告警事件
    """
    try:
        from app.services.sse import notify_monitor_alert
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(notify_monitor_alert(keyword, tweet_data, matched_type))
        finally:
            loop.close()
        
        return {"status": "success", "keyword": keyword}
    except Exception as e:
        logger.error(f"Failed to push monitor alert: {e}")
        return {"status": "error", "message": str(e)}


@shared_task
def push_system_notification(message: str, level: str = "info"):
    """
    推送系统通知
    """
    try:
        from app.services.sse import notify_system
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(notify_system(message, level))
        finally:
            loop.close()
        
        return {"status": "success", "message": message}
    except Exception as e:
        logger.error(f"Failed to push system notification: {e}")
        return {"status": "error", "message": str(e)}
