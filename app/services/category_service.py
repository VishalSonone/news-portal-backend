
from sqlalchemy.orm import Session
from typing import Optional, List
from app.db import models
from app.schemas.category import CategoryCreate, CategoryUpdate


def create_category(db: Session, data: CategoryCreate) -> models.Category:
    category = models.Category(
        name=data.name,
        slug=data.slug,
        description=data.description,
    )
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


def get_category(db: Session, category_id: int) -> Optional[models.Category]:
    return db.query(models.Category).filter(models.Category.id == category_id).first()


def get_category_by_slug(db: Session, slug: str) -> Optional[models.Category]:
    return db.query(models.Category).filter(models.Category.slug == slug).first()


def list_categories(db: Session) -> List[models.Category]:
    return db.query(models.Category).order_by(models.Category.id).all()


def update_category(db: Session, category: models.Category, data: CategoryUpdate) -> models.Category:
    if data.name is not None:
        category.name = data.name
    if data.slug is not None:
        category.slug = data.slug
    if data.description is not None:
        category.description = data.description

    db.commit()
    db.refresh(category)
    return category


def delete_category(db: Session, category: models.Category):
    db.delete(category)
    db.commit()


def get_category_by_slug(db: Session, slug: str):
    return db.query(models.Category).filter(models.Category.slug == slug).first()
