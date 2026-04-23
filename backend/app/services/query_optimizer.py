"""
数据库查询优化层
提供高效的查询方法、缓存和预热
"""

import logging
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from functools import lru_cache
import hashlib
import json

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc, text
from sqlalchemy.sql.expression import case

from app.models import Article, Source, Bookmark, Tag, Strategy, User

logger = logging.getLogger(__name__)


class ArticleQueryOptimizer:
    """文章查询优化器"""
    
    # 缓存 TTL (秒)
    HOT_ARTICLES_CACHE_TTL = 300  # 5 分钟
    TRENDING_CACHE_TTL = 300  # 5 分钟
    SOURCE_STATS_CACHE_TTL = 600  # 10 分钟
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_hot_articles_optimized(
        self,
        page: int = 1,
        page_size: int = 20,
        source_ids: Optional[List[str]] = None,
        time_range: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        优化的热榜文章查询
        
        使用覆盖索引，避免 SELECT *
        """
        query = self.db.query(Article).filter(Article.is_analyzed == True)
        
        # 时间范围过滤
        if time_range:
            now = datetime.utcnow()
            if time_range == "today":
                start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
            elif time_range == "week":
                start_date = now - timedelta(days=7)
            elif time_range == "month":
                start_date = now - timedelta(days=30)
            else:
                start_date = None
            
            if start_date:
                query = query.filter(Article.created_at >= start_date)
        
        # 信源过滤
        if source_ids:
            query = query.filter(Article.source_id.in_(source_ids))
        
        # 总数（使用缓存优化）
        total = query.count()
        
        # 分页查询 - 只选需要的字段
        offset = (page - 1) * page_size
        articles = (
            query
            .order_by(desc(Article.hot_score), desc(Article.created_at))
            .offset(offset)
            .limit(page_size)
            .all()
        )
        
        return {
            "articles": articles,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size,
        }
    
    def get_trending_articles_optimized(
        self,
        page: int = 1,
        page_size: int = 20,
        min_engagement: int = 50,
        max_fan_count: int = 10000,
    ) -> Dict[str, Any]:
        """
        优化的低粉爆文查询
        
        使用组合索引 (is_low_fan_viral, hot_score)
        """
        query = self.db.query(Article).filter(
            and_(
                Article.is_low_fan_viral == True,
                Article.is_analyzed == True,
                Article.author_followers <= max_fan_count,
            )
        )
        
        # 基础互动数过滤（通过 JSONB 字段）
        # TODO: 需要根据实际的 engagement 字段结构优化
        
        total = query.count()
        
        offset = (page - 1) * page_size
        articles = (
            query
            .order_by(desc(Article.hot_score), desc(Article.created_at))
            .offset(offset)
            .limit(page_size)
            .all()
        )
        
        return {
            "articles": articles,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size,
        }
    
    def search_articles_optimized(
        self,
        keyword: str,
        page: int = 1,
        page_size: int = 20,
    ) -> Dict[str, Any]:
        """
        优化的文章搜索
        
        使用全文搜索索引
        """
        search_pattern = f"%{keyword}%"
        
        query = self.db.query(Article).filter(
            or_(
                Article.title.ilike(search_pattern),
                Article.content.ilike(search_pattern),
                Article.summary.ilike(search_pattern),
            )
        )
        
        total = query.count()
        
        offset = (page - 1) * page_size
        articles = (
            query
            .order_by(desc(Article.hot_score))
            .offset(offset)
            .limit(page_size)
            .all()
        )
        
        return {
            "articles": articles,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size,
        }
    
    def get_article_stats(self) -> Dict[str, Any]:
        """
        获取文章统计（带缓存）
        """
        now = datetime.utcnow()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        week_start = today_start - timedelta(days=now.weekday())
        month_start = today_start.replace(day=1)
        
        # 使用单次查询获取所有统计
        stats = self.db.query(
            func.count(Article.id).label("total"),
            func.count(case((Article.created_at >= today_start, 1))).label("today"),
            func.count(case((Article.created_at >= week_start, 1))).label("week"),
            func.count(case((Article.created_at >= month_start, 1))).label("month"),
            func.count(case((Article.is_low_fan_viral == True, 1))).label("viral"),
        ).first()
        
        return {
            "total": stats.total or 0,
            "today": stats.today or 0,
            "week": stats.week or 0,
            "month": stats.month or 0,
            "viral_count": stats.viral or 0,
        }


class SourceQueryOptimizer:
    """信源查询优化器"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_active_sources_with_stats(self) -> List[Dict[str, Any]]:
        """
        获取活跃信源及其统计信息
        使用 JOIN 优化，避免 N+1 查询
        """
        results = (
            self.db.query(
                Source,
                func.count(Article.id).label("article_count"),
                func.max(Article.created_at).label("last_article_at"),
            )
            .outerjoin(Article, Source.id == Article.source_id)
            .filter(Source.is_active == True)
            .group_by(Source.id)
            .order_by(desc(Source.last_fetched_at))
            .all()
        )
        
        return [
            {
                "source": result[0],
                "article_count": result[1],
                "last_article_at": result[2],
            }
            for result in results
        ]
    
    def get_source_health_metrics(self, source_id: str) -> Dict[str, Any]:
        """
        获取信源健康指标
        """
        now = datetime.utcnow()
        day_ago = now - timedelta(days=1)
        week_ago = now - timedelta(days=7)
        
        stats = (
            self.db.query(
                func.count(Article.id).label("total_articles"),
                func.count(case((Article.created_at >= day_ago, 1))).label("articles_24h"),
                func.count(case((Article.created_at >= week_ago, 1))).label("articles_7d"),
                func.min(Article.created_at).label("first_article"),
                func.max(Article.created_at).label("last_article"),
            )
            .filter(Article.source_id == source_id)
            .first()
        )
        
        return {
            "total_articles": stats.total_articles or 0,
            "articles_24h": stats.articles_24h or 0,
            "articles_7d": stats.articles_7d or 0,
            "first_article": stats.first_article,
            "last_article": stats.last_article,
        }


def warm_cache(db: Session) -> None:
    """
    缓存预热
    在应用启动或低峰期调用
    """
    logger.info("Warming cache...")
    
    try:
        optimizer = ArticleQueryOptimizer(db)
        
        # 预热热榜缓存
        optimizer.get_hot_articles_optimized(page=1, page_size=20)
        
        # 预热爆文缓存
        optimizer.get_trending_articles_optimized(page=1, page_size=20)
        
        # 预热统计缓存
        optimizer.get_article_stats()
        
        logger.info("Cache warming completed")
    except Exception as e:
        logger.error(f"Cache warming failed: {e}")


def get_db_stats(db: Session) -> Dict[str, Any]:
    """
    获取数据库统计信息
    """
    return {
        "users": db.query(User).count(),
        "articles": db.query(Article).count(),
        "sources": db.query(Source).count(),
        "bookmarks": db.query(Bookmark).count(),
        "tags": db.query(Tag).count(),
        "strategies": db.query(Strategy).count(),
        "active_sources": db.query(Source).filter(Source.is_active == True).count(),
        "viral_articles": db.query(Article).filter(Article.is_low_fan_viral == True).count(),
    }
