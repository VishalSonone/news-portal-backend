from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user, require_roles
from app.schemas.like import LikeCreate, LikeRead
from app.services.like_service import (
    create_like,
    get_like_by_user_and_article,
    remove_like,
)
from app.services.article_service import get_article

router = APIRouter(prefix="/likes", tags=["likes"])


@router.post("/", response_model=LikeRead, status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(require_roles("reader", "author", "editor", "admin"))])
def like_article(
    data: LikeCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    article = get_article(db, data.article_id)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    existing = get_like_by_user_and_article(db, current_user.id, data.article_id)
    if existing:
        raise HTTPException(status_code=400, detail="Already liked this article")
    like = create_like(db, data, current_user.id)
    return like


@router.delete("/{article_id}", status_code=status.HTTP_204_NO_CONTENT,
               dependencies=[Depends(require_roles("reader", "author", "editor", "admin"))])
def unlike_article(
    article_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    existing = get_like_by_user_and_article(db, current_user.id, article_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Like not found")
    remove_like(db, existing)
    return None
