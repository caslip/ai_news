from pydantic import BaseModel
from typing import Optional


class AgentChatRequest(BaseModel):
    article_ids: list[str]
    prompt: str
    platform: str = "article"


class AgentChatResponse(BaseModel):
    content: str
    content_id: str
