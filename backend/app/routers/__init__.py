from app.routers.auth import router as auth_router
from app.routers.articles import router as articles_router
from app.routers.sources import router as sources_router
from app.routers.favorites import router as favorites_router
from app.routers.strategies import router as strategies_router
from app.routers.sse import router as sse_router
from app.routers.monitor import router as monitor_router
from app.routers.admin import router as admin_router

__all__ = [
    "auth_router",
    "articles_router",
    "sources_router",
    "favorites_router",
    "strategies_router",
    "sse_router",
    "monitor_router",
    "admin_router",
]
