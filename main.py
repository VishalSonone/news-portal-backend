from fastapi import FastAPI
from app.api import auth,users,category,article
app=FastAPI()

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(category.router)
app.include_router(article.router)
@app.get('/')
def root():
    return {
        'message':"News Portal Backend running...."
    }