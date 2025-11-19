
from sqlalchemy.orm import Session
from typing import Optional, List
from app.db import models
from app.schemas.article import ArticleCreate, ArticleUpdate



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
