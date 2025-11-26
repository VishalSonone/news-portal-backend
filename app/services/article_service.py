from sqlalchemy.orm import Session
from typing import Optional, List
from app.db import models
from app.schemas.article import ArticleCreate, ArticleUpdate
from sqlalchemy import or_


def create_article(db: Session, data: ArticleCreate, author_id):
    article = models.Article(
        title=data.title,
        slug=data.slug,
        summary=data.summary,
        content=data.content,
        status=data.status,
        publish_at=data.publish_at,
        category_id=data.category_id,
        author_id=author_id,
    )
    db.add(article)
    db.commit()
    db.refresh(article)
    return article


def get_article(db: Session, article_id) -> Optional[models.Article]:
    return db.query(models.Article).filter(models.Article.id == article_id).first()


def get_article_by_slug(db: Session, slug: str) -> Optional[models.Article]:
    return db.query(models.Article).filter(models.Article.slug == slug).first()


def list_articles(db: Session) -> List[models.Article]:
    return db.query(models.Article).order_by(models.Article.created_at.desc()).all()


def update_article(db: Session, article: models.Article, data: ArticleUpdate):
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

    db.commit()
    db.refresh(article)
    return article


def delete_article(db: Session, article: models.Article):
    db.delete(article)
    db.commit()


def get_articles_by_category(db: Session, category_id: int):
    return (
        db.query(models.Article)
        .filter(models.Article.category_id == category_id)
        .order_by(models.Article.created_at.desc())
        .all()
    )


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
    sort: str = "latest"
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

    if sort == "latest":
        query = query.order_by(models.Article.created_at.desc())
    elif sort == "oldest":
        query = query.order_by(models.Article.created_at.asc())
    elif sort == "likes":
        query = query.order_by(models.Article.likes_count.desc())
    elif sort == "views":
        query = query.order_by(models.Article.views.desc())

    return paginate(query, page, limit)


def get_paginated_articles(db: Session, page: int, limit: int):
    query = db.query(models.Article).order_by(models.Article.created_at.desc())
    return paginate(query, page, limit)
