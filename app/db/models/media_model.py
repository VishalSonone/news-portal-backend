import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship
from app.db.session import Base

class Media(Base):
    __tablename__ = "media"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    article_id = Column(
        PG_UUID(as_uuid=True),
        ForeignKey("articles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    url = Column(String(2048), nullable=False)
    mime_type = Column(String(100), nullable=True)
    size = Column(Integer, nullable=True)
    uploaded_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    article = relationship("Article", back_populates="media")

