
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timedelta, timezone

from common.db import SessionLocal, create_task, list_tasks, get_task
from common.schema import CreateTaskRequest
from common.settings import DEBUG

app = FastAPI(title="DTS Orchestrator", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"status":"ok","service":"orchestrator"}

@app.post("/tasks")
def create_task_endpoint(req: CreateTaskRequest):
    with SessionLocal() as session:
        scheduled_at = datetime.now(timezone.utc) + timedelta(seconds=req.delay_seconds)
        task_id = create_task(session, req.type, req.payload, req.priority, scheduled_at)
        task = get_task(session, task_id)
        return {"id": task_id, "task": dict(task)}

@app.get("/tasks")
def list_tasks_endpoint(limit: int = 50):
    with SessionLocal() as session:
        rows = list_tasks(session, limit=limit)
        return {"tasks":[dict(r) for r in rows]}

@app.get("/tasks/{task_id}")
def get_task_endpoint(task_id: str):
    with SessionLocal() as session:
        row = get_task(session, task_id)
        if not row:
            raise HTTPException(status_code=404, detail="Task not found")
        return dict(row)
