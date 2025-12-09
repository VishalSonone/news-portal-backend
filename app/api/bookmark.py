from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.api.deps import get_db, get_current_user
from app.schemas.bookmark import BookmarkCreate, BookmarkRead
from app.services.bookmark_service import (
    create_bookmark,
    get_bookmark_by_user_and_article,
    list_bookmarks_for_user,
    delete_bookmark,
)
from app.services.article_service import get_article

router = APIRouter(prefix="/bookmarks", tags=["bookmarks"])

@router.post("/", response_model=BookmarkRead, status_code=status.HTTP_201_CREATED)
def save_article(
    data: BookmarkCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    article = get_article(db, data.article_id)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    
    existing = get_bookmark_by_user_and_article(db, current_user.id, data.article_id)
    if existing:
        raise HTTPException(status_code=400, detail="Article already saved")
        
    bookmark = create_bookmark(db, data, user_id=current_user.id)
    return bookmark

@router.get("/", response_model=List[BookmarkRead])
def get_my_bookmarks(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    bookmarks = list_bookmarks_for_user(db, current_user.id)
    return bookmarks

@router.delete("/{article_id}", status_code=status.HTTP_204_NO_CONTENT)
def unsave_article(
    article_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    bookmark = get_bookmark_by_user_and_article(db, current_user.id, article_id)
    if not bookmark:
        raise HTTPException(status_code=404, detail="Bookmark not found")
        
    delete_bookmark(db, bookmark)
    return None
