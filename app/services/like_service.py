from sqlalchemy.orm import Session
from typing import Optional
from app.db import models
from app.schemas.like import LikeCreate



def create_like(db: Session, data: LikeCreate, user_id):
    """Create a like if it doesn't exist (enforced by DB unique constraint)."""
    like = models.Like(
        article_id=data.article_id,
        user_id=user_id,
    )
    db.add(like)

    # increase like count on Article
    article = db.query(models.Article).filter(models.Article.id == data.article_id).first()
    if article:
        article.likes_count += 1

    db.commit()
    db.refresh(like)
    return like



def get_like(db: Session, like_id) -> Optional[models.Like]:
    return db.query(models.Like).filter(models.Like.id == like_id).first()



def get_like_by_user_and_article(db: Session, user_id, article_id) -> Optional[models.Like]:
    return (
        db.query(models.Like)
        .filter(models.Like.user_id == user_id, models.Like.article_id == article_id)
        .first()
    )



def remove_like(db: Session, like: models.Like):
    """Remove like and decrease article counter."""
    article = db.query(models.Article).filter(models.Article.id == like.article_id).first()
    if article and article.likes_count > 0:
        article.likes_count -= 1

    db.delete(like)
    db.commit()
