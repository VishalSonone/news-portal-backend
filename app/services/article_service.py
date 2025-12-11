from sqlalchemy.orm import Session
from typing import Optional, List
from app.db import models
from app.schemas.article import ArticleCreate, ArticleUpdate
from sqlalchemy import or_
from fastapi import HTTPException
from app.services.embedding_service import index_article


def create_article(db: Session, data: ArticleCreate, author_id: str):
    article = models.Article(
        **data.model_dump(),
        author_id=author_id
    )
    db.add(article)
    db.commit()
    db.refresh(article)
    try:
        index_article(article)
    except:
        pass

    return article


def get_article(db: Session, article_id: str, current_user=None):
    article = db.query(models.Article).filter(models.Article.id == article_id).first()
    if not article:
        return None
    
    if not can_view_article(article, current_user):
        return None
        
    return article


def get_article_by_slug(db: Session, slug: str, current_user=None):
    article = db.query(models.Article).filter(models.Article.slug == slug).first()
    if not article:
        return None
        
    if not can_view_article(article, current_user):
        return None
        
    return article


def can_view_article(article: models.Article, current_user) -> bool:
    """
    Determines if a user can view an article based on status and role.
    - Published: visible to everyone
    - Draft: only visible to author
    - Archived: visible to admin, editor, and author (NOT reader)
    """
    article_status = article.status.value if hasattr(article.status, 'value') else str(article.status)
    
    # Published articles are visible to everyone
    if article_status == "published":
        return True
    
    # If no user is logged in, they can only see published articles
    if not current_user:
        return False
    
    # Get user role
    user_role = current_user.role.value if hasattr(current_user.role, 'value') else str(current_user.role)
    
    # Admin and Editor can see pending_review
    if article_status == "pending_review":
        if user_role in ("admin", "editor"):
            return True
        # Author can see their own pending_review
        return str(article.author_id) == str(current_user.id)

    # Draft articles: only author can see
    if article_status == "draft":
        return str(article.author_id) == str(current_user.id)
    
    # Archived articles: admin, editor, and author can see (NOT reader)
    if article_status == "archived":
        if user_role in ("admin", "editor"):
            return True
        return str(article.author_id) == str(current_user.id)
    
    # Rejected articles: only author can see
    if article_status == "rejected":
        return str(article.author_id) == str(current_user.id)

    return False


def apply_article_visibility_filter(query, current_user, skip_filter=False):
    """
    Applies visibility filters to an article query based on user role.
    Set skip_filter=True when the query is already filtered by author_id
    """
    # Skip visibility filter if already filtered by specific criteria
    if skip_filter:
        return query
    
    # If no user is logged in, only show published articles
    if not current_user:
        return query.filter(models.Article.status == "published")
    
    # Get user role
    user_role = current_user.role.value if hasattr(current_user.role, 'value') else str(current_user.role)
    
    # Admin and editor can see all articles
    # Admin can see: published, pending_review, archived (NOT draft, NOT rejected)
    if user_role == "admin":
        return query.filter(
            models.Article.status.in_(["published", "pending_review", "archived"])
        )

    # Editor can see published and pending_review
    if user_role == "editor":
        return query.filter(
            or_(
                models.Article.status == "published",
                models.Article.status == "pending_review"
            )
        )
    
    # Author can see: published (all), their own drafts, their own pending_review, their own archived, their own rejected
    if user_role == "author":
        return query.filter(
            or_(
                models.Article.status == "published",
                models.Article.author_id == current_user.id,
                models.Article.status == "rejected"
            )
        )
    
    # Reader can only see published articles
    return query.filter(models.Article.status == "published")


