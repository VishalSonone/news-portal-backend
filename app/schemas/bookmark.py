from pydantic import BaseModel
from datetime import datetime
import uuid
from app.schemas.article import ArticleRead

class BookmarkBase(BaseModel):
    article_id: uuid.UUID

class BookmarkCreate(BookmarkBase):
    pass

class BookmarkRead(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    article_id: uuid.UUID
    created_at: datetime
    article: ArticleRead

    model_config = {"from_attributes": True }
