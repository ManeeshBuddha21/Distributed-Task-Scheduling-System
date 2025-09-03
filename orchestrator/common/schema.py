
from pydantic import BaseModel, Field
from typing import Any, Dict, Optional

class CreateTaskRequest(BaseModel):
    type: str = Field(..., examples=["demo.echo", "demo.fib", "demo.upper"])
    payload: Dict[str, Any] = Field(default_factory=dict)
    priority: int = Field(10, ge=0, le=100)
    delay_seconds: int = Field(0, ge=0)

class TaskOut(BaseModel):
    id: str
    type: str
    payload: Dict[str, Any]
    priority: int
    status: str
    result: Optional[Dict[str, Any]] = None
    scheduled_at: str
    created_at: str
    updated_at: str
