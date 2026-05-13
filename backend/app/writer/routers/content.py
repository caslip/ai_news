"""
AI 写作助手 API 路由
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from uuid import UUID

from app.database import get_db
from app.models.writer import GeneratedContent
from app.news.schemas.user import UserResponse
from app.news.routers.auth import get_current_user
from app.writer.schemas.content import (
    ContentCreate,
    ContentUpdate,
    ContentResponse,
    ContentListResponse,
)

router = APIRouter(prefix="/content", tags=["写作内容"])


@router.get("/", response_model=ContentListResponse)
def list_content(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
):
    """获取当前用户的所有生成内容"""
    query = db.query(GeneratedContent).filter(
        GeneratedContent.created_by == current_user.id
    )

    total = query.count()
    items = query.order_by(
        GeneratedContent.created_at.desc()
    ).offset((page - 1) * page_size).limit(page_size).all()

    return ContentListResponse(
        items=[ContentResponse.model_validate(c) for c in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.post("/", response_model=ContentResponse, status_code=status.HTTP_201_CREATED)
def create_content(
    data: ContentCreate,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
):
    """保存生成的内容"""
    content = GeneratedContent(
        source_article_ids=data.source_article_ids,
        source_article_titles=data.source_article_titles,
        content=data.content,
        platform=data.platform,
        prompt=data.prompt,
        status="draft",
        created_by=current_user.id,
    )
    db.add(content)
    db.commit()
    db.refresh(content)
    return ContentResponse.model_validate(content)


@router.get("/{content_id}", response_model=ContentResponse)
def get_content(
    content_id: UUID,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
):
    """获取单条内容"""
    content = db.query(GeneratedContent).filter(
        GeneratedContent.id == str(content_id),
        GeneratedContent.created_by == current_user.id,
    ).first()

    if not content:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="内容不存在")

    return ContentResponse.model_validate(content)


@router.put("/{content_id}", response_model=ContentResponse)
def update_content(
    content_id: UUID,
    data: ContentUpdate,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
):
    """更新内容"""
    content = db.query(GeneratedContent).filter(
        GeneratedContent.id == str(content_id),
        GeneratedContent.created_by == current_user.id,
    ).first()

    if not content:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="内容不存在")

    if data.content is not None:
        content.content = data.content
    if data.status is not None:
        content.status = data.status
    if data.prompt is not None:
        content.prompt = data.prompt

    db.commit()
    db.refresh(content)
    return ContentResponse.model_validate(content)


@router.delete("/{content_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_content(
    content_id: UUID,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
):
    """删除内容"""
    content = db.query(GeneratedContent).filter(
        GeneratedContent.id == str(content_id),
        GeneratedContent.created_by == current_user.id,
    ).first()

    if not content:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="内容不存在")

    db.delete(content)
    db.commit()
