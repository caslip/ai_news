from fastapi import APIRouter
from app.writer.routers import content, agent, drafts, templates, generate, chat

router = APIRouter()

router.include_router(content.router, tags=["写作内容"])
router.include_router(agent.router, tags=["写作Agent"])
router.include_router(drafts.router, tags=["写作草稿"])
router.include_router(templates.router, tags=["写作模板"])
router.include_router(generate.router, tags=["内容生成"])
router.include_router(chat.router, tags=["AI 聊天"])
