from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from typing import Optional
from datetime import datetime, timedelta

from app.database import get_db
from app.models.paper import Paper
from app.models.source import Source
from app.schemas.paper import PaperListResponse, PaperResponse
from app.schemas.user import UserResponse
from app.routers.auth import get_current_user

router = APIRouter()


@router.get("/", response_model=PaperListResponse)
def list_papers(
    source_type: Optional[str] = Query(None, description="信源类型: arxiv / hf_paper"),
    category: Optional[str] = Query(None, description="分类过滤（如 cs.AI）"),
    min_upvotes: Optional[int] = Query(None, ge=0, description="最少点赞数过滤"),
    time_range: Optional[str] = Query("today", description="时间范围: today/week/month"),
    sort: str = Query("time", description="排序: time / upvotes"),
    q: Optional[str] = Query(None, description="搜索关键词（标题/作者）"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
):
    query = db.query(Paper).join(Source, Paper.source_id == Source.id).filter(
        Source.is_active == True
    )

    # 分类过滤
    if category:
        query = query.filter(
            or_(
                Paper.primary_category == category,
                Paper.categories.contains([category])
            )
        )

    # 点赞数过滤（仅 HF paper 有意义，Arxiv 论文为 0）
    if min_upvotes is not None:
        query = query.filter(Paper.upvotes >= min_upvotes)

    # 时间过滤
    now = datetime.utcnow()
    if time_range == "today":
        start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    elif time_range == "week":
        start = now - timedelta(days=7)
    elif time_range == "month":
        start = now - timedelta(days=30)
    else:
        start = now - timedelta(days=1)
    query = query.filter(Paper.published_at >= start)

    # 搜索
    if q:
        search_term = f"%{q}%"
        query = query.filter(
            or_(
                Paper.title.ilike(search_term),
                Paper.author.ilike(search_term),
            )
        )

    # 排序
    if sort == "upvotes":
        query = query.order_by(Paper.upvotes.desc())
    else:
        query = query.order_by(Paper.published_at.desc())

    total = query.count()
    papers = query.offset((page - 1) * page_size).limit(page_size).all()

    return PaperListResponse(
        items=[PaperResponse.model_validate(p) for p in papers],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/stats")
def paper_stats(
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
):
    """论文统计"""
    now = datetime.utcnow()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_start = now - timedelta(days=7)
    month_start = now - timedelta(days=30)

    total = db.query(func.count(Paper.id)).scalar()
    today_count = db.query(func.count(Paper.id)).filter(
        Paper.fetched_at >= today_start
    ).scalar()
    week_count = db.query(func.count(Paper.id)).filter(
        Paper.published_at >= week_start
    ).scalar()
    month_count = db.query(func.count(Paper.id)).filter(
        Paper.published_at >= month_start
    ).scalar()

    return {
        "today_count": today_count or 0,
        "week_count": week_count or 0,
        "month_count": month_count or 0,
        "total_count": total or 0,
    }


@router.get("/{paper_id}", response_model=PaperResponse)
def get_paper(
    paper_id: str,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
):
    """获取单个论文详情"""
    paper = db.query(Paper).filter(Paper.id == paper_id).first()
    if not paper:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Paper not found")
    return PaperResponse.model_validate(paper)
