from pydantic import BaseModel, model_validator
from datetime import datetime
from typing import Optional, List
import uuid
from enum import Enum
from app.schemas.user import UserRead
from app.schemas.category import CategoryRead
from app.schemas.media import MediaRead

class ArticleStatus(str, Enum):
    draft = "draft"
    pending_review = "pending_review"
    rejected = "rejected"
    published = "published"
    archived = "archived"

class ArticleBase(BaseModel):
    title: str
    slug: str
    summary: Optional[str] = None
    content: Optional[str] = None
    status: ArticleStatus = ArticleStatus.draft
    publish_at: Optional[datetime] = None
    rejection_reason: Optional[str] = None

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
    rejection_reason: Optional[str] = None

class ArticleRead(ArticleBase):
    id: uuid.UUID
    author_id: uuid.UUID
    category_id: Optional[int]
    views: int
    likes_count: int
    created_at: datetime
    updated_at: datetime
    rejection_reason: Optional[str] = None
    featured_image: Optional[str] = None
    
    # Nested objects for display
    author: Optional[UserRead] = None
    category: Optional[CategoryRead] = None
    media: List[MediaRead] = []

    model_config = {"from_attributes": True }

    @model_validator(mode='after')
    def populate_featured_image(self):
        if self.media and len(self.media) > 0:
            self.featured_image = self.media[0].url
        return self

