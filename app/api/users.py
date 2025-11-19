from fastapi import APIRouter, Depends
from app.schemas.user import UserRead
from app.api.deps import get_current_user

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserRead)
def read_current_user(current_user = Depends(get_current_user)):
    """Return the currently authenticated user's info."""
    return current_user
