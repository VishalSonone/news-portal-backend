import os
import uuid
from typing import Optional
from fastapi import UploadFile, HTTPException
from sqlalchemy.orm import Session
from app.db import models
from app.schemas.media import MediaCreate

# Allowed MIME types
ALLOWED_IMAGE_TYPES = {
    "image/jpeg",
    "image/jpg",
    "image/png",
    "image/webp",
}


UPLOAD_DIR = "uploads/media"


os.makedirs(UPLOAD_DIR, exist_ok=True)


def save_file_locally(file: UploadFile) -> tuple[str, str, int]:
    """
    Save file in local uploads folder.
    Returns: (file_url, mime_type, file_size)
    """
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(status_code=400, detail="Invalid image type")

    # Generate unique filename
    ext = file.filename.split(".")[-1].lower()
    unique_name = f"{uuid.uuid4()}.{ext}"

    file_path = os.path.join(UPLOAD_DIR, unique_name)

    # Save file
    with open(file_path, "wb") as f:
        content = file.file.read()
        f.write(content)

    file_size = len(content)

    # Build URL (we will serve /media as static)
    file_url = f"/media/{unique_name}"

    return file_url, file.content_type, file_size


def create_media_record(
    db: Session, data: MediaCreate, url: str, mime_type: str, size: int
) -> models.Media:
    media = models.Media(
        article_id=data.article_id,
        url=url,
        mime_type=mime_type,
        size=size,
    )
    db.add(media)
    db.commit()
    db.refresh(media)
    return media



def delete_media(db: Session, media: models.Media):
    """
    Delete file from disk + remove DB record.
    """
    # Remove file from disk
    file_path = f"uploads/media/{os.path.basename(media.url)}"
    if os.path.exists(file_path):
        os.remove(file_path)

    # Delete DB record
    db.delete(media)
    db.commit()



def get_media(db: Session, media_id) -> Optional[models.Media]:
    return db.query(models.Media).filter(models.Media.id == media_id).first()
