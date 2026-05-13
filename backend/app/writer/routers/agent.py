"""
AI 写作助手 Agent 路由 - 调用 LLM 基于多篇文章生成内容
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.article import Article
from app.news.schemas.user import UserResponse
from app.news.routers.auth import get_current_user
from app.writer.schemas.agent import AgentChatRequest, AgentChatResponse
from app.writer.schemas.content import ContentCreate, ContentResponse
from app.writer.routers.content import create_content
from app.writer.prompts import SYSTEM_PROMPTS

router = APIRouter(prefix="/agent", tags=["写作Agent"])


def build_prompt(platform: str, articles: list[Article], custom_prompt: str) -> str:
    """构建发送给 LLM 的完整提示词"""
    system = SYSTEM_PROMPTS.get(platform, SYSTEM_PROMPTS["article"])
    custom = f"\n\n用户额外要求：{custom_prompt}" if custom_prompt else ""

    articles_text = "\n\n".join(
        f"--- 文章 {i+1}: {a.title} ---\n{a.summary or a.content or '(无正文)'}"
        for i, a in enumerate(articles)
    )

    return f"{system}\n\n{articles_text}{custom}"


@router.post("/chat", response_model=AgentChatResponse)
def chat(
    data: AgentChatRequest,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
):
    """
    基于多篇文章和提示词，让 AI 生成一篇完整内容。
    先从数据库加载文章，再拼接提示词发送给 LLM，最后保存到 generated_content 表。
    """
    articles = db.query(Article).filter(
        Article.id.in_(data.article_ids)
    ).all()

    if not articles:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="未找到任何文章",
        )

    # 按 id 顺序对齐
    id_order = {aid: i for i, aid in enumerate(data.article_ids)}
    articles.sort(key=lambda a: id_order.get(a.id, 0))

    prompt = build_prompt(data.platform, articles, data.prompt)

    # 调用 LLM（简单实现：直接从 settings 读取）
    from app.config import settings
    from openai import OpenAI

    client = OpenAI(api_key=settings.openai_api_key)
    response = client.chat.completions.create(
        model=settings.openai_model or "gpt-4o",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPTS.get(data.platform, SYSTEM_PROMPTS["article"])},
            {"role": "user", "content": prompt},
        ],
        temperature=0.7,
    )

    generated_text = response.choices[0].message.content

    # 保存内容
    content_data = ContentCreate(
        source_article_ids=data.article_ids,
        source_article_titles=[a.title for a in articles],
        content=generated_text,
        platform=data.platform,
        prompt=data.prompt,
    )
    saved = create_content(content_data, db, current_user)

    return AgentChatResponse(
        content=generated_text,
        content_id=saved.id,
    )
