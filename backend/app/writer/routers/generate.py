"""
AI Writer Generate Router - Async content generation with LLM
Uses LangChain for unified LLM interaction.
"""
import re
import logging
from typing import Optional
import httpx

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from bs4 import BeautifulSoup

from app.database import get_db
from app.models.draft import Draft
from app.models.writer import WriterTemplate
from app.news.schemas.user import UserResponse
from app.news.routers.auth import get_current_user
from app.writer.schemas.draft import GenerateRequest, GenerateResponse
from app.services.llm_service import LLMService
from app.config import settings

router = APIRouter(prefix="/generate", tags=["内容生成"])

logger = logging.getLogger(__name__)

# Length to word count mapping
LENGTH_CONFIG = {
    "short": {"min_words": 200, "max_words": 500, "description": "短内容 (~500字)"},
    "medium": {"min_words": 800, "max_words": 1500, "description": "中等长度 (~1500字)"},
    "long": {"min_words": 2000, "max_words": 3000, "description": "长内容 (~3000字)"},
}

# Style descriptions for prompts
STYLE_PROMPTS = {
    "technical": "深入技术细节，包含实现原理、代码示例和技术分析",
    "news_analysis": "新闻分析风格，分析事件背景、行业影响和未来趋势",
    "tutorial": "教程风格，步骤清晰，适合学习和实践",
    "opinion": "观点表达风格，有立场、有分析、有见解",
    "product_review": "产品评测风格，客观描述、优缺点分析、适用场景",
}

# Tone descriptions for prompts
TONE_PROMPTS = {
    "professional": "专业严谨，使用行业术语，逻辑清晰",
    "casual": "轻松随意，口语化表达，亲切友好",
    "concise": "简洁精炼，直击要点，不啰嗦",
    "storytelling": "故事化叙述，有代入感，情感丰富",
}


def extract_text_from_html(html: str) -> str:
    """Extract plain text from HTML content"""
    if not html:
        return ""
    soup = BeautifulSoup(html, "html.parser")
    
    # Remove script and style elements
    for element in soup(["script", "style"]):
        element.decompose()
    
    # Get text
    text = soup.get_text(separator="\n")
    
    # Clean up whitespace
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    return "\n".join(lines)[:10000]  # Limit to 10000 chars


async def fetch_url_content(url: str) -> str:
    """Fetch and extract content from a URL"""
    try:
        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
            response = await client.get(url)
            response.raise_for_status()
            
            content_type = response.headers.get("content-type", "")
            if "text/html" in content_type:
                return extract_text_from_html(response.text)
            else:
                return response.text[:10000]
    except httpx.HTTPError as e:
        logger.warning(f"Failed to fetch URL {url}: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"无法获取URL内容: {str(e)}"
        )


def extract_title_from_response(content: str) -> tuple[str, str]:
    """
    Extract title from LLM response.
    Returns (title, content_without_title)
    """
    if not content:
        return "Untitled", ""
    
    # Try # Title format first
    match = re.search(r'^#\s+(.+)$', content.strip(), re.MULTILINE)
    if match:
        title = match.group(1).strip()
        # Remove the title line from content
        remaining = re.sub(r'^#\s+.+$\n?', '', content.strip(), count=1, flags=re.MULTILINE)
        return title, remaining.strip()
    
    # Try first non-empty line
    lines = content.strip().split('\n')
    for i, line in enumerate(lines):
        line = line.strip()
        if line and not line.startswith(('#', '*', '-', '>', '|', '=', '```')):
            # Clean up the title
            title = re.sub(r'^[#*\-\s]+', '', line)
            if 5 <= len(title) <= 100:
                return title, '\n'.join(lines[i+1:]).strip()
    
    return "Untitled", content.strip()


