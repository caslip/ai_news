from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.config import settings
from app.news.router import router as news_router
from app.writer.router import router as writer_router
from app.papers import router as papers_router
from app.logging_config import setup_logging
from app.middleware import RequestLoggingMiddleware
from app.logging.router import router as logging_router

# 初始化日志配置
setup_logging(service_name="ai-news-backend", service_type="api")

@asynccontextmanager
async def lifespan(app: FastAPI):
    import logging
    logger = logging.getLogger(__name__)
    logger.info("Application starting, starting scheduler...")

    from app.database import init_db
    init_db()
    logger.info("Database tables initialized")

    from app.services.scheduler import start_scheduler, crawl_all_sources

    start_scheduler()
    logger.info("Scheduler started with hourly crawl")
    crawl_all_sources()
    logger.info("Initial crawl triggered")

    yield

    logger = logging.getLogger(__name__)
    from app.services.scheduler import stop_scheduler
    stop_scheduler()
    logger.info("Application shutting down, scheduler stopped")


app = FastAPI(
    title="AI News API",
    version="1.0.0",
    description="AI News Aggregator - 自动抓取、分发与精选 AI 领域资讯",
    lifespan=lifespan,
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
app.include_router(papers_router, prefix="/api/papers", tags=["论文"])
app.include_router(logging_router, prefix="/api")

# 添加请求日志中间件
app.add_middleware(RequestLoggingMiddleware)


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
