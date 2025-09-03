
import os

DB_URL = os.environ.get("ORCH_DB_URL", "postgresql+psycopg2://scheduler:changeme@localhost:5432/schedulerdb")
PORT = int(os.environ.get("ORCH_PORT", "8080"))
HEARTBEAT_TTL = int(os.environ.get("TASK_HEARTBEAT_TTL_SECONDS", "60"))
