
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.schemas.media import MediaRead, MediaCreate
from app.services.media_service import (
    save_file_locally,
    create_media_record,
    delete_media,
    get_media,
)
from app.services.article_service import get_article

router = APIRouter(prefix="/media", tags=["media"])



@router.post("/upload", response_model=MediaRead, status_code=status.HTTP_201_CREATED)
def upload_media(
    article_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    # Validate article exists
    article = get_article(db, article_id)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    # User must be the author or admin
    if article.author_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to upload media for this article")

    # Save file
    file_url, mime_type, file_size = save_file_locally(file)

    # Create DB record
    data = MediaCreate(article_id=article_id)
    media = create_media_record(db, data, url=file_url, mime_type=mime_type, size=file_size)

    return media



@router.delete("/{media_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_media_file(
    media_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    media = get_media(db, media_id)
    if not media:
        raise HTTPException(status_code=404, detail="Media not found")

    # Only author or admin can delete
    article = get_article(db, media.article_id)
    if article.author_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to delete this media")

    delete_media(db, media)
    return None
