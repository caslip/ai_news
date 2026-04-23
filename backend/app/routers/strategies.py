from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from uuid import UUID

from app.database import get_db
from app.models.strategy import Strategy
from app.schemas.strategy import (
    StrategyCreate,
    StrategyUpdate,
    StrategyResponse,
    StrategyListResponse,
)
from app.schemas.user import UserResponse
from app.routers.auth import get_current_user

router = APIRouter()


@router.get("/", response_model=StrategyListResponse)
def list_strategies(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
):
    query = db.query(Strategy)

    total = query.count()
    strategies = query.order_by(Strategy.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()

    return StrategyListResponse(
        items=[StrategyResponse.model_validate(s) for s in strategies],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/active", response_model=StrategyResponse)
def get_active_strategy(
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
):
    strategy = db.query(Strategy).filter(Strategy.is_active == True).first()
    if not strategy:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No active strategy found")
    return StrategyResponse.model_validate(strategy)


@router.post("/", response_model=StrategyResponse, status_code=status.HTTP_201_CREATED)
def create_strategy(
    strategy_data: StrategyCreate,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
):
    # 检查同名策略
    existing = db.query(Strategy).filter(Strategy.name == strategy_data.name).first()
    version = 1
    if existing:
        # 获取最大版本号
        max_version = db.query(Strategy).filter(
            Strategy.name == strategy_data.name
        ).order_by(Strategy.version.desc()).first()
        version = max_version.version + 1 if max_version else 1

    strategy = Strategy(
        name=strategy_data.name,
        description=strategy_data.description,
        version=version,
        params=strategy_data.params,
        is_active=False,
        created_by=UUID(current_user.id),
    )
    db.add(strategy)
    db.commit()
    db.refresh(strategy)
    return StrategyResponse.model_validate(strategy)


@router.put("/{strategy_id}", response_model=StrategyResponse)
def update_strategy(
    strategy_id: UUID,
    strategy_data: StrategyUpdate,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
):
    # 获取原策略
    old_strategy = db.query(Strategy).filter(Strategy.id == strategy_id).first()
    if not old_strategy:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Strategy not found")

    # 创建新版本
    new_strategy = Strategy(
        name=strategy_data.name or old_strategy.name,
        description=strategy_data.description if strategy_data.description is not None else old_strategy.description,
        version=old_strategy.version + 1,
        params=strategy_data.params or old_strategy.params,
        is_active=False,
        created_by=UUID(current_user.id),
    )
    
    # 禁用旧策略
    old_strategy.is_active = False

    db.add(new_strategy)
    db.commit()
    db.refresh(new_strategy)
    return StrategyResponse.model_validate(new_strategy)


@router.patch("/{strategy_id}/activate", response_model=StrategyResponse)
def activate_strategy(
    strategy_id: UUID,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
):
    strategy = db.query(Strategy).filter(Strategy.id == strategy_id).first()
    if not strategy:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Strategy not found")

    # 禁用所有同名策略
    db.query(Strategy).filter(Strategy.name == strategy.name).update({"is_active": False})

    # 激活当前策略
    strategy.is_active = True
    db.commit()
    db.refresh(strategy)
    return StrategyResponse.model_validate(strategy)


@router.get("/{strategy_id}/history")
def get_strategy_history(
    strategy_id: UUID,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
):
    strategy = db.query(Strategy).filter(Strategy.id == strategy_id).first()
    if not strategy:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Strategy not found")

    # 获取同名策略的所有版本
    histories = db.query(Strategy).filter(
        Strategy.name == strategy.name
    ).order_by(Strategy.version.desc()).all()

    return {
        "items": [StrategyResponse.model_validate(s) for s in histories],
        "total": len(histories),
    }


@router.delete("/{strategy_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_strategy(
    strategy_id: UUID,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
):
    strategy = db.query(Strategy).filter(Strategy.id == strategy_id).first()
    if not strategy:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Strategy not found")

    db.delete(strategy)
    db.commit()