def build_generation_prompt(
    source_content: str,
    style: str,
    tone: str,
    length: str,
    topic: Optional[str] = None,
) -> str:
    """Build the full prompt for content generation"""
    
    length_info = LENGTH_CONFIG.get(length, LENGTH_CONFIG["medium"])
    style_desc = STYLE_PROMPTS.get(style, "")
    tone_desc = TONE_PROMPTS.get(tone, "")
    
    system_prompt = """你是一位专业的AI技术自媒体写手，擅长撰写高质量的技术文章。

## 写作要求
1. **长度**: {}，目标{}-{}字

2. **风格**: {}

3. **语气**: {}

4. **格式要求**:
   - 标题简洁有力，吸引读者
   - 使用Markdown格式（# 标题、## 小标题、- 列表等）
   - 段落之间适当留白
   - 关键信息加粗或用emoji标记

5. **内容要求**:
   - 开头有吸引力的引言或问题
   - 逻辑清晰，层层递进
   - 有独到见解和分析，不只是堆砌信息
   - 结尾有总结或展望

请直接输出文章内容，不需要额外说明。""".format(
        length_info['description'],
        length_info['min_words'],
        length_info['max_words'],
        style_desc,
        tone_desc,
    )
    
    user_content = f"""## 素材内容

{source_content}

---
{f"## 主题要求: {topic}" if topic else ""}
请基于以上素材，生成一篇吸引人的文章。"""
    
    return f"<system>\n{system_prompt}\n</system>\n\n<user>\n{user_content}\n</user>"


async def generate_content_core(
    source_content: str,
    style: str,
    tone: str,
    length: str,
    topic: Optional[str] = None,
    model: Optional[str] = None,
    user_id: Optional[str] = None,
) -> tuple[str, str, int]:
    """
    Core generation logic using LangChain LLMService.
    Returns (title, content, word_count).
    
    This function is reusable by both the generate endpoint and chat router.
    """
    prompt = build_generation_prompt(source_content, style, tone, length, topic)
    model = model or settings.default_model
    
    # Use provider-based initialization when no specific model is given
    # Pass user_id to fetch user-specific API key from database
    if model == settings.default_model:
        llm = LLMService(provider=settings.effective_llm_provider, user_id=user_id)
    else:
        llm = LLMService(model=model, user_id=user_id)
    
    generated_text = await llm.ainvoke([
        {"role": "user", "content": prompt}
    ])
    
    title, content = extract_title_from_response(generated_text)
    word_count = len(content.split())
    
    logger.info(f"Content generated: title='{title}', words={word_count}")
    return title, content, word_count


@router.post("", response_model=GenerateResponse)
async def generate_content(
    request: GenerateRequest,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
):
    """
    生成 AI 写作内容
    
    支持两种来源:
    - source_url: 从 URL 抓取内容
    - source_content: 直接提供内容
    
    生成过程:
    1. 创建草稿 (status=generating)
    2. 获取/构建素材内容
    3. 调用 LLM 生成
    4. 更新草稿状态和内容
    """
    # Determine source content
    source_content = ""
    
    if request.source_url:
        try:
            source_content = await fetch_url_content(request.source_url)
        except HTTPException:
            # Create failed draft if URL fetch fails
            draft = Draft(
                title="Failed",
                content="",
                status="failed",
                style=request.style,
                tone=request.tone,
                length=request.length,
                source_url=request.source_url,
                error_message="Failed to fetch source URL",
                created_by=current_user.id,
            )
            db.add(draft)
            db.commit()
            db.refresh(draft)
            
            return GenerateResponse(
                id=draft.id,
                status="failed",
                error_message="Failed to fetch source URL",
            )
    
    if request.source_content:
        source_content = request.source_content
    
    if not source_content:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either source_url or source_content must be provided"
        )
    
    # Create draft with generating status
    draft = Draft(
        title="Generating...",
        content="",
        status="generating",
        style=request.style,
        tone=request.tone,
        length=request.length,
        source_url=request.source_url,
        source_content=source_content if len(source_content) <= 5000 else source_content[:5000] + "...",
        created_by=current_user.id,
    )
    db.add(draft)
    db.commit()
    db.refresh(draft)
    
    try:
        # Build prompt and call LLM using LangChain
        title, content, word_count = await generate_content_core(
            source_content=source_content,
            style=request.style,
            tone=request.tone,
            length=request.length,
            topic=request.topic,
            user_id=current_user.id,
        )
        
        # Update draft
        draft.title = title
        draft.content = content
        draft.word_count = word_count
        draft.status = "completed"
        draft.error_message = None
        
        db.commit()
        db.refresh(draft)
        
        return GenerateResponse(
            id=draft.id,
            status="completed",
            content=content,
            title=title,
            word_count=word_count,
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions
        db.rollback()
        raise
    except Exception as e:
        logger.error(f"Generation error: {e}")
        
        # Update draft with error
        draft.status = "failed"
        draft.error_message = str(e)
        db.commit()
        db.refresh(draft)
        
        return GenerateResponse(
            id=draft.id,
            status="failed",
            error_message=str(e),
        )
