"""
Streaming Chat API for AI Writer Floating Window.
Uses LangChain for LLM orchestration with DeepSeek support.
"""
import asyncio
import json
import logging
import time
import uuid
from typing import Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.news.schemas.user import UserResponse
from app.news.routers.auth import get_current_user
from app.services.llm_service import LLMService
from app.config import settings

router = APIRouter(prefix="/chat", tags=["AI 聊天"])
logger = logging.getLogger(__name__)

WRITER_SYSTEM_PROMPT = """你是一位专业的AI写作助手，擅长：
1. 回答关于写作、创作、内容策划的问题
2. 帮助用户分析和改写文章内容
3. 提供创意建议和灵感
4. 解释技术概念和行业趋势
5. 辅助从素材到成文的完整写作流程

请用友好、专业的语气回答。如果用户要求写作帮助，引导他们使用「文章生成」功能。
如果需要分析多篇文章，可以使用 /analyze 命令。
保持对话简洁有条理，适当使用 Markdown 格式。"""

# In-memory session storage (per-user, per-session)
# For production, use Redis
chat_sessions: dict[str, list[dict]] = {}


class ChatRequest(BaseModel):
    """Request model for chat endpoints."""
    session_id: Optional[str] = None
    message: str
    model: Optional[str] = None


class ChatResponse(BaseModel):
    """Response model for non-streaming chat."""
    session_id: str
    message: str
    error: Optional[str] = None


class SessionInfo(BaseModel):
    """Chat session info."""
    session_id: str
    title: str
    message_count: int
    created_at: Optional[float] = None


class SessionListResponse(BaseModel):
    """Response for listing sessions."""
    sessions: list[SessionInfo]


@router.get("/sessions", response_model=SessionListResponse)
def list_sessions(current_user: UserResponse = Depends(get_current_user)) -> SessionListResponse:
    """List all chat sessions for the current user."""
    user_id = current_user.id
    sessions = []
    for session_id, messages in chat_sessions.items():
        if session_id.startswith(user_id):
            first_msg = next((m for m in messages if m["role"] == "user"), None)
            title = first_msg["content"][:50] if first_msg else "新对话"
            created_at = messages[0].get("created_at") if messages else None
            sessions.append(SessionInfo(
                session_id=session_id,
                title=title,
                message_count=len([m for m in messages if m["role"] != "system"]),
                created_at=created_at,
            ))
    return SessionListResponse(sessions=sessions)


@router.post("/sessions")
def create_session(current_user: UserResponse = Depends(get_current_user)) -> dict:
    """Create a new chat session."""
    session_id = f"{current_user.id}_{uuid.uuid4().hex[:8]}"
    chat_sessions[session_id] = [
        {"role": "system", "content": WRITER_SYSTEM_PROMPT, "created_at": time.time()}
    ]
    return {"session_id": session_id}


@router.delete("/sessions/{session_id}")
def delete_session(
    session_id: str,
    current_user: UserResponse = Depends(get_current_user),
) -> dict:
    """Delete a chat session."""
    if session_id in chat_sessions and session_id.startswith(current_user.id):
        del chat_sessions[session_id]
    return {"status": "ok"}


@router.post("", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
):
    """
    Non-streaming chat — returns full response.
    """
    # Get or create session
    session_id = request.session_id
    if not session_id:
        session_id = f"{current_user.id}_{uuid.uuid4().hex[:8]}"
    
    if session_id not in chat_sessions:
        chat_sessions[session_id] = [
            {"role": "system", "content": WRITER_SYSTEM_PROMPT, "created_at": time.time()}
        ]
    
    # Append user message
    chat_sessions[session_id].append({
        "role": "user",
        "content": request.message,
        "created_at": time.time(),
    })
    
    # Call LLM
    model = request.model or settings.default_model
    llm = LLMService(model=model)
    
    try:
        response = await llm.ainvoke(chat_sessions[session_id])
        
        # Append assistant response
        chat_sessions[session_id].append({
            "role": "assistant",
            "content": response,
            "created_at": time.time(),
        })
        
        return ChatResponse(session_id=session_id, message=response)
    except Exception as e:
        logger.error(f"Chat error: {e}")
        return ChatResponse(
            session_id=session_id,
            message="",
            error=str(e),
        )


@router.post("/stream")
async def chat_stream(
    request: ChatRequest,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
):
    """
    Streaming chat — SSE response for real-time UI updates.
    """
    session_id = request.session_id
    if not session_id:
        session_id = f"{current_user.id}_{uuid.uuid4().hex[:8]}"
    
    if session_id not in chat_sessions:
        chat_sessions[session_id] = [
            {"role": "system", "content": WRITER_SYSTEM_PROMPT, "created_at": time.time()}
        ]
    
    chat_sessions[session_id].append({
        "role": "user",
        "content": request.message,
        "created_at": time.time(),
    })
    
    model = request.model or settings.default_model
    llm = LLMService(model=model)
    
    async def event_generator():
        full_response = ""
        try:
            async for chunk in llm.astream(chat_sessions[session_id]):
                if chunk:
                    full_response += chunk
                    yield {
                        "event": "message",
                        "data": json.dumps({"content": chunk, "done": False}),
                    }
                    # Small delay for smoother streaming feel
                    await asyncio.sleep(0.01)
            
            # Save complete response
            chat_sessions[session_id].append({
                "role": "assistant",
                "content": full_response,
                "created_at": time.time(),
            })
            
            yield {
                "event": "done",
                "data": json.dumps({"session_id": session_id, "done": True}),
            }
            
        except Exception as e:
            logger.error(f"Stream error: {e}")
            yield {
                "event": "error",
                "data": json.dumps({"error": str(e)}),
            }
    
    return EventSourceResponse(event_generator())


@router.get("/history/{session_id}")
def get_history(
    session_id: str,
    current_user: UserResponse = Depends(get_current_user),
) -> dict:
    """Get chat history for a session."""
    if session_id not in chat_sessions:
        return {"messages": []}
    # Only return non-system messages to frontend
    messages = [m for m in chat_sessions[session_id] if m["role"] != "system"]
    return {"messages": messages}


@router.post("/generate")
async def chat_to_generate(
    request: ChatRequest,
    current_user: UserResponse = Depends(get_current_user),
):
    """
    Take chat context and generate a full article from it.
    This bridges chat → writing by using the chat context as source material.
    """
    from app.writer.routers.generate import generate_content_core
    from app.writer.schemas.draft import GenerateRequest
    
    # Build source content from recent chat messages
    session_id = request.session_id or ""
    if session_id and session_id in chat_sessions:
        recent = chat_sessions[session_id][-6:]  # Last 6 messages
        source = "\n\n".join(
            f"[{m['role']}]: {m['content']}" 
            for m in recent 
            if m["role"] != "system"
        )
    else:
        source = request.message
    
    # Extract style/tone from message if provided
    style = "technical"
    tone = "professional"
    if "教程" in request.message or "tutorial" in request.message.lower():
        style = "tutorial"
    elif "评测" in request.message or "review" in request.message.lower():
        style = "product_review"
    elif "分析" in request.message:
        style = "news_analysis"
    
    gen_request = GenerateRequest(
        source_content=source,
        topic=request.message[:100],
        style=style,
        tone=tone,
        length="medium",
    )
    
    # Call the core generation function
    title, content, word_count = await generate_content_core(
        source_content=gen_request.source_content,
        style=gen_request.style,
        tone=gen_request.tone,
        length=gen_request.length,
        topic=gen_request.topic,
    )
    
    return {
        "title": title,
        "content": content,
        "word_count": word_count,
        "session_id": session_id,
    }
