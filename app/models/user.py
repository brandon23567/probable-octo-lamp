from sqlalchemy import Column, Integer, String, Boolean, DateTime
from app.db.base import Base
from uuid import uuid4 
from datetime import datetime, timezone

class User(Base):
    id = Column(String, primary_key=True, index=True, default=lambda: uuid4().hex)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    date_created = Column(DateTime, default=lambda: datetime.now(timezone.utc))
