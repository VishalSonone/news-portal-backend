from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.deps import get_db, require_roles
from app.services.user_service import count_users_by_role
from app.db.models.article import Article
from app.db.models.category import Category
from app.db.models.user import User
from app.db.enums import RoleEnum

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

@router.get("/stats", dependencies=[Depends(require_roles("admin", "editor", "author"))])
def get_dashboard_stats(db: Session = Depends(get_db), current_user = Depends(require_roles("admin", "editor", "author"))):
    # Common stats
    total_categories = db.query(Category).count()
    
    # Admin stats
    if current_user.role == RoleEnum.admin:
        total_users = db.query(User).count()
        total_articles = db.query(Article).filter(Article.status.in_(["published", "pending_review", "archived"])).count()
        return {
            "total_users": total_users,
            "total_articles": total_articles,
            "total_categories": total_categories
        }
    
    # Editor stats
    if current_user.role == RoleEnum.editor:
        pending_previews = db.query(Article).filter(Article.status == "pending_review").count()
        
        # Published today
        from datetime import datetime, timedelta
        today = datetime.utcnow().date()
        published_today = db.query(Article).filter(
            Article.status == "published",
            Article.publish_at >= today
        ).count()
        
        return {
            "pending_reviews": pending_previews,
            "published_today": published_today,
            "total_categories": total_categories
        }
    
    # Author stats
    if current_user.role == RoleEnum.author:
        my_articles = db.query(Article).filter(Article.author_id == current_user.id).count()
        pending_preview = db.query(Article).filter(
            Article.author_id == current_user.id,
            Article.status == "pending_review"
        ).count()
        published = db.query(Article).filter(
            Article.author_id == current_user.id,
            Article.status == "published"
        ).count()
        rejected = db.query(Article).filter(
            Article.author_id == current_user.id,
            Article.status == "rejected"
        ).count()
        
        return {
            "my_articles": my_articles,
            "pending_review": pending_preview,
            "published": published,
            "rejected": rejected
        }
