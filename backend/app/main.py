from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.routers import auth, articles, sources, favorites, strategies, sse, monitor, admin, github

app = FastAPI(
    title="AI News API",
    version="1.0.0",
    description="AI News Aggregator - 自动抓取、分发与精选 AI 领域资讯",
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(auth.router, prefix="/api/auth", tags=["认证"])
app.include_router(articles.router, prefix="/api/articles", tags=["文章"])
app.include_router(sources.router, prefix="/api/sources", tags=["信源"])
app.include_router(favorites.router, prefix="/api/favorites", tags=["收藏"])
app.include_router(strategies.router, prefix="/api/strategies", tags=["策略"])
app.include_router(sse.router, prefix="/api", tags=["SSE实时推送"])
app.include_router(monitor.router, prefix="/api", tags=["监控"])
app.include_router(admin.router, prefix="/api", tags=["后台管理"])
app.include_router(github.router, prefix="/api/github", tags=["GitHub Trending"])


@app.get("/api/health")
def health_check():
    return {"status": "healthy", "version": "1.0.0"}


@app.get("/")
def root():
    return {
        "message": "AI News API",
        "docs": "/docs",
        "health": "/api/health",
    }
