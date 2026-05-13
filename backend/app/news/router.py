from fastapi import APIRouter
from app.news.routers import (
    auth, articles, sources, favorites, strategies,
    sse, monitor, admin, github,
)

router = APIRouter()

router.include_router(auth.router, prefix="/auth", tags=["认证"])
router.include_router(articles.router, prefix="/articles", tags=["文章"])
router.include_router(sources.router, prefix="/sources", tags=["信源"])
router.include_router(favorites.router, prefix="/favorites", tags=["收藏"])
router.include_router(strategies.router, prefix="/strategies", tags=["策略"])
router.include_router(sse.router, tags=["SSE实时推送"])
router.include_router(monitor.router, tags=["监控"])
router.include_router(admin.router, tags=["后台管理"])
router.include_router(github.router, prefix="/github", tags=["GitHub Trending"])
