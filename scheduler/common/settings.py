
import os

POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_DB = os.getenv("POSTGRES_DB", "tasks")
POSTGRES_USER = os.getenv("POSTGRES_USER", "tasks")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "tasks")
POSTGRES_PORT = int(os.getenv("POSTGRES_PORT", "5432"))

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
DEBUG = os.getenv("DEBUG", "0") == "1"
