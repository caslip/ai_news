"""
AI Writer Drafts Router - CRUD operations for drafts
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from typing import Optional

from app.database import get_db
from app.models.draft import Draft
from app.news.schemas.user import UserResponse
from app.news.routers.auth import get_current_user
from app.writer.schemas.draft import (
    DraftResponse,
    DraftListResponse,
    BatchDeleteRequest,
    BatchDeleteResponse,
    WriterStats,
)

router = APIRouter(prefix="/drafts", tags=["写作草稿"])


@router.get("/", response_model=DraftListResponse)
def list_drafts(
    status: Optional[str] = Query(None, description="Filter by status: generating, completed, failed"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
):
    """
    获取当前用户的所有草稿列表（分页）
    """
    query = db.query(Draft).filter(Draft.created_by == current_user.id)
    
    # Apply status filter if provided
    if status:
        query = query.filter(Draft.status == status)
    
    # Get total count
    total = query.count()
    
    # Get paginated items
    items = query.order_by(
        Draft.updated_at.desc()
    ).offset((page - 1) * page_size).limit(page_size).all()
    
    return DraftListResponse(
        items=[DraftResponse.model_validate(d) for d in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/stats", response_model=WriterStats)
def get_writer_stats(
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
):
    """
    获取写作统计信息
    """
    user_id = current_user.id
    
    # Get today's start time
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    
    # Total drafts
    total_drafts = db.query(func.count(Draft.id)).filter(
        Draft.created_by == user_id
    ).scalar() or 0
    
    # Today's drafts count
    today_count = db.query(func.count(Draft.id)).filter(
        Draft.created_by == user_id,
        Draft.created_at >= today_start
    ).scalar() or 0
    
    # Total words written
    total_words = db.query(func.sum(Draft.word_count)).filter(
        Draft.created_by == user_id,
        Draft.status == "completed"
    ).scalar() or 0
    
    # Average duration (simplified - using created_at vs updated_at difference)
    completed_drafts = db.query(Draft).filter(
        Draft.created_by == user_id,
        Draft.status == "completed"
    ).all()
    
    if completed_drafts:
        total_duration = sum(
            (d.updated_at - d.created_at).total_seconds() 
            for d in completed_drafts 
            if d.updated_at and d.created_at
        )
        avg_duration = total_duration / len(completed_drafts) if completed_drafts else 0
    else:
        avg_duration = 0.0
    
    return WriterStats(
        today_count=today_count,
        total_drafts=total_drafts,
        total_words=total_words,
        avg_duration_seconds=round(avg_duration, 2),
    )


@router.get("/{draft_id}", response_model=DraftResponse)
def get_draft(
    draft_id: str,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
):
    """
    获取单个草稿详情
    """
    draft = db.query(Draft).filter(
        Draft.id == draft_id,
        Draft.created_by == current_user.id,
    ).first()
    
    if not draft:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="草稿不存在"
        )
    
    return DraftResponse.model_validate(draft)


@router.delete("/{draft_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_draft(
    draft_id: str,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
):
    """
    删除单个草稿
    """
    draft = db.query(Draft).filter(
        Draft.id == draft_id,
        Draft.created_by == current_user.id,
    ).first()
    
    if not draft:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="草稿不存在"
        )
    
    db.delete(draft)
    db.commit()


@router.post("/batch-delete", response_model=BatchDeleteResponse)
def batch_delete_drafts(
    request: BatchDeleteRequest,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
):
    """
    批量删除草稿
    """
    if not request.draft_ids:
        return BatchDeleteResponse(deleted_count=0)
    
    deleted_count = db.query(Draft).filter(
        Draft.id.in_(request.draft_ids),
        Draft.created_by == current_user.id,
    ).delete(synchronize_session=False)
    
    db.commit()
    
    return BatchDeleteResponse(deleted_count=deleted_count)
