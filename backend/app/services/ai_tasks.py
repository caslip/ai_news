"""
AI 分析任务 - 使用 OpenRouter 进行文章评分和分类
"""

from celery import shared_task
import logging
from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session

from app.config import settings
from app.database import SessionLocal
from app.models.article import Article
from app.models.strategy import Strategy
from app.services.openrouter import (
    score_article,
    generate_summary,
    calculate_hot_score,
    is_low_fan_viral,
    AIServiceError,
)

logger = logging.getLogger(__name__)


def get_db():
    return SessionLocal()


def get_active_strategy_params() -> dict:
    """获取当前激活的策略参数"""
    db = get_db()
    try:
        strategy = db.query(Strategy).filter(Strategy.is_active == True).first()
        if strategy:
            return strategy.params
        return get_default_strategy_params()
    finally:
        db.close()


def get_default_strategy_params() -> dict:
    """默认策略参数"""
    return {
        "max_fan_count": 10000,
        "min_engagement": 100,
        "min_viral_score": 5.0,
        "min_quality_score": 6.0,
        "hotness_boost_threshold": 7.5,
        "exclude_keywords": ["广告", "推广", "抽奖"],
        "target_domains": [],
    }


@shared_task(bind=True, max_retries=3, default_retry_delay=120)
def analyze_article_ai(self, article_id: str):
    """
    分析单篇文章并更新评分
    
    使用 OpenRouter AI 对文章进行：
    1. 内容质量评分
    2. 话题热度评分  
    3. 传播潜力评分
    4. 生成推荐标签
    5. 计算综合热度分数
    6. 判断是否为低粉爆文
    """
    db = get_db()
    try:
        article = db.query(Article).filter(Article.id == article_id).first()
        if not article:
            return {"status": "error", "message": "Article not found"}

        if not settings.openrouter_api_key:
            logger.warning("OpenRouter API key not configured, skipping AI analysis")
            return {"status": "skipped", "reason": "No API key"}

        try:
            scores = score_article(
                title=article.title,
                content=article.summary or "",
                metadata={
                    "source": article.source.name if article.source else "unknown",
                    "author": article.author or "unknown",
                    "engagement": article.engagement or {},
                    "url": article.url,
                },
            )

            quality = scores["quality"]
            hotness = scores["hotness"]
            spread = scores["spread_potential"]
            ai_tags = scores["tags"]
            reasoning = scores.get("reasoning", "")

        except AIServiceError as e:
            logger.error(f"AI scoring failed for article {article_id}: {e}")
            raise self.retry(exc=e)

        hot_score = calculate_hot_score(
            quality=quality,
            hotness=hotness,
            spread=spread,
            engagement=article.engagement or {},
        )

        strategy_params = get_active_strategy_params()
        viral = is_low_fan_viral(
            fan_count=article.fan_count,
            engagement=article.engagement or {},
            quality_score=quality,
            strategy_params=strategy_params,
        )

        article.hot_score = hot_score
        article.is_low_fan_viral = viral

        if ai_tags:
            existing_tags = set(article.tags or [])
            article.tags = list(existing_tags | set(ai_tags))

        if article.raw_metadata:
            article.raw_metadata["ai_analysis"] = {
                "quality": quality,
                "hotness": hotness,
                "spread": spread,
                "reasoning": reasoning,
                "analyzed_at": datetime.utcnow().isoformat(),
            }
        else:
            article.raw_metadata = {
                "ai_analysis": {
                    "quality": quality,
                    "hotness": hotness,
                    "spread": spread,
                    "reasoning": reasoning,
                    "analyzed_at": datetime.utcnow().isoformat(),
                }
            }

        db.commit()

        return {
            "status": "success",
            "article_id": article_id,
            "hot_score": hot_score,
            "is_low_fan_viral": viral,
            "ai_scores": {
                "quality": quality,
                "hotness": hotness,
                "spread": spread,
            },
        }

    except Exception as e:
        db.rollback()
        logger.error(f"analyze_article_ai failed: {e}")
        return {"status": "error", "message": str(e)}
    finally:
        db.close()


@shared_task(bind=True, max_retries=2, default_retry_delay=60)
def generate_article_summary_ai(self, article_id: str):
    """为文章生成摘要"""
    db = get_db()
    try:
        article = db.query(Article).filter(Article.id == article_id).first()
        if not article:
            return {"status": "error", "message": "Article not found"}

        if not article.summary:
            return {"status": "skipped", "reason": "No content to summarize"}

        if not settings.openrouter_api_key:
            return {"status": "skipped", "reason": "No API key"}

        try:
            summary = generate_summary(article.summary, max_length=500)
            article.summary = summary
            db.commit()

            return {
                "status": "success",
                "article_id": article_id,
                "summary_length": len(summary),
            }
        except AIServiceError as e:
            raise self.retry(exc=e)

    except Exception as e:
        db.rollback()
        return {"status": "error", "message": str(e)}
    finally:
        db.close()


@shared_task
def process_pending_articles(limit: int = 20):
    """
    处理待分析的待处理文章
    
    找出未完成 AI 分析的文章，并触发分析任务
    """
    db = get_db()
    try:
        pending_articles = db.query(Article).filter(
            Article.raw_metadata == None,
        ).order_by(Article.created_at.asc()).limit(limit).all()

        results = []
        for article in pending_articles:
            task = analyze_article_ai.delay(str(article.id))
            results.append({
                "article_id": str(article.id),
                "task_id": task.id,
            })

        return {
            "task": "process_pending_articles",
            "timestamp": datetime.utcnow().isoformat(),
            "pending_count": len(pending_articles),
            "queued": results,
        }

    except Exception as e:
        logger.error(f"process_pending_articles failed: {e}")
        return {"task": "process_pending_articles", "error": str(e)}
    finally:
        db.close()


@shared_task
def batch_analyze_articles(article_ids: list[str]):
    """批量分析文章"""
    results = []
    for article_id in article_ids:
        task = analyze_article_ai.delay(article_id)
        results.append({
            "article_id": article_id,
            "task_id": task.id,
        })

    return {
        "task": "batch_analyze_articles",
        "timestamp": datetime.utcnow().isoformat(),
        "total": len(article_ids),
        "queued": results,
    }


@shared_task
def recalculate_all_viral_flags():
    """
    重新计算所有文章的低粉爆文标记
    
    当策略参数更新后调用此任务
    """
    db = get_db()
    try:
        strategy_params = get_active_strategy_params()

        articles = db.query(Article).filter(
            Article.fan_count > 0,
            Article.fan_count <= strategy_params.get("max_fan_count", 10000),
        ).all()

        updated_count = 0
        for article in articles:
            quality = 5.0
            if article.raw_metadata and "ai_analysis" in article.raw_metadata:
                quality = article.raw_metadata["ai_analysis"].get("quality", 5.0)

            viral = is_low_fan_viral(
                fan_count=article.fan_count,
                engagement=article.engagement or {},
                quality_score=quality,
                strategy_params=strategy_params,
            )

            if article.is_low_fan_viral != viral:
                article.is_low_fan_viral = viral
                updated_count += 1

        db.commit()

        return {
            "task": "recalculate_all_viral_flags",
            "timestamp": datetime.utcnow().isoformat(),
            "total_articles": len(articles),
            "updated": updated_count,
        }

    except Exception as e:
        db.rollback()
        logger.error(f"recalculate_all_viral_flags failed: {e}")
        return {"task": "recalculate_all_viral_flags", "error": str(e)}
    finally:
        db.close()
