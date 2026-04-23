"""
SSE 实时推送 API 路由
"""

from fastapi import APIRouter, Request
from app.services.sse import router as sse_router

# 重新导出 SSE 路由
router = sse_router
