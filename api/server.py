import os
import uuid
import json
import time
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from dotenv import load_dotenv
import psycopg2

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://scheduler:scheduler@localhost:5432/scheduler")
QUEUE_DIR = Path(os.getenv("QUEUE_DIR", Path(__file__).resolve().parent.parent / "queue"))
COMPLETED_DIR = Path(os.getenv("COMPLETED_DIR", Path(__file__).resolve().parent.parent / "completed"))
for d in (QUEUE_DIR, COMPLETED_DIR):
    d.mkdir(parents=True, exist_ok=True)

def db():
    return psycopg2.connect(DATABASE_URL)

class SubmitBody(BaseModel):
    name: str = Field(..., example="matrix-mul")
    priority: str = Field(..., regex="^(HIGH|MED|LOW)$")
    type: str = Field(..., regex="^(ml|system)$")
    duration_ms: int = Field(..., gt=0)

app = FastAPI(title="Distributed Scheduler API")

@app.get("/health")
def health():
    # naive counters from dirs
    queued = len(list(QUEUE_DIR.glob("*.task")))
    completed = len(list(COMPLETED_DIR.glob("*.done")))
    try:
        with db() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT COUNT(*) FROM tasks WHERE status='queued';")
                db_queued = cur.fetchone()[0]
    except Exception as e:
        db_queued = -1
    return {"status":"ok","queue_files":queued,"completed_files":completed,"db_queued":db_queued}

@app.post("/submit")
def submit_task(body: SubmitBody):
    task_id = str(uuid.uuid4())
    now_ms = int(time.time() * 1000)
    # Write DB
    try:
        with db() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO tasks (id, name, priority, type, duration_ms, status) VALUES (%s,%s,%s,%s,%s,'queued')",
                    (task_id, body.name, body.priority, body.type, body.duration_ms)
                )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"DB error: {e}")

    # Mirror to .task file for the C++ scheduler
    task_file = QUEUE_DIR / f"{task_id}.task"
    content = [
        f"id:{task_id}",
        f"name:{body.name}",
        f"priority:{body.priority}",
        f"type:{body.type}",
        f"duration_ms:{body.duration_ms}",
        "attempts:0",
        f"created_at_ms:{now_ms}"
    ]
    task_file.write_text("\n".join(content), encoding="utf-8")
    return {"id": task_id}
