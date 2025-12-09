
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db import models
from app.schemas.comment import CommentCreate


def create_comment(db: Session, data: CommentCreate, user_id) -> models.Comment:
    comment = models.Comment(
        content=data.content,
        article_id=data.article_id,
        user_id=user_id,
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment


def get_comment(db: Session, comment_id) -> Optional[models.Comment]:
    return db.query(models.Comment).filter(models.Comment.id == comment_id).first()


def list_comments_for_article(db: Session, article_id) -> List[models.Comment]:
    return (
        db.query(models.Comment)
        .filter(models.Comment.article_id == article_id)
        .order_by(models.Comment.created_at.asc())
        .all()
    )


def delete_comment(db: Session, comment: models.Comment):
    db.delete(comment)
    db.commit()
