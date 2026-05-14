"""
AI Writer Templates Router
"""
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.models.writer import WriterTemplate
from app.news.schemas.user import UserResponse
from app.news.routers.auth import get_current_user
from app.writer.schemas.template import TemplateResponse, TemplateListResponse

router = APIRouter(prefix="/templates", tags=["写作模板"])


def seed_default_templates(db: Session) -> None:
    """
    Seed default templates if none exist
    """
    count = db.query(func.count(WriterTemplate.id)).scalar() or 0
    if count > 0:
        return
    
    default_templates = [
        {
            "name": "技术深度分析",
            "description": "深度解析技术原理、实现细节和行业影响",
            "category": "tech",
            "style": "technical",
            "tone": "professional",
            "length": "long",
        },
        {
            "name": "AI 资讯速递",
            "description": "快速传递 AI 领域最新动态和热点事件",
            "category": "news",
            "style": "news_analysis",
            "tone": "concise",
            "length": "medium",
        },
        {
            "name": "新手入门教程",
            "description": "面向初学者的详细操作指南",
            "category": "tech",
            "style": "tutorial",
            "tone": "casual",
            "length": "long",
        },
        {
            "name": "观点评论",
            "description": "表达个人见解和行业观点",
            "category": "tech",
            "style": "opinion",
            "tone": "storytelling",
            "length": "medium",
        },
        {
            "name": "产品体验报告",
            "description": "真实客观的产品使用体验分享",
            "category": "tech",
            "style": "product_review",
            "tone": "professional",
            "length": "medium",
        },
        {
            "name": "Twitter/X 快讯",
            "description": "简洁有力的短内容，适合社交媒体",
            "category": "social",
            "style": "news_analysis",
            "tone": "concise",
            "length": "short",
        },
        {
            "name": "小红书种草文",
            "description": "亲切分享风格，带互动引导",
            "category": "social",
            "style": "tutorial",
            "tone": "casual",
            "length": "medium",
        },
    ]
    
    for template_data in default_templates:
        template = WriterTemplate(**template_data)
        db.add(template)
    
    db.commit()


@router.get("/", response_model=TemplateListResponse)
def list_templates(
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
):
    """
    获取写作模板列表
    """
    # Ensure default templates exist
    seed_default_templates(db)
    
    templates = db.query(WriterTemplate).order_by(
        WriterTemplate.use_count.desc(),
        WriterTemplate.name
    ).all()
    
    return TemplateListResponse(
        items=[TemplateResponse.model_validate(t) for t in templates],
        total=len(templates),
    )
