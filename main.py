from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.api import auth,users,category,article,comment,like,media
from fastapi.middleware.cors import CORSMiddleware
app = FastAPI(title="News Portal Backend")
app.mount("/media", StaticFiles(directory="uploads/media"), name="media")



app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(auth.router)
app.include_router(users.router)
app.include_router(category.router)
app.include_router(article.router)
app.include_router(comment.router)
app.include_router(like.router)
app.include_router(media.router)
app.include_router(users.router)


@app.get('/')
def root():
    return {
        'message':"News Portal Backend running...."
    }