from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_roles
from app.services.category_service import (
    create_category,
    get_category,
    list_categories,
    update_category,
    delete_category,
    get_category_by_slug,
)
from app.schemas.category import CategoryCreate, CategoryRead, CategoryUpdate

router = APIRouter(prefix="/categories", tags=["categories"])


@router.post("/", response_model=CategoryRead, status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(require_roles("editor", "admin"))])
def create_new_category(data: CategoryCreate, db: Session = Depends(get_db)):
    if get_category_by_slug(db, data.slug):
        raise HTTPException(status_code=400, detail="Slug already exists")
    return create_category(db, data)


@router.get("/", response_model=list[CategoryRead])
def list_all_categories(db: Session = Depends(get_db)):
    return list_categories(db)


@router.get("/{category_id}", response_model=CategoryRead)
def get_single_category(category_id: int, db: Session = Depends(get_db)):
    category = get_category(db, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category


@router.put("/{category_id}", response_model=CategoryRead,
            dependencies=[Depends(require_roles("editor", "admin"))])
def update_single_category(category_id: int, data: CategoryUpdate, db: Session = Depends(get_db)):
    category = get_category(db, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return update_category(db, category, data)


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT,
               dependencies=[Depends(require_roles("editor", "admin"))])
def delete_single_category(category_id: int, db: Session = Depends(get_db)):
    category = get_category(db, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    delete_category(db, category)
    return None


@router.get("/slug/{slug}", response_model=CategoryRead)
def get_category_by_slug_route(slug: str, db: Session = Depends(get_db)):
    category = get_category_by_slug(db, slug)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category
