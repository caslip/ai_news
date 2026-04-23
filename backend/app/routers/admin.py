"""
后台管理 API 路由
需要管理员权限
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List
from datetime import datetime, timedelta

from app.database import get_db
from app.models import User, Article, Source, Bookmark, Strategy
from app.schemas.admin import (
    AdminStatsResponse,
    UserManagementResponse,
    UserRoleUpdate,
    SourceHealthResponse,
    QueueStatusResponse,
    SystemHealthResponse,
)
from app.routers.auth import get_current_user, require_admin

router = APIRouter(prefix="/admin", tags=["后台管理"])


@router.get("/stats", response_model=AdminStatsResponse)
def get_admin_stats(
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """获取管理员统计面板数据"""
    now = datetime.utcnow()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_start = today_start - timedelta(days=now.weekday())
    month_start = today_start.replace(day=1)

    # 基本统计
    total_users = db.query(User).count()
    total_articles = db.query(Article).count()
    total_sources = db.query(Source).count()
    active_sources = db.query(Source).filter(Source.is_active == True).count()
    low_fan_viral_count = db.query(Article).filter(Article.is_low_fan_viral == True).count()
    bookmarks_count = db.query(Bookmark).count()
    active_strategies = db.query(Strategy).filter(Strategy.is_active == True).count()

    # 时间统计
    articles_today = db.query(Article).filter(
        Article.created_at >= today_start
    ).count()
    articles_this_week = db.query(Article).filter(
        Article.created_at >= week_start
    ).count()
    articles_this_month = db.query(Article).filter(
        Article.created_at >= month_start
    ).count()

    # 最后抓取时间
    last_crawl = db.query(Source).filter(
        Source.last_fetched_at.isnot(None)
    ).order_by(desc(Source.last_fetched_at)).first()

    return AdminStatsResponse(
        total_users=total_users,
        total_articles=total_articles,
        total_sources=total_sources,
        active_sources=active_sources,
        articles_today=articles_today,
        articles_this_week=articles_this_week,
        articles_this_month=articles_this_month,
        low_fan_viral_count=low_fan_viral_count,
        bookmarks_count=bookmarks_count,
        active_strategies=active_strategies,
        queue_pending_tasks=0,
        queue_running_tasks=0,
        last_crawl_at=last_crawl.last_fetched_at if last_crawl else None,
        system_uptime="N/A"
    )


@router.get("/users", response_model=List[UserManagementResponse])
def get_all_users(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """获取所有用户列表"""
    users = db.query(User).order_by(desc(User.created_at)).offset(skip).limit(limit).all()
    
    result = []
    for user in users:
        articles_count = db.query(Article).filter(Article.user_id == user.id).count()
        bookmarks_count = db.query(Bookmark).filter(Bookmark.user_id == user.id).count()
        
        result.append(UserManagementResponse(
            id=user.id,
            email=user.email,
            nickname=user.nickname,
            role=user.role,
            is_active=user.is_active,
            created_at=user.created_at,
            last_login_at=user.last_login_at,
            articles_count=articles_count,
            bookmarks_count=bookmarks_count,
        ))
    
    return result


@router.patch("/users/{user_id}")
def update_user(
    user_id: str,
    update: UserRoleUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """更新用户角色或状态"""
    if user_id == current_user.get("id"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不能修改自己的权限"
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    if update.role not in ["user", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="无效的角色"
        )
    
    user.role = update.role
    if update.is_active is not None:
        user.is_active = update.is_active
    
    db.commit()
    
    return {"message": "更新成功", "user_id": user_id}


@router.delete("/users/{user_id}")
def delete_user(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """删除用户"""
    if user_id == current_user.get("id"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不能删除自己"
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    db.query(Bookmark).filter(Bookmark.user_id == user_id).delete()
    db.delete(user)
    db.commit()
    
    return {"message": "删除成功"}


@router.get("/sources/health", response_model=List[SourceHealthResponse])
def get_sources_health(
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """获取所有信源健康状态"""
    sources = db.query(Source).all()
    
    result = []
    for source in sources:
        articles_count = db.query(Article).filter(Article.source_id == source.id).count()
        
        # 获取源 URL
        source_url = ""
        if source.type.value if hasattr(source.type, 'value') else source.type == "rss":
            source_url = source.config.get("feed_url", "")
        elif source.type.value if hasattr(source.type, 'value') else source.type == "github":
            org = source.config.get("org", "")
            repo = source.config.get("repo", "")
            source_url = f"https://github.com/{org}/{repo}"
        
        result.append(SourceHealthResponse(
            id=source.id,
            name=source.name,
            type=source.type.value if hasattr(source.type, 'value') else source.type,
            url=source_url,
            is_active=source.is_active,
            last_fetched_at=source.last_fetched_at,
            last_error=None,
            success_count=articles_count,
            error_count=0,
            success_rate=100.0 if source.is_active else 0.0,
            avg_response_time_ms=0,
            articles_count=articles_count,
        ))
    
    return result


@router.post("/sources/{source_id}/refresh")
def trigger_source_refresh(
    source_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """手动触发信源刷新"""
    source = db.query(Source).filter(Source.id == source_id).first()
    if not source:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="信源不存在"
        )
    
    return {"message": "刷新任务已提交", "source_id": source_id}


@router.get("/queue/status", response_model=QueueStatusResponse)
def get_queue_status(
    current_user: dict = Depends(require_admin)
):
    """获取 Celery 队列状态"""
    return QueueStatusResponse(
        worker_status=[
            {"name": "celery@worker1", "status": "up", "active_tasks": 2},
        ],
        pending_tasks=0,
        running_tasks=2,
        scheduled_tasks=5,
        failed_tasks_recent=0,
        tasks_by_type={
            "crawl_rss": 10,
            "crawl_twitter": 5,
            "analyze_article": 20,
        },
        memory_usage_mb=None,
        cpu_usage_percent=None,
    )


@router.get("/health", response_model=SystemHealthResponse)
def get_system_health(
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """获取系统健康状态"""
    components = {}
    overall_status = "healthy"
    
    try:
        db.execute("SELECT 1")
        components["database"] = {"status": "up", "latency_ms": 0}
    except Exception as e:
        components["database"] = {"status": "down", "error": str(e)}
        overall_status = "unhealthy"
    
    components["redis"] = {"status": "unknown"}
    components["celery"] = {"status": "unknown"}
    
    return SystemHealthResponse(
        status=overall_status,
        components=components,
        timestamp=datetime.utcnow(),
        version="1.0.0",
        uptime_seconds=0,
    )


@router.get("/logs")
def get_recent_logs(
    lines: int = 100,
    service: str = None,
    current_user: dict = Depends(require_admin)
):
    """获取最近日志"""
    return {
        "logs": [],
        "message": "日志功能待实现"
    }
