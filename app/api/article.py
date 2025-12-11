from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.schemas.pagination import PaginatedResponse
from app.api.deps import (
    get_db,
    get_current_user,
    get_current_user_optional,
    require_roles,
    ensure_article_edit_permission,
    ensure_article_delete_permission
)
from app.services.category_service import get_category
from app.schemas.article import ArticleCreate, ArticleRead, ArticleUpdate
from app.services.article_service import (
    create_article,
    get_article,
    update_article,
    delete_article,
    get_article_by_slug,
    get_articles_by_category,
    search_articles,
    get_paginated_articles
)
from app.db.models import Article
from app.services.summarizer import summarize_news
router = APIRouter(prefix="/articles", tags=["articles"])


@router.post("/", response_model=ArticleRead, status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(require_roles("author"))])
def create_new_article(
    data: ArticleCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if not get_category(db,data.category_id):
        raise HTTPException(status_code=400, detail="category not exists")

    if get_article_by_slug(db, data.slug):
        raise HTTPException(status_code=400, detail="Slug already exists")
    return create_article(db, data, author_id=current_user.id)


@router.get("/search", response_model=PaginatedResponse)
def search_articles_route(
    q: str,
    page: int = 1,
    limit: int = 6,
    category_id: int = None,
    author_id: str = None,
    status: str = None,
    sort: str = "latest",
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_optional)
):
    if not q or q.strip() == "":
        raise HTTPException(status_code=400, detail="Search query 'q' is required")
    items, total = search_articles(
        db=db,
        q=q,
        page=page,
        limit=limit,
        category_id=category_id,
        author_id=author_id,
        status=status,
        sort=sort,
        current_user=current_user
    )
    return {
        "items": [ArticleRead.model_validate(i) for i in items],
        "total": total,
        "page": page,
        "limit": limit
    }


@router.get("/category/{category_id}", response_model=PaginatedResponse)
def get_articles_by_category_route(
    category_id: int,
    page: int = 1,
    limit: int = 6,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_optional)
):
    items = get_articles_by_category(db, category_id, current_user)
    total = len(items)
    start = (page - 1) * limit
    end = start + limit
    paginated = items[start:end]
    return {
        "items": [ArticleRead.model_validate(i) for i in paginated],
        "total": total,
        "page": page,
        "limit": limit
    }


@router.get("/", response_model=PaginatedResponse)
def list_articles_paginated(
    page: int = 1,
    limit: int = 6,
    status: str = None,
    author_id: str = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_optional)
):
    items, total = get_paginated_articles(db, page, limit, current_user, status, author_id)
    return {
        "items": [ArticleRead.model_validate(i) for i in items],
        "total": total,
        "page": page,
        "limit": limit
    }


@router.get("/{article_id}", response_model=ArticleRead)
def get_single_article(
    article_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_optional)
):
    article = get_article(db, article_id, current_user)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    return ArticleRead.model_validate(article)


@router.put("/{article_id}", response_model=ArticleRead)
def update_single_article(
    article_id: str,
    data: ArticleUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
    article = Depends(ensure_article_edit_permission)
):
    # Debug logging
    with open("debug_update.log", "a") as f:
        f.write(f"Updating article {article_id}\n")
        f.write(f"User: {current_user.id} (Role: {current_user.role})\n")
        f.write(f"Data: {data}\n")
    
    try:
        updated = update_article(db, article, data, current_user)
        return ArticleRead.model_validate(updated)
    except Exception as e:
        with open("debug_update.log", "a") as f:
            f.write(f"Error updating article: {str(e)}\n")
        raise e


@router.delete("/{article_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_single_article(
    article_id: str,
    db: Session = Depends(get_db),
    article = Depends(ensure_article_delete_permission)
):
    delete_article(db, article)
    return None


@router.get("/summarize/{article_id}",status_code=status.HTTP_200_OK)
def summarize_article(
        article_id:str,
        db:Session=Depends(get_db)):
    article=db.query(Article).filter(Article.id==article_id).first()
    return summarize_news(article.content)