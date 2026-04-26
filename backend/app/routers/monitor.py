"""
API 路由 - 监控配置
所有关键词和账号监控配置现在统一存储在 sources 表中：
- type='keyword', monitor_type='keyword'  -> 关键词监控
- type='account', monitor_type='account'  -> 账号监控
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.source import Source
from app.schemas.source import SourceCreate, SourceUpdate, SourceResponse
from app.schemas.user import UserResponse
from app.routers.auth import get_current_user

router = APIRouter(prefix="/monitor", tags=["监控"])


# ─── 关键词监控 ───────────────────────────────────────────────

@router.get("/keywords", response_model=List[SourceResponse])
def get_monitor_keywords(
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
):
    """获取当前用户的所有关键词监控配置"""
    keywords = db.query(Source).filter(
        Source.user_id == current_user.id,
        Source.monitor_type == "keyword"
    ).all()
    return [SourceResponse.model_validate(k) for k in keywords]


@router.post("/keywords", response_model=SourceResponse, status_code=status.HTTP_201_CREATED)
def create_monitor_keyword(
    keyword: SourceCreate,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
):
    """创建关键词监控配置"""
    keyword_value = keyword.value or keyword.name
    source = Source(
        name=keyword.name,
        type="keyword",
        config={"keyword": keyword_value, "params": keyword.params or {}},
        is_active=keyword.is_active,
        user_id=current_user.id,
        monitor_type="keyword",
    )
    db.add(source)
    db.commit()
    db.refresh(source)
    return SourceResponse.model_validate(source)


@router.put("/keywords/{keyword_id}", response_model=SourceResponse)
def update_monitor_keyword(
    keyword_id: str,
    update: SourceUpdate,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
):
    """更新关键词监控配置"""
    source = db.query(Source).filter(
        Source.id == keyword_id,
        Source.user_id == current_user.id,
        Source.monitor_type == "keyword"
    ).first()

    if not source:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="关键词不存在"
        )

    if update.name is not None:
        source.name = update.name
    if update.is_active is not None:
        source.is_active = update.is_active
    if update.config is not None:
        source.config = update.config

    db.commit()
    db.refresh(source)
    return SourceResponse.model_validate(source)


@router.delete("/keywords/{keyword_id}")
def delete_monitor_keyword(
    keyword_id: str,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
):
    """删除关键词监控配置"""
    source = db.query(Source).filter(
        Source.id == keyword_id,
        Source.user_id == current_user.id,
        Source.monitor_type == "keyword"
    ).first()

    if not source:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="关键词不存在"
        )

    db.delete(source)
    db.commit()
    return {"message": "删除成功"}


# ─── 账号监控（Nitter 信源 + Account 监控）────────────────────

@router.get("/accounts", response_model=List[SourceResponse])
def get_monitor_accounts(
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
):
    """获取当前用户的所有账号监控配置（包括 Nitter 信源和 Account 监控）"""
    # 监控页面的"账号"实际包括：
    # 1. monitor_type='account' 的账号监控（必须有 user_id）
    # 2. monitor_type='nitter' 的账号监控（必须有 user_id）
    # 3. type='nitter' 的信源（可能是旧数据，user_id 可能为空）
    #    对于无 user_id 的 nitter 信源，假设是当前用户的（向后兼容）
    accounts = db.query(Source).filter(
        (
            Source.user_id == current_user.id
        ) | (
            Source.type == "nitter"
        )
    ).filter(
        (
            Source.monitor_type.in_(["account", "nitter"])
        ) | (
            Source.type == "nitter"
        )
    ).all()
    return [SourceResponse.model_validate(a) for a in accounts]


@router.post("/accounts", response_model=SourceResponse, status_code=status.HTTP_201_CREATED)
def create_monitor_account(
    account: SourceCreate,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
):
    """
    创建账号监控配置（支持 Nitter 信源和 Account 监控）
    - type='nitter' 或 monitor_type='nitter' -> Nitter 信源
    - type='account' 或 monitor_type='account' -> Account 监控
    """
    # 统一处理：自动设置正确的 type 和 monitor_type
    monitor_type = account.monitor_type or "account"
    source_type = "nitter" if monitor_type == "nitter" else "account"
    account_value = account.value.lstrip("@") if account.value else account.name.lstrip("@")

    source = Source(
        name=account.name,
        type=source_type,
        config={"username": account_value, "account": account_value, "params": account.params or {}},
        is_active=account.is_active,
        user_id=current_user.id,
        monitor_type=monitor_type,
    )
    db.add(source)
    db.commit()
    db.refresh(source)
    return SourceResponse.model_validate(source)


@router.put("/accounts/{account_id}", response_model=SourceResponse)
def update_monitor_account(
    account_id: str,
    update: SourceUpdate,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
):
    """更新账号监控配置"""
    source = db.query(Source).filter(
        Source.id == account_id,
        (
            (Source.user_id == current_user.id) | (Source.type == "nitter")
        ),
        (
            (Source.monitor_type.in_(["account", "nitter"])) | (Source.type == "nitter")
        )
    ).first()

    if not source:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="账号不存在"
        )

    if update.name is not None:
        source.name = update.name
    if update.is_active is not None:
        source.is_active = update.is_active
    if update.config is not None:
        source.config = update.config

    db.commit()
    db.refresh(source)
    return SourceResponse.model_validate(source)


@router.delete("/accounts/{account_id}")
def delete_monitor_account(
    account_id: str,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
):
    """删除账号监控配置"""
    source = db.query(Source).filter(
        Source.id == account_id,
        (
            (Source.user_id == current_user.id) | (Source.type == "nitter")
        ),
        (
            (Source.monitor_type.in_(["account", "nitter"])) | (Source.type == "nitter")
        )
    ).first()

    if not source:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="账号不存在"
        )

    db.delete(source)
    db.commit()
    return {"message": "删除成功"}


# ─── 测试 ─────────────────────────────────────────────────────

@router.post("/test")
def test_monitor_config(
    value: str,
    config_type: str,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
):
    """测试监控配置"""
    return {
        "status": "success",
        "message": f"测试 {config_type}: {value} 连接成功",
        "mock": True
    }
