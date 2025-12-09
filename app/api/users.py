from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.api.deps import get_db, require_roles, get_current_user
from app.services.user_service import get_user_by_email, get_user_by_id, create_user, list_users, update_user_role, toggle_user_activation, delete_user, update_user
from app.schemas.user import UserCreate, UserRead, UserUpdate

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserRead)
def read_current_user(current_user = Depends(get_current_user)):
    return current_user


@router.get("/", response_model=List[UserRead], dependencies=[Depends(require_roles("admin"))])
def admin_list_users(db: Session = Depends(get_db)):
    return list_users(db)


@router.post("/", response_model=UserRead, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_roles("admin"))])
def admin_create_user(data: UserCreate, db: Session = Depends(get_db)):
    user = get_user_by_email(db, data.email)
    if user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return create_user(db, data)


@router.get("/{user_id}", response_model=UserRead, dependencies=[Depends(require_roles("admin"))])
def admin_get_user(user_id: str, db: Session = Depends(get_db)):
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.put("/{user_id}", response_model=UserRead, dependencies=[Depends(require_roles("admin"))])
def admin_update_user(user_id: str, data: UserUpdate, db: Session = Depends(get_db)):
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return update_user(db, user, data)


@router.put("/{user_id}/role", response_model=UserRead, dependencies=[Depends(require_roles("admin"))])
def admin_update_user_role(user_id: str, role: str, db: Session = Depends(get_db)):
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    updated = update_user_role(db, user, role)
    return updated


@router.put("/{user_id}/activate", response_model=UserRead, dependencies=[Depends(require_roles("admin"))])
def admin_toggle_user_activation(user_id: str, db: Session = Depends(get_db)):
    """Toggle user's is_active status"""
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    updated = toggle_user_activation(db, user)
    return updated


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_roles("admin"))])
def admin_delete_user(user_id: str, db: Session = Depends(get_db)):
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    delete_user(db, user)
    return None
