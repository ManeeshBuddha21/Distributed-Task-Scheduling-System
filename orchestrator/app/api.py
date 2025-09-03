
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional

from .db import get_db
from .schemas import JobCreate, JobOut, TaskOut, WorkerRegister, TaskResult
from .crud import create_job, register_worker, heartbeat, list_tasks, claim_next_task, complete_task, fail_task

router = APIRouter(prefix="/api/v1", tags=["scheduler"])

@router.post("/jobs", response_model=JobOut)
def create_job_ep(payload: JobCreate, db: Session = Depends(get_db)):
    job = create_job(db, payload.name, [t.model_dump() for t in payload.tasks])
    return JobOut(id=job.id, name=job.name, created_at=job.created_at)

@router.post("/workers/register")
def register_worker_ep(info: WorkerRegister, db: Session = Depends(get_db)):
    register_worker(db, info.id, info.name, info.capabilities)
    return {"ok": True}

@router.post("/workers/{worker_id}/heartbeat")
def heartbeat_ep(worker_id: str, db: Session = Depends(get_db)):
    heartbeat(db, worker_id)
    return {"ok": True}

@router.get("/tasks")
def list_tasks_ep(status: Optional[str] = None, limit: int = 100, db: Session = Depends(get_db)):
    tasks = list_tasks(db, status, limit)
    return [TaskOut(id=t.id, job_id=t.job_id, status=t.status.value, priority=t.priority, payload=t.payload, assigned_worker_id=t.assigned_worker_id) for t in tasks]

@router.post("/tasks/next", response_model=TaskOut)
def claim_next_ep(worker_id: str, db: Session = Depends(get_db)):
    t = claim_next_task(db, worker_id)
    if not t:
        raise HTTPException(status_code=404, detail="no tasks available")
    return TaskOut(id=t.id, job_id=t.job_id, status=t.status.value, priority=t.priority, payload=t.payload, assigned_worker_id=t.assigned_worker_id)

@router.post("/tasks/{task_id}/complete")
def complete_task_ep(task_id: int, result: TaskResult, db: Session = Depends(get_db)):
    complete_task(db, task_id, result.result_text)
    return {"ok": True}

@router.post("/tasks/{task_id}/fail")
def fail_task_ep(task_id: int, result: TaskResult, db: Session = Depends(get_db)):
    fail_task(db, task_id, result.result_text)
    return {"ok": True}
