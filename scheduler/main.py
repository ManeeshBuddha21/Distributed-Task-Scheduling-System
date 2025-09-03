
import time
from datetime import datetime, timezone
import json
import redis

from common.db import SessionLocal, tasks, StatusEnum
from sqlalchemy import select, update, and_
from common.settings import REDIS_URL

QUEUE_KEY = "task_queue"
r = redis.from_url(REDIS_URL)

def once(batch_size: int = 50):
    now = datetime.now(timezone.utc)
    with SessionLocal() as session:
        # Find pending and due tasks ordered by priority then created_at
        stmt = (
            select(tasks)
            .where(and_(tasks.c.status == StatusEnum.pending, tasks.c.scheduled_at <= now))
            .order_by(tasks.c.priority.asc(), tasks.c.created_at.asc())
            .limit(batch_size)
        )
        rows = session.execute(stmt).mappings().all()
        for row in rows:
            # mark queued
            session.execute(
                update(tasks).where(tasks.c.id == row["id"]).values(status=StatusEnum.queued.value, updated_at=now)
            )
            payload = {
                "id": row["id"],
                "type": row["type"],
                "payload": row["payload"],
                "priority": row["priority"],
            }
            r.lpush(QUEUE_KEY, json.dumps(payload))
        session.commit()
        return len(rows)

def main():
    print("Scheduler started.")
    while True:
        try:
            n = once()
            if n:
                print(f"Queued {n} tasks")
            time.sleep(1)
        except Exception as e:
            print("Scheduler error:", e, flush=True)
            time.sleep(2)

if __name__ == "__main__":
    main()
