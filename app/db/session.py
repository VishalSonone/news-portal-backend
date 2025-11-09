from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base,sessionmaker
from app.core.config import settings


engine=create_engine(settings.DATABASE_URL)

SessionLocal=sessionmaker(autoflush=False,autocommit=False,echo=True,bind=engine,)

Base=declarative_base()

def getdb():
    db=SessionLocal()
    try:
        yield db
    finally:
        db.close()