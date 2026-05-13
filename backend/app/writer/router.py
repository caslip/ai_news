from fastapi import APIRouter
from app.writer.routers import content, agent

router = APIRouter()

router.include_router(content.router, tags=["写作内容"])
router.include_router(agent.router, tags=["写作Agent"])
