from pydantic import BaseModel
from datetime import datetime
import uuid

class CommentBase(BaseModel):
    content: str

class CommentCreate(CommentBase):
    article_id: uuid.UUID

class CommentRead(CommentBase):
    id: uuid.UUID
    user_id: uuid.UUID
    article_id: uuid.UUID
    created_at: datetime

    class Config:
        orm_mode = True
