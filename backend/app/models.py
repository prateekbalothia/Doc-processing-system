from sqlalchemy import Column, Integer, String, DateTime, Boolean, JSON
from sqlalchemy.sql import func
from app.database import Base

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)

    filename = Column(String, nullable=False)
    filepath = Column(String, nullable=False)
    file_type = Column(String)
    file_size = Column(Integer)

    status = Column(String, default="queued")  # queued, processing, completed, failed
    progress = Column(Integer, default=0)

    result = Column(JSON, nullable=True)

    is_finalized = Column(Boolean, default=False)

    error_message = Column(String, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

