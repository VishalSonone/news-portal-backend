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

class UserUpdate(BaseModel):
    email: EmailStr | None = None
    username: str | None = None
    password: str | None = None
    role: RoleEnum | None = None
    is_active: bool | None = None

class UserRead(UserBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True }

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str
