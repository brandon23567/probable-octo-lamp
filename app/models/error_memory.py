from sqlalchemy import Column, Integer, String, Text, DateTime
from pgvector.sqlalchemy import Vector
from datetime import datetime, timezone
from app.db.base import Base
from uuid import uuid4

class ErrorMemory(Base):
    id = Column(String, primary_key=True, index=True, default=lambda: uuid4().hex)
    error_hash = Column(String, index=True, nullable=False)
    error_summary = Column(Text, nullable=False)
    file_path = Column(String, nullable=False)
    corrected_code = Column(Text, nullable=False)
    embedding = Column(Vector(384)) 
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
