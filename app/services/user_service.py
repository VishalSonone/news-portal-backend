from sqlalchemy.orm import Session
from typing import Optional, List
from app.db import models
from app.schemas.user import UserCreate, UserUpdate
import bcrypt


def get_user_by_email(db: Session, email: str) -> Optional[models.User]:
    return db.query(models.User).filter(models.User.email == email).first()


def get_user_by_id(db: Session, user_id: str) -> Optional[models.User]:
    return db.query(models.User).filter(models.User.id == user_id).first()


def list_users(db: Session) -> List[models.User]:
    return db.query(models.User).order_by(models.User.created_at.desc()).all()


def create_user(db: Session, data: UserCreate) -> models.User:
    # hash password with bcrypt
    raw = data.password.encode("utf-8")
    hashed = bcrypt.hashpw(raw, bcrypt.gensalt()).decode("utf-8")

    user = models.User(
        email=data.email,
        username=data.username,
        hashed_password=hashed,
        role=data.role,
        is_active=data.is_active if data.is_active is not None else True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def count_users_by_role(db: Session, role: str) -> int:
    return db.query(models.User).filter(models.User.role == role).count()


def count_active_authors(db: Session) -> int:
    return (
        db.query(models.User)
        .filter(models.User.role == "author", models.User.is_active == True)
        .count()
    )
def update_user_role(db: Session, user: models.User, role: str) -> models.User:
    user.role = role
    db.commit()
    db.refresh(user)
    return user


def toggle_user_activation(db: Session, user: models.User) -> models.User:
    """Toggle user's is_active status"""
    user.is_active = not user.is_active
    db.commit()
    db.refresh(user)
    return user


def delete_user(db: Session, user: models.User):
    db.delete(user)
    db.commit()


def update_user(db: Session, user: models.User, data: UserUpdate) -> models.User:
    if data.email is not None:
        user.email = data.email
    if data.username is not None:
        user.username = data.username
    if data.password is not None:
        raw = data.password.encode("utf-8")
        hashed = bcrypt.hashpw(raw, bcrypt.gensalt()).decode("utf-8")
        user.hashed_password = hashed
    if data.role is not None:
        user.role = data.role
    if data.is_active is not None:
        user.is_active = data.is_active
        
    db.commit()
    db.refresh(user)
    return user
