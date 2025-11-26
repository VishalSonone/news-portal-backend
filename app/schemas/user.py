from pydantic import BaseModel, EmailStr
from datetime import datetime
import uuid
from enum import Enum

class RoleEnum(str, Enum):
    reader = "reader"
    author = "author"
    editor = "editor"
    admin = "admin"

class UserBase(BaseModel):
    email: EmailStr
    username: str | None = None
    role: RoleEnum = RoleEnum.reader
    is_active: bool = True

class UserCreate(UserBase):
    password: str

class UserRead(UserBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True }
