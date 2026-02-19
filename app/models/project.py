from sqlalchemy import Column, String, ForeignKey, DateTime
from uuid import uuid4
from datetime import datetime, timezone
from app.db.base import Base
from sqlalchemy.orm import relationship

class Project(Base):
    id = Column(String, primary_key=True, default=lambda: uuid4().hex)
    name = Column(String, index=True, nullable=False)
    slug = Column(String, unique=True, index=True, nullable=False)
    user_id = Column(String, ForeignKey("user.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    
    user = relationship("User", back_populates="user_projects")
