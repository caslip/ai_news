from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.news.router import router as news_router
from app.writer.router import router as writer_router
from app import papers
from app.logging_config import setup_logging
from app.middleware import RequestLoggingMiddleware
from app.logging.router import router as logging_router

# 初始化日志配置
setup_logging(service_name="ai-news-backend", service_type="api")

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
app.include_router(news_router, prefix="/api")
app.include_router(writer_router, prefix="/api/writer")
app.include_router(papers.router, prefix="/api/papers", tags=["论文"])
app.include_router(logging_router, prefix="/api")

# 添加请求日志中间件
app.add_middleware(RequestLoggingMiddleware)


@app.on_event("startup")
async def startup_event():
    """应用启动时启动定时调度器"""
    import logging

    logger = logging.getLogger(__name__)
    logger.info("Application starting, starting scheduler...")

    from app.services.scheduler import start_scheduler, crawl_all_sources

    start_scheduler()
    logger.info("Scheduler started with hourly crawl")

    # 启动后立即执行一次全量爬取
    crawl_all_sources()
    logger.info("Initial crawl triggered")


@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭时停止调度器"""
    import logging
    logger = logging.getLogger(__name__)
    from app.services.scheduler import stop_scheduler
    stop_scheduler()
    logger.info("Application shutting down, scheduler stopped")


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
