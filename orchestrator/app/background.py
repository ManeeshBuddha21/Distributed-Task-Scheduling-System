
import threading, time
from sqlalchemy.orm import Session
from .db import SessionLocal
from .crud import requeue_stale_inprogress

class RequeueThread(threading.Thread):
    def __init__(self, ttl_seconds: int):
        super().__init__(daemon=True)
        self.ttl_seconds = ttl_seconds

    def run(self):
        # purposely simple, we don't want a framework for one loop
        while True:
            try:
                db: Session = SessionLocal()
                requeue_stale_inprogress(db, self.ttl_seconds)
                db.close()
            except Exception as e:
                # keep going; log to stdout
                print(f"[background] requeue loop error: {e}")
            time.sleep(max(1, self.ttl_seconds // 2))
