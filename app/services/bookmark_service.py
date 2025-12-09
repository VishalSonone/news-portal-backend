from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from app.db import models
from app.schemas.bookmark import BookmarkCreate

def create_bookmark(db: Session, data: BookmarkCreate, user_id) -> models.Bookmark:
    bookmark = models.Bookmark(
        article_id=data.article_id,
        user_id=user_id,
    )
    db.add(bookmark)
    db.commit()
    db.refresh(bookmark)
    return bookmark

def get_bookmark_by_user_and_article(db: Session, user_id, article_id) -> Optional[models.Bookmark]:
    return db.query(models.Bookmark).filter(
        models.Bookmark.user_id == user_id,
        models.Bookmark.article_id == article_id
    ).first()

def list_bookmarks_for_user(db: Session, user_id) -> List[models.Bookmark]:
    return (
        db.query(models.Bookmark)
        .options(joinedload(models.Bookmark.article))
        .filter(models.Bookmark.user_id == user_id)
        .order_by(models.Bookmark.created_at.desc())
        .all()
    )

def delete_bookmark(db: Session, bookmark: models.Bookmark):
    db.delete(bookmark)
    db.commit()