def update_article(db: Session, article: models.Article, data: ArticleUpdate, current_user):
    # Status transition logic
    if data.status is not None:
        new_status = data.status.value if hasattr(data.status, 'value') else str(data.status)
        old_status = article.status.value if hasattr(article.status, 'value') else str(article.status)

        if new_status != old_status:
            user_role = current_user.role.value if hasattr(current_user.role, 'value') else str(current_user.role)

            # Author Rules
            if user_role == "author":
                # Author can move draft -> pending_review
                # Author can move rejected -> pending_review (Resubmit)
                # Author can move pending_review -> draft (Retract)
                if (old_status == "draft" and new_status == "pending_review") or \
                   (old_status == "rejected" and new_status == "pending_review") or \
                   (old_status == "pending_review" and new_status == "draft"):
                    pass # Allowed
                else:
                    raise HTTPException(
                        status_code=403, 
                        detail=f"Author cannot change status from {old_status} to {new_status}"
                    )
            
            # Editor Rules
            elif user_role == "editor":
                # Editor can move pending_review -> published (Approve)
                # Editor can move pending_review -> rejected (Reject)
                if old_status == "pending_review" and new_status in ("published", "rejected"):
                    pass # Allowed
                else:
                    raise HTTPException(
                        status_code=403, 
                        detail=f"Editor cannot change status from {old_status} to {new_status}"
                    )

            # Admin Rules
            elif user_role == "admin":
                # Admin can move pending_review -> rejected (Reject)
                # Admin can move pending_review -> published (Approve)
                # Admin can move published -> archived (Archive)
                # Admin can move archived -> published (Republish)
                
                allowed_transitions = [
                    ("pending_review", "rejected"),
                    ("pending_review", "published"),
                    ("published", "archived"),
                    ("archived", "published")
                ]
                
                if (old_status, new_status) in allowed_transitions:
                    pass # Allowed
                else:
                     raise HTTPException(
                        status_code=403, 
                        detail=f"Admin cannot change status from {old_status} to {new_status}"
                    )

    if data.title is not None:
        article.title = data.title
    if data.slug is not None:
        article.slug = data.slug
    if data.summary is not None:
        article.summary = data.summary
    if data.content is not None:
        article.content = data.content
    
    if data.status is not None:
        article.status = data.status
        
    if data.publish_at is not None:
        article.publish_at = data.publish_at
    if data.category_id is not None:
        article.category_id = data.category_id
    if data.rejection_reason is not None:
        article.rejection_reason = data.rejection_reason

    db.commit()
    db.refresh(article)
    try:
        index_article(article)
    except:
        pass

    return article


def delete_article(db: Session, article: models.Article):
    db.delete(article)
    db.commit()


def get_articles_by_category(db: Session, category_id: int, current_user=None):
    # Home/Category pages should ONLY show published articles, regardless of user role
    query = db.query(models.Article).filter(
        models.Article.category_id == category_id,
        models.Article.status == "published"
    )
    return query.order_by(models.Article.created_at.desc()).all()


def paginate(query, page: int, limit: int):
    total = query.count()
    items = query.offset((page - 1) * limit).limit(limit).all()
    return items, total


def search_articles(
    db: Session,
    q: str,
    page: int,
    limit: int,
    category_id: int = None,
    author_id: str = None,
    status: str = None,
    sort: str = "latest",
    current_user = None
):
    query = db.query(models.Article)

    query = query.filter(
        or_(
            models.Article.title.ilike(f"%{q}%"),
            models.Article.summary.ilike(f"%{q}%"),
            models.Article.content.ilike(f"%{q}%"),
        )
    )

    if category_id:
        query = query.filter(models.Article.category_id == category_id)

    if author_id:
        query = query.filter(models.Article.author_id == author_id)

    if status:
        query = query.filter(models.Article.status == status)
    
    # Apply visibility filter based on user role
    query = apply_article_visibility_filter(query, current_user)

    if sort == "latest":
        query = query.order_by(models.Article.created_at.desc())
    elif sort == "oldest":
        query = query.order_by(models.Article.created_at.asc())
    elif sort == "likes":
        query = query.order_by(models.Article.likes_count.desc())
    elif sort == "views":
        query = query.order_by(models.Article.views.desc())

    return paginate(query, page, limit)


def get_paginated_articles(db: Session, page: int, limit: int, current_user=None, status: str = None, author_id: str = None):
    query = db.query(models.Article)
    
    # Apply status and author_id filters FIRST (before visibility filter)
    if author_id:
        query = query.filter(models.Article.author_id == author_id)
    
    if status:
        query = query.filter(models.Article.status == status)
        
    # Skip visibility filter if author_id is provided (reducing SQL complexity)
    # Authors filtering their own articles don't need additional visibility checks
    skip_visibility = bool(author_id and current_user and str(author_id) == str(current_user.id))
    query = apply_article_visibility_filter(query, current_user, skip_filter=skip_visibility)
    
    query = query.order_by(models.Article.created_at.desc())
    return paginate(query, page, limit)
