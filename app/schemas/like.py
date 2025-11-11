from pydantic import BaseModel
from datetime import datetime
import uuid

class LikeBase(BaseModel):
    article_id: uuid.UUID

class LikeCreate(LikeBase):
    pass

class LikeRead(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    article_id: uuid.UUID
    created_at: datetime

    class Config:
        orm_mode = True
