"""
调度器 - 定时爬取任务和事件触发爬取
基于 APScheduler 实现每小时定时爬取和创建账号时立即爬取
直接调用 celery_tasks 中的 do_* 核心函数（绕过 @shared_task）
"""

import logging
import threading
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

logger = logging.getLogger(__name__)

_scheduler = None
_scheduler_lock = threading.Lock()


def check_zhihu_stale():
    """
    检查知乎问题数据是否过期，超过 2 小时未更新则输出提醒日志
    """
    try:
        from app.database import SessionLocal
        from app.services.zhihu_crawler import ZhihuCrawlerService

        db = SessionLocal()
        try:
            service = ZhihuCrawlerService(db)
            last_fetch = service.get_last_fetch_time()

            if last_fetch:
                hours_since = (datetime.utcnow() - last_fetch).total_seconds() / 3600
                if hours_since > 2:
                    logger.warning(
                        f"[Scheduler] 知乎问题数据已超过 {hours_since:.1f} 小时未更新，"
                        f"请访问知乎邀请页面重新提取数据"
                    )
                else:
                    logger.info(
                        f"[Scheduler] 知乎问题数据最新，最后更新于 {hours_since:.1f} 小时前"
                    )
            else:
                logger.warning(
                    "[Scheduler] 尚未抓取过知乎问题，请访问知乎邀请页面提取数据"
                )
        finally:
            db.close()
    except Exception as e:
        logger.error(f"[Scheduler] 检查知乎数据时效失败: {e}")


def crawl_all_sources():
    """
    爬取所有信源（在新线程中执行，不阻塞）
    """
    def _run():
        from app.services.celery_tasks import (
            do_crawl_rss_sources,
            do_crawl_nitter_sources,
            do_crawl_twitter_sources,
            do_crawl_github_sources,
            do_crawl_arxiv_sources,
            do_crawl_hf_paper_sources,
        )
        tasks = [
            ("RSS", do_crawl_rss_sources),
            ("Nitter/X", do_crawl_nitter_sources),
            ("Twitter", do_crawl_twitter_sources),
            ("GitHub", do_crawl_github_sources),
            ("Arxiv", do_crawl_arxiv_sources),
            ("HF Papers", do_crawl_hf_paper_sources),
        ]
        for name, task_fn in tasks:
            try:
                result = task_fn()
                logger.info(f"[Scheduler] {name} crawling done: {result}")
            except Exception as e:
                logger.error(f"[Scheduler] {name} crawling failed: {e}")

    thread = threading.Thread(target=_run, daemon=True)
    thread.start()
    logger.info("[Scheduler] Triggered all source crawling in background thread")


def crawl_single_source_sync(source_id: str, source_type: str):
    """
    同步爬取单个信源（在新线程中执行，不阻塞）

    Args:
        source_id: 信源ID
        source_type: 信源类型（仅用于日志）
    """
    def _run():
        from app.services.celery_tasks import do_crawl_single_source
        try:
            result = do_crawl_single_source(source_id)
            logger.info(f"[Scheduler] Single source {source_id} ({source_type}) crawl: {result}")
        except Exception as e:
            logger.error(f"[Scheduler] Single source {source_id} crawl failed: {e}")

    thread = threading.Thread(target=_run, daemon=True)
    thread.start()
    logger.info(f"[Scheduler] Triggered single source {source_id} ({source_type}) crawl in background thread")


def start_scheduler():
    """
    启动调度器（每小时爬取一次所有信源）
    必须在应用启动后调用
    """
    global _scheduler

    with _scheduler_lock:
        if _scheduler is not None:
            logger.warning("[Scheduler] Scheduler already started, skipping")
            return

        _scheduler = BackgroundScheduler(timezone="Asia/Shanghai")
        _scheduler.add_job(
            crawl_all_sources,
            trigger=IntervalTrigger(hours=1),
            id="hourly_crawl_all",
            name="每小时爬取所有信源",
            replace_existing=True,
        )
        _scheduler.add_job(
            check_zhihu_stale,
            trigger=IntervalTrigger(hours=1),
            id="hourly_check_zhihu",
            name="每小时检查知乎问题时效",
            replace_existing=True,
        )
        _scheduler.start()
        logger.info("[Scheduler] Started with hourly crawl schedule")


def stop_scheduler():
    """
    停止调度器
    """
    global _scheduler

    with _scheduler_lock:
        if _scheduler is None:
            return
        _scheduler.shutdown(wait=False)
        _scheduler = None
        logger.info("[Scheduler] Stopped")
