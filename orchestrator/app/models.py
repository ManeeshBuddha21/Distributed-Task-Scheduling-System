
from sqlalchemy import Column, Integer, String, JSON, Enum, ForeignKey, TIMESTAMP, text
from sqlalchemy.orm import relationship
import enum

from .db import Base

class TaskStatus(str, enum.Enum):
    pending = "pending"
    queued = "queued"
    in_progress = "in_progress"
    done = "done"
    failed = "failed"

class Job(Base):
    __tablename__ = "jobs"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=text("NOW()"))
    tasks = relationship("Task", back_populates="job", cascade="all, delete")

class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False)
    priority = Column(Integer, nullable=False, default=0)
    status = Column(Enum(TaskStatus), nullable=False, default=TaskStatus.pending)
    payload = Column(JSON, nullable=False)
    result_text = Column(String)
    assigned_worker_id = Column(String)
    retry_count = Column(Integer, nullable=False, default=0)
    max_retries = Column(Integer, nullable=False, default=3)
    created_at = Column(TIMESTAMP(timezone=True), server_default=text("NOW()"))
    updated_at = Column(TIMESTAMP(timezone=True), server_default=text("NOW()"))
    started_at = Column(TIMESTAMP(timezone=True))
    completed_at = Column(TIMESTAMP(timezone=True))

    job = relationship("Job", back_populates="tasks")

class Worker(Base):
    __tablename__ = "workers"
    id = Column(String, primary_key=True)
    name = Column(String)
    capabilities = Column(JSON)
    last_heartbeat = Column(TIMESTAMP(timezone=True), server_default=text("NOW()"))
