from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, func
from typing import Optional
from uuid import UUID
from datetime import datetime, timedelta

from app.database import get_db
from app.models.article import Article
from app.models.source import Source
from app.models.bookmark import Bookmark
from app.schemas.article import (
    ArticleResponse,
    ArticleListResponse,
    ArticleStatsResponse,
)
from app.schemas.user import UserResponse
from app.routers.auth import get_current_user

router = APIRouter()


from app.routers.auth import get_current_user_optional


def get_time_filter(time_range: str):
    now = datetime.utcnow()
    if time_range == "today":
        start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    elif time_range == "week":
        start = now - timedelta(days=7)
    elif time_range == "month":
        start = now - timedelta(days=30)
    else:
        start = now - timedelta(days=1)
    return start


@router.get("/", response_model=ArticleListResponse)
def list_articles(
    source: Optional[str] = Query(None, description="信源 ID 过滤"),
    source_type: Optional[str] = Query(None, description="信源类型过滤"),
    time_range: Optional[str] = Query("today", description="时间范围: today/week/month"),
    sort: Optional[str] = Query("hot", description="排序: hot/time"),
    q: Optional[str] = Query(None, description="搜索关键词"),
    is_low_fan_viral: Optional[bool] = Query(None, description="低粉爆文过滤"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: Optional[UserResponse] = Depends(get_current_user_optional),
):
    query = db.query(Article)

    # 时间过滤
    start_time = get_time_filter(time_range)
    query = query.filter(Article.fetched_at >= start_time)

    # 信源过滤
    if source:
        query = query.filter(Article.source_id == UUID(source))

    if source_type:
        query = query.join(Source).filter(Source.type == source_type)

    # 低粉爆文过滤
    if is_low_fan_viral is not None:
        query = query.filter(Article.is_low_fan_viral == is_low_fan_viral)

    # 搜索
    if q:
        search_term = f"%{q}%"
        query = query.filter(
            or_(
                Article.title.ilike(search_term),
                Article.summary.ilike(search_term),
            )
        )

    # 排序
    if sort == "hot":
        query = query.order_by(Article.hot_score.desc())
    else:
        query = query.order_by(Article.fetched_at.desc())

    # 总数
    total = query.count()

    # 分页
    articles = query.offset((page - 1) * page_size).limit(page_size).all()

    # 获取用户收藏状态
    bookmarked_ids = set()
    if current_user:
        bookmarks = db.query(Bookmark).filter(
            Bookmark.user_id == UUID(current_user.id),
            Bookmark.article_id.in_([a.id for a in articles])
        ).all()
        bookmarked_ids = {b.article_id for b in bookmarks}

    # 构建响应
    items = []
    for article in articles:
        try:
            source_type = None
            if article.source:
                source_type = article.source.type.value if hasattr(article.source.type, 'value') else str(article.source.type)
            
            item = ArticleResponse(
                id=str(article.id),
                source_id=str(article.source_id) if article.source_id else None,
                source_name=article.raw_metadata.get("repo", article.source.name) if article.raw_metadata else (article.source.name if article.source else None),
                source_type=source_type,
                title=article.title,
                url=article.url,
                summary=article.summary,
                author=article.author,
                hot_score=article.hot_score or 0,
                fan_count=article.fan_count or 0,
                engagement=article.engagement or {},
                is_low_fan_viral=article.is_low_fan_viral or False,
                tags=article.tags or [],
                raw_metadata=article.raw_metadata,
                fetched_at=article.fetched_at,
                published_at=article.published_at,
                created_at=article.created_at,
                is_bookmarked=article.id in bookmarked_ids,
            )
            items.append(item)
        except Exception as e:
            print(f"Error building response for article {article.id}: {e}")
            continue

    total_pages = (total + page_size - 1) // page_size

    return ArticleListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.get("/trending", response_model=ArticleListResponse)
def list_trending_articles(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: Optional[UserResponse] = Depends(get_current_user_optional),
):
    """获取低粉爆文列表"""
    query = db.query(Article).filter(Article.is_low_fan_viral == True)

    total = query.count()
    articles = query.order_by(Article.hot_score.desc()).offset((page - 1) * page_size).limit(page_size).all()

    # 获取用户收藏状态
    bookmarked_ids = set()
    if current_user:
        bookmarks = db.query(Bookmark).filter(
            Bookmark.user_id == UUID(current_user.id),
            Bookmark.article_id.in_([a.id for a in articles])
        ).all()
        bookmarked_ids = {b.article_id for b in bookmarks}

    items = []
    for article in articles:
        source_type_val = article.source.type.value if article.source and hasattr(article.source.type, 'value') else str(article.source.type) if article.source else None
        source_name = article.raw_metadata.get("repo", article.source.name) if article.raw_metadata else (article.source.name if article.source else None)
        items.append(ArticleResponse(
            id=str(article.id),
            source_id=str(article.source_id) if article.source_id else None,
            source_name=source_name,
            source_type=source_type_val,
            title=article.title,
            url=article.url,
            summary=article.summary,
            author=article.author,
            hot_score=article.hot_score,
            fan_count=article.fan_count,
            engagement=article.engagement or {},
            is_low_fan_viral=article.is_low_fan_viral,
            tags=article.tags or [],
            raw_metadata=article.raw_metadata,
            fetched_at=article.fetched_at,
            published_at=article.published_at,
            created_at=article.created_at,
            is_bookmarked=article.id in bookmarked_ids,
        ))

    total_pages = (total + page_size - 1) // page_size

    return ArticleListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.get("/stats", response_model=ArticleStatsResponse)
def get_article_stats(
    db: Session = Depends(get_db),
):
    """获取文章统计"""
    now = datetime.utcnow()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_start = now - timedelta(days=7)
    month_start = now - timedelta(days=30)

    today_count = db.query(func.count(Article.id)).filter(Article.fetched_at >= today_start).scalar()
    week_count = db.query(func.count(Article.id)).filter(Article.fetched_at >= week_start).scalar()
    month_count = db.query(func.count(Article.id)).filter(Article.fetched_at >= month_start).scalar()
    total_count = db.query(func.count(Article.id)).scalar()

    return ArticleStatsResponse(
        today_count=today_count or 0,
        week_count=week_count or 0,
        month_count=month_count or 0,
        total_count=total_count or 0,
    )


@router.get("/{article_id}", response_model=ArticleResponse)
def get_article(
    article_id: UUID,
    db: Session = Depends(get_db),
    current_user: Optional[UserResponse] = Depends(get_current_user),
):
    article = db.query(Article).filter(Article.id == article_id).first()
    if not article:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Article not found")

    is_bookmarked = False
    if current_user:
        bookmark = db.query(Bookmark).filter(
            Bookmark.user_id == UUID(current_user.id),
            Bookmark.article_id == article_id,
        ).first()
        is_bookmarked = bookmark is not None

    return ArticleResponse(
        id=str(article.id),
        source_id=str(article.source_id) if article.source_id else None,
        source_name=article.raw_metadata.get("repo", article.source.name) if article.raw_metadata else (article.source.name if article.source else None),
        source_type=article.source.type.value if article.source else None,
        title=article.title,
        url=article.url,
        summary=article.summary,
        author=article.author,
        hot_score=article.hot_score,
        fan_count=article.fan_count,
        engagement=article.engagement or {},
        is_low_fan_viral=article.is_low_fan_viral,
        tags=article.tags or [],
        raw_metadata=article.raw_metadata,
        fetched_at=article.fetched_at,
        published_at=article.published_at,
        created_at=article.created_at,
        is_bookmarked=is_bookmarked,
    )
