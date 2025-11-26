from pydantic import BaseModel
from datetime import datetime
import uuid


class MediaCreate(BaseModel):
    article_id: uuid.UUID


class MediaRead(BaseModel):
    id: uuid.UUID
    url: str
    mime_type: str | None = None
    size: int | None = None
    uploaded_at: datetime

    model_config = {"from_attributes": True }
