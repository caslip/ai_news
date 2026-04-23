"""
API 路由 - 监控配置
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models import MonitorConfig
from app.schemas import MonitorConfigCreate, MonitorConfigUpdate, MonitorConfigResponse

router = APIRouter(prefix="/monitor", tags=["监控"])


@router.get("/keywords", response_model=List[MonitorConfigResponse])
def get_monitor_keywords(db: Session = Depends(get_db)):
    """获取所有监控关键词"""
    keywords = db.query(MonitorConfig).filter(
        MonitorConfig.config_type == "keyword"
    ).all()
    return keywords


@router.post("/keywords", response_model=MonitorConfigResponse)
def create_monitor_keyword(
    keyword: MonitorConfigCreate,
    db: Session = Depends(get_db)
):
    """创建监控关键词"""
    db_keyword = MonitorConfig(
        config_type="keyword",
        name=keyword.name,
        value=keyword.value,
        is_active=keyword.is_active,
        params=keyword.params
    )
    db.add(db_keyword)
    db.commit()
    db.refresh(db_keyword)
    return db_keyword


@router.put("/keywords/{keyword_id}", response_model=MonitorConfigResponse)
def update_monitor_keyword(
    keyword_id: str,
    keyword: MonitorConfigUpdate,
    db: Session = Depends(get_db)
):
    """更新监控关键词"""
    db_keyword = db.query(MonitorConfig).filter(
        MonitorConfig.id == keyword_id,
        MonitorConfig.config_type == "keyword"
    ).first()
    
    if not db_keyword:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="关键词不存在"
        )
    
    db_keyword.name = keyword.name
    db_keyword.value = keyword.value
    db_keyword.is_active = keyword.is_active
    db_keyword.params = keyword.params
    
    db.commit()
    db.refresh(db_keyword)
    return db_keyword


@router.delete("/keywords/{keyword_id}")
def delete_monitor_keyword(
    keyword_id: str,
    db: Session = Depends(get_db)
):
    """删除监控关键词"""
    db_keyword = db.query(MonitorConfig).filter(
        MonitorConfig.id == keyword_id,
        MonitorConfig.config_type == "keyword"
    ).first()
    
    if not db_keyword:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="关键词不存在"
        )
    
    db.delete(db_keyword)
    db.commit()
    return {"message": "删除成功"}


@router.get("/accounts", response_model=List[MonitorConfigResponse])
def get_monitor_accounts(db: Session = Depends(get_db)):
    """获取所有监控账号"""
    accounts = db.query(MonitorConfig).filter(
        MonitorConfig.config_type == "account"
    ).all()
    return accounts


@router.post("/accounts", response_model=MonitorConfigResponse)
def create_monitor_account(
    account: MonitorConfigCreate,
    db: Session = Depends(get_db)
):
    """创建监控账号"""
    db_account = MonitorConfig(
        config_type="account",
        name=account.name,
        value=account.value,
        is_active=account.is_active,
        params=account.params
    )
    db.add(db_account)
    db.commit()
    db.refresh(db_account)
    return db_account


@router.put("/accounts/{account_id}", response_model=MonitorConfigResponse)
def update_monitor_account(
    account_id: str,
    account: MonitorConfigUpdate,
    db: Session = Depends(get_db)
):
    """更新监控账号"""
    db_account = db.query(MonitorConfig).filter(
        MonitorConfig.id == account_id,
        MonitorConfig.config_type == "account"
    ).first()
    
    if not db_account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="账号不存在"
        )
    
    db_account.name = account.name
    db_account.value = account.value
    db_account.is_active = account.is_active
    db_account.params = account.params
    
    db.commit()
    db.refresh(db_account)
    return db_account


@router.delete("/accounts/{account_id}")
def delete_monitor_account(
    account_id: str,
    db: Session = Depends(get_db)
):
    """删除监控账号"""
    db_account = db.query(MonitorConfig).filter(
        MonitorConfig.id == account_id,
        MonitorConfig.config_type == "account"
    ).first()
    
    if not db_account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="账号不存在"
        )
    
    db.delete(db_account)
    db.commit()
    return {"message": "删除成功"}


@router.post("/test")
def test_monitor_config(
    value: str,
    config_type: str,
    db: Session = Depends(get_db)
):
    """测试监控配置"""
    # TODO: 实际调用 Twitter API 测试
    return {
        "status": "success",
        "message": f"测试 {config_type}: {value} 连接成功",
        "mock": True
    }
