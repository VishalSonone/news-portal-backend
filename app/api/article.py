from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.schemas.article import ArticleCreate, ArticleRead, ArticleUpdate
from app.services.article_service import (
    create_article,
    get_article,
    list_articles,
    update_article,
    delete_article,
    get_article_by_slug,
)
from app.db import models

router = APIRouter(prefix="/articles", tags=["articles"])




@router.post("/", response_model=ArticleRead, status_code=status.HTTP_201_CREATED)
def create_new_article(
    data: ArticleCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    # Check if slug already exists
    if get_article_by_slug(db, data.slug):
        raise HTTPException(status_code=400, detail="Slug already exists")

    article = create_article(db, data, author_id=current_user.id)
    return article



@router.get("/", response_model=list[ArticleRead])
def list_all_articles(db: Session = Depends(get_db)):
    return list_articles(db)



@router.get("/{article_id}", response_model=ArticleRead)
def get_single_article(article_id: str, db: Session = Depends(get_db)):
    article = get_article(db, article_id)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    return article




@router.put("/{article_id}", response_model=ArticleRead)
def update_single_article(
    article_id: str,
    data: ArticleUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    article = get_article(db, article_id)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    # Only the author or an editor/admin can update
    if article.author_id != current_user.id and current_user.role not in ["editor", "admin"]:
        raise HTTPException(status_code=403, detail="Not authorized to update this article")

    updated_article = update_article(db, article, data)
    return updated_article



@router.delete("/{article_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_single_article(
    article_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    article = get_article(db, article_id)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    # Only the author or admin can delete
    if article.author_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to delete this article")

    delete_article(db, article)
    return None