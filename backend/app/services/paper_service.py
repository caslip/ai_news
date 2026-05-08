"""论文数据访问层"""
from sqlalchemy.orm import Session
from app.models.paper import Paper
from app.models.source import Source
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


def save_paper(db: Session, source_id: str, paper_data: dict) -> bool:
    """
    保存论文到 Paper 表，去重逻辑：
    - 优先用 arxiv_id 或 hf_paper_id 匹配（同一信源内去重）
    - 其次用 content_hash 匹配（跨信源去重兜底）
    """
    try:
        arxiv_id = paper_data.get("arxiv_id")
        hf_paper_id = paper_data.get("hf_paper_id")
        content_hash = paper_data["content_hash"]

        query = db.query(Paper)

        if arxiv_id:
            existing = query.filter(
                Paper.arxiv_id == arxiv_id,
                Paper.source_id == source_id
            ).first()
        elif hf_paper_id:
            existing = query.filter(
                Paper.hf_paper_id == hf_paper_id,
                Paper.source_id == source_id
            ).first()
        else:
            existing = query.filter(Paper.content_hash == content_hash).first()

        if existing:
            return False

        paper = Paper(
            source_id=source_id,
            arxiv_id=arxiv_id or None,
            hf_paper_id=hf_paper_id or None,
            title=paper_data["title"],
            url=paper_data["url"],
            summary=paper_data.get("summary", ""),
            content_hash=content_hash,
            author=paper_data.get("author", ""),
            upvotes=paper_data.get("upvotes", 0) or 0,
            thumbnail_url=paper_data.get("thumbnail_url"),
            github_repo=paper_data.get("github_repo"),
            project_page=paper_data.get("project_page"),
            hf_url=paper_data.get("hf_url"),
            primary_category=paper_data.get("primary_category"),
            categories=paper_data.get("categories", []),
            tags=paper_data.get("tags", []),
            published_at=paper_data.get("published_at"),
            fetched_at=datetime.utcnow(),
        )

        db.add(paper)
        db.commit()
        return True

    except Exception as e:
        db.rollback()
        logger.error(f"save_paper failed: {e}")
        return False
