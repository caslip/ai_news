from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import Optional
import uuid
from app.models.article import Article
from app.models.source import Source
from app.schemas.article import ArticleCreate, ArticleUpdate, ArticleListResponse


class ArticleService:
    def __init__(self, db: Session):
        self.db = db

    def list_articles(
        self,
        page: int = 1,
        page_size: int = 20,
        source_id: Optional[str] = None,
        category: Optional[str] = None,
        is_featured: Optional[bool] = None,
        is_trending: Optional[bool] = None,
    ) -> ArticleListResponse:
        query = self.db.query(Article)

        if source_id:
            query = query.filter(Article.source_id == source_id)
        if is_featured is not None:
            query = query.filter(Article.is_featured == is_featured)
        if is_trending is not None:
            query = query.filter(Article.is_trending == is_trending)

        total = query.count()
        items = (
            query
            .order_by(desc(Article.published_at))
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )

        return ArticleListResponse(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
        )

    def get_article(self, article_id: str) -> Optional[Article]:
        article = self.db.query(Article).filter(Article.id == article_id).first()
        if article:
            article.view_count += 1
            self.db.commit()
        return article

    def create_article(self, article_data: ArticleCreate) -> Article:
        existing = self.db.query(Article).filter(Article.url == article_data.url).first()
        if existing:
            return existing

        db_article = Article(id=str(uuid.uuid4()), **article_data.model_dump())
        self.db.add(db_article)
        self.db.commit()
        self.db.refresh(db_article)
        return db_article

    def update_article(self, article_id: str, article_data: ArticleUpdate) -> Optional[Article]:
        article = self.db.query(Article).filter(Article.id == article_id).first()
        if not article:
            return None
        for key, value in article_data.model_dump(exclude_unset=True).items():
            setattr(article, key, value)
        self.db.commit()
        self.db.refresh(article)
        return article

    def delete_article(self, article_id: str) -> bool:
        article = self.db.query(Article).filter(Article.id == article_id).first()
        if not article:
            return False
        self.db.delete(article)
        self.db.commit()
        return True
