from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from typing import Callable
from app.db.session import SessionLocal
from app.core.security import decode_access_token
from app.db import models
from enum import Enum

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login", auto_error=False)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def decode_role(role):
    try:
        return role.value if hasattr(role, "value") else str(role)
    except Exception:
        return str(role)

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # Ensure a token was provided
    if not token:
        raise credentials_exception

    payload = decode_access_token(token)

    # Token invalid, expired, or missing required field
    if payload is None or "sub" not in payload:
        raise credentials_exception

    user_id = payload["sub"]

   
    user = db.query(models.User).filter(models.User.id == user_id).first()

    # If token is valid but user is missing in DB
    if not user:
        raise credentials_exception

    return user


def require_roles(*allowed_roles: str) -> Callable:
    def role_dependency(current_user=Depends(get_current_user)):
        role_name = decode_role(current_user.role)
        if role_name not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )
        return current_user

    return role_dependency


def require_any_login(current_user=Depends(get_current_user)):
    return current_user


def get_current_user_optional(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """
    Returns the current user if authenticated, otherwise returns None.
    Does not raise an exception if token is invalid or missing.
    """
    if not token:
        return None
    
    try:
        payload = decode_access_token(token)
        if payload is None or "sub" not in payload:
            return None
        
        user_id = payload["sub"]
        user = db.query(models.User).filter(models.User.id == user_id).first()
        return user
    except Exception:
        return None


def ensure_article_edit_permission(
    article_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    article = db.query(models.Article).filter(models.Article.id == article_id).first()
    if not article:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Article not found")

    role_name = decode_role(current_user.role)
    if role_name in ("editor", "admin") or article.author_id == current_user.id:
        return article

    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to edit this article")


def ensure_article_delete_permission(
    article_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    article = db.query(models.Article).filter(models.Article.id == article_id).first()
    if not article:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Article not found")

    role_name = decode_role(current_user.role)
    
    if role_name in ("editor", "admin"):
        return article

    if article.author_id == current_user.id:
        status_value = article.status.value if hasattr(article.status, "value") else str(article.status)
        if status_value == "draft":
            return article
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Authors can only delete draft articles")

    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this article")


def ensure_comment_delete_permission(
    comment_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    comment = db.query(models.Comment).filter(models.Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")

    role_name = decode_role(current_user.role)
    if role_name in ("admin", "editor") or comment.user_id == current_user.id:
        return comment

    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this comment")


def ensure_category_manage_permission(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    role_name = decode_role(current_user.role)
    if role_name in ("editor", "admin"):
        return current_user

    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to manage categories")


def ensure_media_manage_permission(
    article_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    article = db.query(models.Article).filter(models.Article.id == article_id).first()
    if not article:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Article not found")

    role_name = decode_role(current_user.role)
    if role_name in ("editor", "admin") or article.author_id == current_user.id:
        return article

    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to manage media for this article")
