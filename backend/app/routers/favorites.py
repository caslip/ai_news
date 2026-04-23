from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from uuid import UUID

from app.database import get_db
from app.models.bookmark import Bookmark, Tag
from app.models.article import Article
from app.schemas.user import UserResponse
from app.routers.auth import get_current_user

router = APIRouter()


@router.get("/")
def list_favorites(
    tag: Optional[str] = Query(None, description="标签过滤"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
):
    query = db.query(Bookmark).filter(Bookmark.user_id == UUID(current_user.id))

    if tag:
        query = query.join(Bookmark.tags).filter(Tag.name == tag)

    total = query.count()
    bookmarks = query.order_by(Bookmark.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()

    items = []
    for bm in bookmarks:
        article = bm.article
        items.append({
            "id": str(bm.id),
            "article_id": str(article.id),
            "article": {
                "id": str(article.id),
                "title": article.title,
                "url": article.url,
                "summary": article.summary,
                "author": article.author,
                "hot_score": article.hot_score,
                "tags": article.tags or [],
                "fetched_at": article.fetched_at.isoformat() if article.fetched_at else None,
            },
            "tags": [{"id": str(t.id), "name": t.name, "color": t.color} for t in bm.tags],
            "created_at": bm.created_at.isoformat(),
        })

    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.post("/", status_code=status.HTTP_201_CREATED)
def add_favorite(
    article_id: str,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
):
    article_uuid = UUID(article_id)
    
    existing = db.query(Bookmark).filter(
        Bookmark.user_id == UUID(current_user.id),
        Bookmark.article_id == article_uuid,
    ).first()
    
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Already bookmarked")

    bookmark = Bookmark(
        user_id=UUID(current_user.id),
        article_id=article_uuid,
    )
    db.add(bookmark)
    db.commit()
    db.refresh(bookmark)

    return {"id": str(bookmark.id), "message": "Added to favorites"}


@router.delete("/{bookmark_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_favorite(
    bookmark_id: UUID,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
):
    bookmark = db.query(Bookmark).filter(
        Bookmark.id == bookmark_id,
        Bookmark.user_id == UUID(current_user.id),
    ).first()

    if not bookmark:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bookmark not found")

    db.delete(bookmark)
    db.commit()


@router.post("/{bookmark_id}/tags")
def add_bookmark_tag(
    bookmark_id: UUID,
    tag_id: str,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
):
    bookmark = db.query(Bookmark).filter(
        Bookmark.id == bookmark_id,
        Bookmark.user_id == UUID(current_user.id),
    ).first()

    if not bookmark:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bookmark not found")

    tag = db.query(Tag).filter(Tag.id == UUID(tag_id)).first()
    if not tag:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found")

    if tag not in bookmark.tags:
        bookmark.tags.append(tag)
        db.commit()

    return {"message": "Tag added"}


@router.delete("/{bookmark_id}/tags/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_bookmark_tag(
    bookmark_id: UUID,
    tag_id: str,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
):
    bookmark = db.query(Bookmark).filter(
        Bookmark.id == bookmark_id,
        Bookmark.user_id == UUID(current_user.id),
    ).first()

    if not bookmark:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bookmark not found")

    tag = db.query(Tag).filter(Tag.id == UUID(tag_id)).first()
    if tag and tag in bookmark.tags:
        bookmark.tags.remove(tag)
        db.commit()


@router.get("/tags")
def list_tags(
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
):
    tags = db.query(Tag).filter(Tag.user_id == UUID(current_user.id)).all()
    return {"items": [{"id": str(t.id), "name": t.name, "color": t.color} for t in tags]}


@router.post("/tags", status_code=status.HTTP_201_CREATED)
def create_tag(
    name: str,
    color: str = "#6366f1",
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
):
    existing = db.query(Tag).filter(
        Tag.user_id == UUID(current_user.id),
        Tag.name == name,
    ).first()

    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Tag already exists")

    tag = Tag(
        user_id=UUID(current_user.id),
        name=name,
        color=color,
    )
    db.add(tag)
    db.commit()
    db.refresh(tag)

    return {"id": str(tag.id), "name": tag.name, "color": tag.color}


@router.delete("/tags/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_tag(
    tag_id: UUID,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
):
    tag = db.query(Tag).filter(
        Tag.id == tag_id,
        Tag.user_id == UUID(current_user.id),
    ).first()

    if not tag:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found")

    db.delete(tag)
    db.commit()
