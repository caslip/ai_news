"""
Celery 定时任务 - 内容抓取与缓存
"""

from celery import shared_task
import redis
import json
import logging
from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.config import settings
from app.database import SessionLocal
from app.models.source import Source, SourceType
from app.models.article import Article
from app.services.crawler import RSSCrawler, GitHubCrawler, NitterCrawler

logger = logging.getLogger(__name__)

_redis_client = None


def _get_redis_client():
    """Lazy Redis client - only connects when actually used"""
    global _redis_client
    if _redis_client is None:
        _redis_client = redis.from_url(settings.redis_url, decode_responses=True)
    return _redis_client


def get_db():
    db = SessionLocal()
    try:
        return db
    finally:
        pass


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def crawl_rss_sources(self):
    """抓取所有活跃的 RSS 信源"""
    db = get_db()
    try:
        sources = db.query(Source).filter(
            Source.is_active == True,
            Source.type == SourceType.RSS
        ).all()

        results = []
        for source in sources:
            try:
                feed_url = source.config.get("feed_url")
                if not feed_url:
                    continue

                crawler = RSSCrawler()
                articles = crawler.fetch_sync(feed_url)

                saved_count = 0
                for article_data in articles:
                    if save_article(db, source.id, article_data):
                        saved_count += 1

                source.last_fetched_at = datetime.utcnow()
                db.commit()

                results.append({
                    "source_id": str(source.id),
                    "source_name": source.name,
                    "fetched": len(articles),
                    "new": saved_count,
                    "status": "success",
                })
                logger.info(f"RSS source {source.name}: fetched {len(articles)}, new {saved_count}")

            except Exception as e:
                logger.error(f"Failed to crawl RSS source {source.name}: {e}")
                results.append({
                    "source_id": str(source.id),
                    "source_name": source.name,
                    "error": str(e),
                    "status": "failed",
                })

        return {
            "task": "crawl_rss_sources",
            "timestamp": datetime.utcnow().isoformat(),
            "sources_count": len(sources),
            "results": results,
        }

    except Exception as e:
        logger.error(f"crawl_rss_sources failed: {e}")
        raise self.retry(exc=e)
    finally:
        db.close()


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def crawl_twitter_sources(self):
    """抓取所有 Twitter 信源（通过 Nitter RSS，无需 API Key）"""
    db = get_db()
    try:
        sources = db.query(Source).filter(
            Source.is_active == True,
            Source.type == SourceType.TWITTER
        ).all()

        results = []
        for source in sources:
            try:
                account = source.config.get("account", "").lstrip("@")
                if not account:
                    continue

                # 使用 NitterCrawler 获取推文，保留原始 source_type
                crawler = NitterCrawler()
                tweets = crawler.fetch_user_tweets_sync(account, max_results=20, source_type_override="twitter")

                saved_count = 0
                for article_data in tweets:
                    if save_article(db, source.id, article_data):
                        saved_count += 1

                source.last_fetched_at = datetime.utcnow()
                db.commit()

                results.append({
                    "source_id": str(source.id),
                    "account": account,
                    "fetched": len(tweets),
                    "new": saved_count,
                    "status": "success",
                })

            except Exception as e:
                logger.error(f"Failed to crawl Twitter {source.name}: {e}")
                results.append({
                    "source_id": str(source.id),
                    "account": source.config.get("account"),
                    "error": str(e),
                    "status": "failed",
                })

        return {
            "task": "crawl_twitter_sources",
            "timestamp": datetime.utcnow().isoformat(),
            "results": results,
        }

    except Exception as e:
        raise self.retry(exc=e)
    finally:
        db.close()


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def crawl_nitter_sources(self):
    """抓取所有 Nitter 信源（无需 API Key）- 仅限 X 监控页面创建的信源）"""
    db = get_db()
    try:
        # 只爬取 monitor_type='nitter' 的信源（通过 X 监控页面创建）
        # 也兼容旧的 type='nitter', monitor_type=null 的信源（向后兼容）
        sources = db.query(Source).filter(
            Source.is_active == True,
            Source.type == SourceType.NETTER,
            Source.monitor_type.in_(["nitter", None])
        ).all()

        if not sources:
            logger.info("No active Nitter sources found")
            return {"task": "crawl_nitter_sources", "status": "skipped", "reason": "No active Nitter sources"}

        results = []
        for source in sources:
            try:
                username = source.config.get("username", "")
                if not username:
                    logger.warning(f"Nitter source {source.name} has no username configured")
                    continue

                crawler = NitterCrawler()
                tweets = crawler.fetch_user_tweets_sync(username, max_results=20)

                saved_count = 0
                for article_data in tweets:
                    if save_article(db, source.id, article_data):
                        saved_count += 1

                source.last_fetched_at = datetime.utcnow()
                db.commit()

                results.append({
                    "source_id": str(source.id),
                    "source_name": source.name,
                    "username": username,
                    "fetched": len(tweets),
                    "new": saved_count,
                    "status": "success",
                })
                logger.info(f"Nitter source {source.name} (@{username}): fetched {len(tweets)}, new {saved_count}")

            except Exception as e:
                logger.error(f"Failed to crawl Nitter source {source.name}: {e}")
                results.append({
                    "source_id": str(source.id),
                    "source_name": source.name,
                    "username": source.config.get("username", ""),
                    "error": str(e),
                    "status": "failed",
                })

        return {
            "task": "crawl_nitter_sources",
            "timestamp": datetime.utcnow().isoformat(),
            "sources_count": len(sources),
            "results": results,
        }

    except Exception as e:
        logger.error(f"crawl_nitter_sources failed: {e}")
        raise self.retry(exc=e)
    finally:
        db.close()


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def crawl_github_sources(self):
    """抓取所有 GitHub Trending 信源"""
    db = get_db()
    try:
        sources = db.query(Source).filter(
            Source.is_active == True,
            Source.type == SourceType.GITHUB
        ).all()

        results = []
        for source in sources:
            try:
                language = source.config.get("language", "")
                since = source.config.get("since", "daily")

                crawler = GitHubCrawler()
                trending = crawler.fetch_trending_sync(language=language, since=since)

                saved_count = 0
                for article_data in trending:
                    if save_article(db, source.id, article_data):
                        saved_count += 1

                source.last_fetched_at = datetime.utcnow()
                db.commit()

                results.append({
                    "source_id": str(source.id),
                    "source": source.name,
                    "language": language or "all",
                    "since": since,
                    "fetched": len(trending),
                    "new": saved_count,
                    "status": "success",
                })

            except Exception as e:
                logger.error(f"Failed to crawl GitHub {source.name}: {e}")
                results.append({
                    "source_id": str(source.id),
                    "error": str(e),
                    "status": "failed",
                })

        return {
            "task": "crawl_github_sources",
            "timestamp": datetime.utcnow().isoformat(),
            "results": results,
        }

    except Exception as e:
        raise self.retry(exc=e)
    finally:
        db.close()


