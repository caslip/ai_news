from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from uuid import UUID
import logging

from app.database import get_db
from app.services.zhihu_crawler import ZhihuCrawlerService
from app.news.schemas.zhihu import (
    ZhihuQuestionBatchCreate,
    ZhihuQuestionResponse,
    ZhihuQuestionListResponse,
    ZhihuQuestionStatsResponse,
    ZhihuQuestionSaveResponse,
    ZhihuQuestionRefreshResponse,
)

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/questions", response_model=ZhihuQuestionSaveResponse)
def save_questions(
    payload: ZhihuQuestionBatchCreate,
    db: Session = Depends(get_db),
):
    """
    接收前端传来的问题数据，批量保存到数据库
    """
    service = ZhihuCrawlerService(db)
    result = service.save_questions(payload.questions)

    return ZhihuQuestionSaveResponse(
        created=result["created"],
        updated=result["updated"],
        skipped=result["skipped"],
        total=result["total"],
        message=f"已保存 {result['created']} 条，新增 {result['updated']} 条更新",
    )


@router.get("/questions", response_model=ZhihuQuestionListResponse)
def list_questions(
    label: str = Query(None, description="标签过滤: surging/new/recommend"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """
    查询已存储的问题列表（支持 label 过滤、分页）
    """
    service = ZhihuCrawlerService(db)
    questions, total = service.get_questions(label=label, page=page, page_size=page_size)

    items = [
        ZhihuQuestionResponse(
            id=q.id,
            zhihu_id=q.zhihu_id,
            title=q.title,
            excerpt=q.excerpt,
            answer_count=q.answer_count,
            follower_count=q.follower_count,
            view_count=q.view_count,
            tags=q.tags or [],
            label=q.label,
            author_name=q.author_name,
            author_url=q.author_url,
            url=q.url,
            content_hash=q.content_hash,
            raw_metadata=q.raw_metadata,
            fetched_at=q.fetched_at,
            created_at=q.created_at,
            updated_at=q.updated_at,
        )
        for q in questions
    ]

    total_pages = (total + page_size - 1) // page_size

    return ZhihuQuestionListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.get("/questions/stats", response_model=ZhihuQuestionStatsResponse)
def get_stats(
    db: Session = Depends(get_db),
):
    """
    获取知乎问题统计信息
    """
    service = ZhihuCrawlerService(db)
    stats = service.get_stats()

    return ZhihuQuestionStatsResponse(**stats)


@router.get("/questions/refresh", response_model=ZhihuQuestionRefreshResponse)
def refresh_reminder(
    db: Session = Depends(get_db),
):
    """
    提醒用户刷新数据（返回数据时效信息）
    """
    service = ZhihuCrawlerService(db)
    last_fetch = service.get_last_fetch_time()

    if last_fetch:
        hours_since = (datetime.utcnow() - last_fetch).total_seconds() / 3600
    else:
        hours_since = None

    message = "数据已过期，请访问知乎邀请页面重新提取" if (hours_since and hours_since > 2) else "数据是最新的"

    return ZhihuQuestionRefreshResponse(
        message=message,
        last_fetch_at=last_fetch.isoformat() if last_fetch else None,
        hours_since_fetch=round(hours_since, 1) if hours_since else None,
    )


@router.get("/questions/{question_id}", response_model=ZhihuQuestionResponse)
def get_question(
    question_id: UUID,
    db: Session = Depends(get_db),
):
    """
    获取单个问题详情
    """
    service = ZhihuCrawlerService(db)
    question = service.get_question_by_id(str(question_id))

    if not question:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Question not found")

    return ZhihuQuestionResponse(
        id=question.id,
        zhihu_id=question.zhihu_id,
        title=question.title,
        excerpt=question.excerpt,
        answer_count=question.answer_count,
        follower_count=question.follower_count,
        view_count=question.view_count,
        tags=question.tags or [],
        label=question.label,
        author_name=question.author_name,
        author_url=question.author_url,
        url=question.url,
        content_hash=question.content_hash,
        raw_metadata=question.raw_metadata,
        fetched_at=question.fetched_at,
        created_at=question.created_at,
        updated_at=question.updated_at,
    )


@router.delete("/questions/{question_id}")
def delete_question(
    question_id: UUID,
    db: Session = Depends(get_db),
):
    """
    删除问题
    """
    service = ZhihuCrawlerService(db)
    deleted = service.delete_question(str(question_id))

    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Question not found")

    return {"message": "Question deleted successfully"}
