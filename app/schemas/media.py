from pydantic import BaseModel
from datetime import datetime
import uuid

class MediaBase(BaseModel):
    url: str
    mime_type: str | None = None
    size: int | None = None

class MediaCreate(MediaBase):
    article_id: uuid.UUID

class MediaRead(MediaBase):
    id: uuid.UUID
    uploaded_at: datetime

    class Config:
        orm_mode = True
