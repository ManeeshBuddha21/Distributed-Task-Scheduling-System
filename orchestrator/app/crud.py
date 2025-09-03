
from sqlalchemy.orm import Session
from sqlalchemy import text, select, update
from datetime import datetime, timedelta, timezone
from typing import Optional, List, Dict, Any

from .models import Job, Task, Worker, TaskStatus

def create_job(db: Session, name: str, tasks: List[Dict[str, Any]]) -> Job:
    job = Job(name=name)
    db.add(job)
    db.flush()
    for t in tasks:
        db.add(Task(job_id=job.id, priority=t.get("priority", 0), payload=t["payload"], max_retries=t.get("max_retries", 3)))
    db.commit()
    db.refresh(job)
    return job

def register_worker(db: Session, worker_id: str, name: Optional[str], capabilities: Optional[Dict]):
    worker = db.get(Worker, worker_id)
    if worker:
        worker.name = name or worker.name
        worker.capabilities = capabilities or worker.capabilities
    else:
        worker = Worker(id=worker_id, name=name, capabilities=capabilities)
        db.add(worker)
    db.commit()
    return worker

def heartbeat(db: Session, worker_id: str):
    db.execute(text("""UPDATE workers SET last_heartbeat = NOW() WHERE id = :wid"""), {"wid": worker_id})
    db.commit()

def list_tasks(db: Session, status: Optional[str] = None, limit: int = 100) -> List[Task]:
    q = select(Task).order_by(Task.id.desc()).limit(limit)
    if status:
        q = select(Task).where(Task.status == status).order_by(Task.id.desc()).limit(limit)
    return list(db.scalars(q))

def claim_next_task(db: Session, worker_id: str) -> Optional[Task]:
    # SKIP LOCKED to avoid thundering herd
    res = db.execute(text("""
        UPDATE tasks SET status = 'in_progress', assigned_worker_id = :wid, started_at = NOW(), updated_at = NOW()
        WHERE id = (
            SELECT id FROM tasks
            WHERE status = 'queued'
            ORDER BY priority DESC, created_at ASC
            FOR UPDATE SKIP LOCKED
            LIMIT 1
        )
        RETURNING id
    """), {"wid": worker_id}).fetchone()
    if not res:
        return None
    task_id = res[0]
    task = db.get(Task, task_id)
    return task

def complete_task(db: Session, task_id: int, result_text: str):
    db.execute(text("""
        UPDATE tasks SET status = 'done', result_text = :res, completed_at = NOW(), updated_at = NOW()
        WHERE id = :tid
    """), {"tid": task_id, "res": result_text})
    db.commit()

def fail_task(db: Session, task_id: int, reason: str):
    db.execute(text("""
        UPDATE tasks SET status = 'failed', result_text = :res, completed_at = NOW(), updated_at = NOW()
        WHERE id = :tid
    """), {"tid": task_id, "res": reason})
    db.commit()

def requeue_stale_inprogress(db: Session, ttl_seconds: int = 60, batch_size: int = 200):
    cutoff = datetime.now(timezone.utc) - timedelta(seconds=ttl_seconds)
    db.execute(text("""
        UPDATE tasks SET status = 'queued', assigned_worker_id = NULL, started_at = NULL, updated_at = NOW(), retry_count = retry_count + 1
        WHERE status = 'in_progress' AND updated_at < :cutoff AND retry_count < max_retries
    """), {"cutoff": cutoff})
    db.commit()