@shared_task
def refresh_hot_articles_cache():
    """刷新热榜文章缓存"""
    db = get_db()
    try:
        cache_key = "hot_articles:daily"
        cache_ttl = 300

        hot_articles = db.query(Article).order_by(
            Article.hot_score.desc()
        ).limit(100).all()

        articles_data = [
            {
                "id": str(a.id),
                "title": a.title,
                "url": a.url,
                "hot_score": a.hot_score,
                "is_low_fan_viral": a.is_low_fan_viral,
            }
            for a in hot_articles
        ]

        _get_redis_client().setex(cache_key, cache_ttl, json.dumps(articles_data))

        return {
            "task": "refresh_hot_articles_cache",
            "timestamp": datetime.utcnow().isoformat(),
            "count": len(articles_data),
        }

    except Exception as e:
        logger.error(f"refresh_hot_articles_cache failed: {e}")
        return {"task": "refresh_hot_articles_cache", "error": str(e)}
    finally:
        db.close()


@shared_task
def health_check():
    """系统健康检查"""
    checks = {
        "database": "unknown",
        "redis": "unknown",
        "timestamp": datetime.utcnow().isoformat(),
    }

    db = get_db()
    try:
        db.execute("SELECT 1")
        checks["database"] = "ok"
    except Exception as e:
        checks["database"] = f"error: {str(e)}"
    finally:
        db.close()

    try:
        _get_redis_client().ping()
        checks["redis"] = "ok"
    except Exception as e:
        checks["redis"] = f"error: {str(e)}"

    return {"task": "health_check", "checks": checks}


