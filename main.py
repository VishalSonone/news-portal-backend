from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.api import auth,users,category,article,comment,like,media

app = FastAPI(title="News Portal Backend")
app.mount("/media", StaticFiles(directory="uploads/media"), name="media")


app.include_router(auth.router)
app.include_router(users.router)
app.include_router(category.router)
app.include_router(article.router)
app.include_router(comment.router)
app.include_router(like.router)
app.include_router(media.router, prefix="/api/v1")


@app.get('/')
def root():
    return {
        'message':"News Portal Backend running...."
    }