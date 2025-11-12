from app.db.session import SessionLocal
from app.services.user_service import create_user, get_user_by_email
from app.schemas.user import UserCreate

db = SessionLocal()
u = create_user(db, UserCreate(email="test@example.com", username="test", password="123456"))
print(u.email)
print(get_user_by_email(db, "test@example.com"))
db.close()
