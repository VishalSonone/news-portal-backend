from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.db.session import Base

class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(150), nullable=False, unique=True)
    slug = Column(String(160), nullable=False, unique=True, index=True)
    description = Column(String(500), nullable=True)

    articles = relationship(
        "Article",
        back_populates="category",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
