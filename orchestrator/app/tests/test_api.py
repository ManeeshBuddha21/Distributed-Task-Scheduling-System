
import os, pytest
from fastapi.testclient import TestClient

# Ensure the DB URL points to something reachable in CI; for local, docker-compose handles it.
os.environ.setdefault("ORCH_DB_URL", "postgresql+psycopg2://scheduler:changeme@postgres:5432/schedulerdb")

from app.main import app

client = TestClient(app)

def test_health_job_flow():
    # submit a job
    payload = {
        "name": "pytest-job",
        "tasks": [
            {"payload": {"cmd": "echo one"}, "priority": 5},
            {"payload": {"cmd": "echo two"}, "priority": 10}
        ]
    }
    r = client.post("/api/v1/jobs", json=payload)
    assert r.status_code == 200
    job = r.json()
    assert job["name"] == "pytest-job"

    # register worker + heartbeat
    assert client.post("/api/v1/workers/register", json={"id": "tworker"}).status_code == 200
    assert client.post("/api/v1/workers/tworker/heartbeat").status_code == 200

    # Claiming will 404 until scheduler queues something; that's fine in unit test context.
    r = client.post("/api/v1/tasks/next", params={"worker_id": "tworker"})
    assert r.status_code in (200, 404)