@shared_task
def crawl_single_source(source_id: str):
    """手动触发单个信源抓取"""
    db = get_db()
    try:
        source = db.query(Source).filter(Source.id == source_id).first()
        if not source:
            return {"status": "error", "message": "Source not found"}

        if source.type == SourceType.RSS:
            feed_url = source.config.get("feed_url")
            if not feed_url:
                return {"status": "error", "message": "No feed URL configured"}
            
            crawler = RSSCrawler()
            articles = crawler.fetch_sync(feed_url)
            
        elif source.type == SourceType.NETTER:
            username = source.config.get("username", "")
            if not username:
                return {"status": "error", "message": "No username configured for Nitter source"}

            crawler = NitterCrawler()
            articles = crawler.fetch_user_tweets_sync(username, max_results=20)

        elif source.type == SourceType.TWITTER:
            # Twitter 类型使用 Nitter RSS 获取，但保留原始 source_type
            account = source.config.get("account", "").lstrip("@")
            if not account:
                return {"status": "error", "message": "No account configured for Twitter source"}

            crawler = NitterCrawler()
            articles = crawler.fetch_user_tweets_sync(account, max_results=20, source_type_override="twitter")

        elif source.type == SourceType.GITHUB:
            language = source.config.get("language", "")
            since = source.config.get("since", "daily")

            crawler = GitHubCrawler()
            articles = crawler.fetch_trending_sync(language=language, since=since)
            
        else:
            return {"status": "error", "message": f"Unsupported type: {source.type}"}

        saved_count = 0
        for article_data in articles:
            if save_article(db, source.id, article_data):
                saved_count += 1

        source.last_fetched_at = datetime.utcnow()
        db.commit()

        return {
            "status": "success",
            "source_name": source.name,
            "fetched": len(articles),
            "new": saved_count,
        }

    except Exception as e:
        logger.error(f"crawl_single_source failed: {e}")
        return {"status": "error", "message": str(e)}
    finally:
        db.close()


def save_article(db: Session, source_id, article_data) -> bool:
    """
    保存文章到数据库，处理去重
    
    Args:
        article_data: ParsedArticle 对象或字典
    
    Returns:
        True if new article was saved, False if duplicate or error
    """
    try:
        # 处理 ParsedArticle 对象
        if hasattr(article_data, 'content_hash'):
            content_hash = article_data.content_hash
            title = article_data.title
            url = article_data.url
            summary = article_data.summary
            author = article_data.author
            fan_count = getattr(article_data, 'fan_count', 0)
            engagement = getattr(article_data, 'engagement', None)
            tags = getattr(article_data, 'tags', [])
            raw_metadata = article_data.raw_metadata
            published_at = article_data.published_at
        else:
            content_hash = article_data.get("content_hash")
            title = article_data["title"]
            url = article_data["url"]
            summary = article_data.get("summary", "")
            author = article_data.get("author", "")
            fan_count = article_data.get("fan_count", 0)
            engagement = article_data.get("engagement", None)
            tags = article_data.get("tags", [])
            raw_metadata = article_data.get("raw_metadata", {})
            published_at = article_data.get("published_at")
        
        existing = db.query(Article).filter(
            Article.content_hash == content_hash
        ).first()
        
        if existing:
            return False

        article = Article(
            source_id=source_id,
            title=title,
            url=url,
            summary=summary,
            content_hash=content_hash,
            author=author,
            hot_score=0,
            fan_count=fan_count,
            engagement=engagement or {"likes": 0, "retweets": 0, "comments": 0},
            is_low_fan_viral=False,
            tags=tags,
            raw_metadata=raw_metadata,
            published_at=published_at,
            fetched_at=datetime.utcnow(),
        )
        
        db.add(article)
        db.commit()

        return True

    except Exception as e:
        db.rollback()
        logger.error(f"save_article failed: {e}")
        return False
