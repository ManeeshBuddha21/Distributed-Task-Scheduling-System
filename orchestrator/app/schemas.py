
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class TaskPayload(BaseModel):
    cmd: str

class TaskCreate(BaseModel):
    payload: TaskPayload
    priority: int = 0
    max_retries: int = 3

class JobCreate(BaseModel):
    name: str
    tasks: List[TaskCreate]

class JobOut(BaseModel):
    id: int
    name: str
    created_at: datetime

class TaskOut(BaseModel):
    id: int
    job_id: int
    status: str
    priority: int
    payload: Dict[str, Any]
    assigned_worker_id: Optional[str] = None

class WorkerRegister(BaseModel):
    id: str
    name: Optional[str] = None
    capabilities: Optional[Dict[str, Any]] = None

class ClaimRequest(BaseModel):
    worker_id: str

class TaskResult(BaseModel):
    result_text: str
