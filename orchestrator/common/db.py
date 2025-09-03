
from datetime import datetime
import uuid
from typing import Optional, Any, Dict

from sqlalchemy import (create_engine, MetaData, Table, Column, String, Integer, 
                        DateTime, Enum, JSON, text, select, update)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import sessionmaker
import enum

from .settings import POSTGRES_HOST, POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_PORT

class StatusEnum(str, enum.Enum):
    pending = "pending"
    queued = "queued"
    processing = "processing"
    done = "done"
    failed = "failed"

def pg_dsn() -> str:
    return f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

engine = create_engine(pg_dsn(), pool_pre_ping=True, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)

metadata = MetaData()

tasks = Table(
    "tasks",
    metadata,
    Column("id", String, primary_key=True),
    Column("type", String, nullable=False),
    Column("payload", JSONB, nullable=False, server_default=text("'{}'::jsonb")),
    Column("priority", Integer, nullable=False, server_default=text("10")),
    Column("status", Enum(StatusEnum), nullable=False, server_default=StatusEnum.pending.value),
    Column("result", JSONB, nullable=True),
    Column("scheduled_at", DateTime(timezone=True), nullable=False),
    Column("created_at", DateTime(timezone=True), nullable=False, server_default=text("now()")),
    Column("updated_at", DateTime(timezone=True), nullable=False, server_default=text("now()")),
)

def create_task(session, task_type: str, payload: Dict[str, Any], priority: int, scheduled_at: datetime) -> str:
    task_id = str(uuid.uuid4())
    now = datetime.utcnow()
    session.execute(
        tasks.insert().values(
            id=task_id,
            type=task_type,
            payload=payload,
            priority=priority,
            status=StatusEnum.pending.value,
            scheduled_at=scheduled_at,
            created_at=now,
            updated_at=now,
        )
    )
    session.commit()
    return task_id

def list_tasks(session, limit: int = 50):
    stmt = select(tasks).order_by(tasks.c.created_at.desc()).limit(limit)
    return session.execute(stmt).mappings().all()

def get_task(session, task_id: str):
    stmt = select(tasks).where(tasks.c.id == task_id)
    return session.execute(stmt).mappings().first()

def mark_task_status(session, task_id: str, status: StatusEnum, result=None):
    stmt = (
        update(tasks)
        .where(tasks.c.id == task_id)
        .values(status=status.value, result=result, updated_at=datetime.utcnow())
    )
    session.execute(stmt)
    session.commit()
