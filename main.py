from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.api import auth, users, category, article, media, dashboard, comment, like, bookmark,chat
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="News Portal Backend")

# CORS must be added BEFORE mounting static files and adding routers
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=False,  # Disabled to work with wildcard
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(category.router)
app.include_router(article.router)
app.include_router(media.router)
app.include_router(dashboard.router)
app.include_router(comment.router)
app.include_router(like.router)
app.include_router(bookmark.router)
app.include_router(chat.router)


# Mount static files AFTER routers to avoid shadowing /media/upload
app.mount("/media", StaticFiles(directory="uploads/media"), name="media")

# @app.on_event("startup")
# def create_admin_user():
#     from app.db.session import SessionLocal
#     from app.db import models
#     from app.core.security import get_password_hash
#     from app.db.enums import RoleEnum
    
#     db = SessionLocal()
#     try:
#         email = "admin@gmail.com"
#         password = "5555"
#         user = db.query(models.User).filter(models.User.email == email).first()
#         if user:
#             user.hashed_password = get_password_hash(password)
#             user.role = RoleEnum.admin
#             user.is_active = True
#             print(f"Admin user {email} updated.")
#         else:
#             user = models.User(
#                 email=email,
#                 username="admin",
#                 hashed_password=get_password_hash(password),
#                 role=RoleEnum.admin,
#                 is_active=True
#             )
#             db.add(user)
#             print(f"Admin user {email} created.")
#         db.commit()
#     except Exception as e:
#         print(f"Error creating admin: {e}")
#     finally:
#         db.close()

@app.get('/')
def root():
    return {
        'message':"News Portal Backend running...."
    }