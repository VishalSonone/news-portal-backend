import uuid
from datetime import datetime
from sqlalchemy import (
    Column,
    String,
    Text,
    Integer,
    DateTime,
    Enum,
    ForeignKey,
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship
from app.db.session import Base
from enum import Enum as PyEnum


class ArticleStatus(PyEnum):
    draft = "draft"
    pending_review = "pending_review"
    rejected = "rejected"
    published = "published"
    archived = "archived"

class Article(Base):
    __tablename__ = "articles"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(500), nullable=False)
    slug = Column(String(550), unique=True, nullable=False, index=True)
    summary = Column(String(2000), nullable=True)
    content = Column(Text, nullable=True)
    status = Column(Enum(ArticleStatus), default=ArticleStatus.draft, nullable=False)
    rejection_reason = Column(Text, nullable=True)
    publish_at = Column(DateTime, nullable=True)
    source_url = Column(String(2048), nullable=True)
    views = Column(Integer, default=0, nullable=False)
    likes_count = Column(Integer, default=0, nullable=False)

    author_id = Column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    category_id = Column(
        Integer,
        ForeignKey("categories.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    author = relationship("User", back_populates="articles", lazy="joined")
    category = relationship("Category", back_populates="articles", lazy="joined")
    media = relationship(
        "Media",
        back_populates="article",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    comments = relationship(
        "Comment",
        back_populates="article",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    likes = relationship(
        "Like",
        back_populates="article",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    bookmarks = relationship(
        "Bookmark",
        back_populates="article",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

