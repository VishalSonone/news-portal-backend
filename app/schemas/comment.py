from pydantic import BaseModel
from datetime import datetime
import uuid

from app.schemas.user import UserRead
from app.schemas.article import ArticleRead
from typing import Optional

class CommentBase(BaseModel):
    content: str


class CommentCreate(CommentBase):
    article_id: uuid.UUID


class CommentRead(CommentBase):
    id: uuid.UUID
    user_id: uuid.UUID
    article_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    user: UserRead
    article: Optional[ArticleRead] = None
    
    model_config = {"from_attributes": True }

   
