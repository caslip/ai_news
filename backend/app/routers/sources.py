from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.models.source import Source, SourceType
from app.models.user import User
from app.schemas.source import (
    SourceCreate,
    SourceUpdate,
    SourceResponse,
    SourceListResponse,
    SourceTestResponse,
    SourceBatchDeleteRequest,
)
from app.schemas.user import UserResponse
from app.routers.auth import get_current_user

router = APIRouter()


@router.get("/", response_model=SourceListResponse)
def list_sources(
    type: Optional[str] = Query(None, description="信源类型过滤 (rss/twitter/github/nitter/keyword/account)"),
    monitor_type: Optional[str] = Query(None, description="监控类型过滤 (keyword/account)"),
    is_active: Optional[bool] = Query(None, description="是否激活"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
):
    query = db.query(Source)

    if type:
        query = query.filter(Source.type == type)

    if monitor_type:
        query = query.filter(Source.monitor_type == monitor_type)

    if is_active is not None:
        query = query.filter(Source.is_active == is_active)

    total = query.count()
    sources = query.order_by(Source.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()

    return SourceListResponse(
        items=[SourceResponse.model_validate(s) for s in sources],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.post("/", response_model=SourceResponse, status_code=status.HTTP_201_CREATED)
def create_source(
    source_data: SourceCreate,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
):
    # 信源管理页面只允许创建 rss 和 github 类型
    # X 账号（nitter/twitter）和监控配置（keyword/account）通过 X 监控页面创建
    if source_data.type not in ("rss", "github"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不支持从此入口创建该类型信源，请使用 X 监控页面"
        )
    source = Source(
        name=source_data.name,
        type=source_data.type,
        config=source_data.config,
        created_by=current_user.id,
        user_id=source_data.user_id or current_user.id,
        monitor_type=source_data.monitor_type,
    )
    db.add(source)
    db.commit()
    db.refresh(source)
    return SourceResponse.model_validate(source)


@router.get("/{source_id}", response_model=SourceResponse)
def get_source(
    source_id: str,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
):
    source = db.query(Source).filter(Source.id == source_id).first()
    if not source:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Source not found")
    return SourceResponse.model_validate(source)


@router.put("/{source_id}", response_model=SourceResponse)
def update_source(
    source_id: str,
    source_data: SourceUpdate,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
):
    source = db.query(Source).filter(Source.id == source_id).first()
    if not source:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Source not found")

    # 信源管理页面只允许操作 rss 和 github 类型
    if source_data.type is not None and source_data.type not in ("rss", "github"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不支持从此入口修改该类型信源，请使用 X 监控页面"
        )

    update_dict = source_data.model_dump(exclude_unset=True)
    for key, value in update_dict.items():
        setattr(source, key, value)

    db.commit()
    db.refresh(source)
    return SourceResponse.model_validate(source)


@router.patch("/{source_id}/toggle", response_model=SourceResponse)
def toggle_source(
    source_id: str,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
):
    source = db.query(Source).filter(Source.id == source_id).first()
    if not source:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Source not found")

    source.is_active = not source.is_active
    db.commit()
    db.refresh(source)
    return SourceResponse.model_validate(source)


@router.delete("/{source_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_source(
    source_id: str,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
):
    source = db.query(Source).filter(Source.id == source_id).first()
    if not source:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Source not found")

    db.delete(source)
    db.commit()


@router.post("/batch-delete", status_code=status.HTTP_200_OK)
def batch_delete_sources(
    request: SourceBatchDeleteRequest,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
):
    deleted_count = 0
    not_found_ids = []

    for source_id in request.source_ids:
        source = db.query(Source).filter(Source.id == source_id).first()
        if source:
            db.delete(source)
            deleted_count += 1
        else:
            not_found_ids.append(source_id)

    db.commit()

    return {
        "deleted_count": deleted_count,
        "not_found_ids": not_found_ids,
        "total_requested": len(request.source_ids),
    }


@router.post("/{source_id}/test", response_model=SourceTestResponse)
def test_source(
    source_id: str,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
):
    source = db.query(Source).filter(Source.id == source_id).first()
    if not source:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Source not found")

    try:
        from app.services.crawler import crawl_source
        source_type_val = source.type.value if hasattr(source.type, 'value') else str(source.type)
        articles = crawl_source({
            "type": source_type_val,
            **source.config,
        })

        return SourceTestResponse(
            success=True,
            message=f"成功抓取 {len(articles)} 篇文章",
            article_count=len(articles),
        )
    except Exception as e:
        return SourceTestResponse(
            success=False,
            message=f"抓取失败: {str(e)}",
            article_count=0,
        )
