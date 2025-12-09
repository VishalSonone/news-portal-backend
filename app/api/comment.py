from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.api.deps import get_db, get_current_user, require_roles, ensure_comment_delete_permission
from app.db import models
from app.schemas.comment import CommentCreate, CommentRead
from app.services.comment_service import (
    create_comment,
    get_comment,
    list_comments_for_article,
    delete_comment,
)
from app.services.article_service import get_article

router = APIRouter(prefix="/comments", tags=["comments"])


@router.post("/", response_model=CommentRead, status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(require_roles("reader", "author", "editor", "admin"))])
def create_new_comment(
    data: CommentCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    article = get_article(db, data.article_id)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    comment = create_comment(db, data, user_id=current_user.id)
    return comment


@router.get("/article/{article_id}", response_model=list[CommentRead])
def get_comments_for_article(article_id: str, db: Session = Depends(get_db)):
    comments = list_comments_for_article(db, article_id)
    return comments


@router.delete("/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_single_comment(
    comment_id: str,
    db: Session = Depends(get_db),
    comment = Depends(ensure_comment_delete_permission)
):
    delete_comment(db, comment)
    return None


@router.get("/me", response_model=list[CommentRead])
def get_my_comments(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    comments = (
        db.query(models.Comment)
        .options(joinedload(models.Comment.article))
        .filter(models.Comment.user_id == current_user.id)
        .order_by(models.Comment.created_at.desc())
        .all()
    )
    return comments
