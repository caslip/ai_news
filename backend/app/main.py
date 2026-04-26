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


@app.on_event("startup")
async def startup_event():
    """应用启动时一次性爬取所有信源（静默失败，不阻塞启动）"""
    import logging
    import threading

    logger = logging.getLogger(__name__)
    logger.info("Application starting, triggering initial crawl tasks...")

    def submit_crawl_tasks():
        """在新线程中提交爬取任务，不阻塞主线程"""
        import time
        time.sleep(1)  # 等待应用完全启动
        tasks = [
            ("crawl_rss_sources", "app.services.celery_tasks.crawl_rss_sources"),
            ("crawl_nitter_sources", "app.services.celery_tasks.crawl_nitter_sources"),
            ("crawl_twitter_sources", "app.services.celery_tasks.crawl_twitter_sources"),
            ("crawl_github_sources", "app.services.celery_tasks.crawl_github_sources"),
        ]
        for name, path in tasks:
            try:
                import importlib
                module_path, func_name = path.rsplit(".", 1)
                mod = importlib.import_module(module_path)
                func = getattr(mod, func_name)
                func.delay()
                logger.info(f"Submitted {name} successfully")
            except Exception as e:
                logger.warning(f"Failed to submit {name} (Redis may be unavailable): {e}")

    thread = threading.Thread(target=submit_crawl_tasks, daemon=True)
    thread.start()
    logger.info("Crawl tasks thread started")


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
