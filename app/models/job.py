from sqlalchemy import Column, Integer, String, Enum, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from uuid import uuid4
import enum
from datetime import datetime, timezone
from app.db.base import Base

class JobStatus(str, enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class Job(Base):
    id = Column(String, primary_key=True, default=lambda: uuid4().hex)
    user_id = Column(String, ForeignKey("user.id"), nullable=False)
    project_name = Column(String, nullable=False)
    status = Column(Enum(JobStatus, name="project_job_status"), default=JobStatus.PENDING)
    result_summary = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))
