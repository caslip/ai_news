"""
知乎问题爬取服务 - 负责存储/去重/更新知乎问题
"""

import hashlib
import json
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import Optional
from sqlalchemy.orm import Session

from app.models.zhihu_question import ZhihuQuestion


@dataclass
class ZhihuQuestionData:
    """知乎问题数据结构"""
    zhihu_id: str
    title: str
    excerpt: str = ""
    answer_count: int = 0
    follower_count: int = 0
    view_count: int = 0
    tags: list[str] = None
    label: str = "recommend"  # surging | new | recommend
    author_name: str = ""
    author_url: str = ""
    url: str = ""
    content_hash: str = ""
    raw_metadata: dict = None

    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        if self.raw_metadata is None:
            self.raw_metadata = {}

    @classmethod
    def from_dict(cls, data: dict) -> "ZhihuQuestionData":
        return cls(
            zhihu_id=data.get("zhihu_id", ""),
            title=data.get("title", ""),
            excerpt=data.get("excerpt", ""),
            answer_count=int(data.get("answer_count", 0)),
            follower_count=int(data.get("follower_count", 0)),
            view_count=int(data.get("view_count", 0)),
            tags=data.get("tags", []),
            label=data.get("label", "recommend"),
            author_name=data.get("author_name", ""),
            author_url=data.get("author_url", ""),
            url=data.get("url", ""),
            content_hash=data.get("content_hash", ""),
            raw_metadata=data.get("raw_metadata", {}),
        )

    def to_dict(self) -> dict:
        return asdict(self)

    def generate_hash(self) -> str:
        """生成内容哈希用于去重"""
        content = f"{self.zhihu_id}:{self.title}"
        return hashlib.sha256(content.encode()).hexdigest()


class ZhihuCrawlerService:
    """知乎问题爬取服务"""

    def __init__(self, db: Session):
        self.db = db

    def save_questions(self, questions: list[dict]) -> dict:
        """
        批量保存/去重/更新问题

        Args:
            questions: 问题数据列表

        Returns:
            dict: {"created": int, "updated": int, "skipped": int, "total": int}
        """
        created = 0
        updated = 0
        skipped = 0

        for q_data in questions:
            try:
                question_data = ZhihuQuestionData.from_dict(q_data)

                if not question_data.zhihu_id:
                    skipped += 1
                    continue

                if not question_data.content_hash:
                    question_data.content_hash = question_data.generate_hash()

                existing = self.db.query(ZhihuQuestion).filter(
                    ZhihuQuestion.zhihu_id == question_data.zhihu_id
                ).first()

                if existing:
                    changed = False

                    if question_data.title and question_data.title != existing.title:
                        existing.title = question_data.title
                        changed = True

                    if question_data.excerpt and question_data.excerpt != existing.excerpt:
                        existing.excerpt = question_data.excerpt
                        changed = True

                    if question_data.answer_count != existing.answer_count:
                        existing.answer_count = question_data.answer_count
                        changed = True

                    if question_data.follower_count != existing.follower_count:
                        existing.follower_count = question_data.follower_count
                        changed = True

                    if question_data.view_count != existing.view_count:
                        existing.view_count = question_data.view_count
                        changed = True

                    if question_data.tags:
                        existing.tags = question_data.tags
                        changed = True

                    if question_data.raw_metadata:
                        existing.raw_metadata = question_data.raw_metadata
                        changed = True

                    if changed:
                        existing.updated_at = datetime.utcnow()
                        existing.fetched_at = datetime.utcnow()
                        updated += 1
                    else:
                        skipped += 1
                else:
                    new_question = ZhihuQuestion(
                        zhihu_id=question_data.zhihu_id,
                        title=question_data.title,
                        excerpt=question_data.excerpt,
                        answer_count=question_data.answer_count,
                        follower_count=question_data.follower_count,
                        view_count=question_data.view_count,
                        tags=question_data.tags,
                        label=question_data.label,
                        author_name=question_data.author_name,
                        author_url=question_data.author_url,
                        url=question_data.url,
                        content_hash=question_data.content_hash,
                        raw_metadata=question_data.raw_metadata,
                        fetched_at=datetime.utcnow(),
                    )
                    self.db.add(new_question)
                    created += 1

            except Exception as e:
                skipped += 1
                continue

        self.db.commit()

        return {
            "created": created,
            "updated": updated,
            "skipped": skipped,
            "total": len(questions),
        }

    def get_questions(
        self,
        label: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[ZhihuQuestion], int]:
        """
        查询问题列表

        Args:
            label: 标签过滤 (surging/new/recommend)
            page: 页码
            page_size: 每页数量

        Returns:
            tuple[list[ZhihuQuestion], int]: (问题列表, 总数)
        """
        query = self.db.query(ZhihuQuestion)

        if label:
            query = query.filter(ZhihuQuestion.label == label)

        total = query.count()
        questions = (
            query
            .order_by(ZhihuQuestion.fetched_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )

        return questions, total

    def get_question_by_id(self, question_id: str) -> Optional[ZhihuQuestion]:
        """根据 ID 获取问题"""
        return self.db.query(ZhihuQuestion).filter(
            ZhihuQuestion.id == question_id
        ).first()

    def delete_question(self, question_id: str) -> bool:
        """删除问题"""
        question = self.get_question_by_id(question_id)
        if question:
            self.db.delete(question)
            self.db.commit()
            return True
        return False

    def get_last_fetch_time(self) -> Optional[datetime]:
        """获取最后抓取时间"""
        latest = (
            self.db.query(ZhihuQuestion)
            .order_by(ZhihuQuestion.fetched_at.desc())
            .first()
        )
        return latest.fetched_at if latest else None

    def get_stats(self) -> dict:
        """获取统计信息"""
        from sqlalchemy import func

        total = self.db.query(func.count(ZhihuQuestion.id)).scalar() or 0
        surging = self.db.query(func.count(ZhihuQuestion.id)).filter(
            ZhihuQuestion.label == "surging"
        ).scalar() or 0
        new_q = self.db.query(func.count(ZhihuQuestion.id)).filter(
            ZhihuQuestion.label == "new"
        ).scalar() or 0
        recommend = self.db.query(func.count(ZhihuQuestion.id)).filter(
            ZhihuQuestion.label == "recommend"
        ).scalar() or 0

        last_fetch = self.get_last_fetch_time()

        return {
            "total": total,
            "surging": surging,
            "new": new_q,
            "recommend": recommend,
            "last_fetch_at": last_fetch.isoformat() if last_fetch else None,
        }
