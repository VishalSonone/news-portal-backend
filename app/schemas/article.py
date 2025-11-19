from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
import uuid
from enum import Enum
from app.schemas.user import UserRead
from app.schemas.category import CategoryRead

class ArticleStatus(str, Enum):
    draft = "draft"
    published = "published"
    archived = "archived"

class ArticleBase(BaseModel):
    title: str
    slug: str
    summary: Optional[str] = None
    content: Optional[str] = None
    status: ArticleStatus = ArticleStatus.draft
    publish_at: Optional[datetime] = None

class ArticleCreate(ArticleBase):
    category_id: Optional[int] = None

class ArticleUpdate(BaseModel):
    title: Optional[str] = None
    slug: Optional[str] = None
    summary: Optional[str] = None
    content: Optional[str] = None
    status: Optional[ArticleStatus] = None
    publish_at: Optional[datetime] = None
    category_id: Optional[int] = None

class ArticleRead(ArticleBase):
    id: uuid.UUID
    author_id: uuid.UUID
    category_id: Optional[int]
    views: int
    likes_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
