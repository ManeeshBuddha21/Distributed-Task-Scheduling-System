
import json
import time
import redis
from common.db import SessionLocal, mark_task_status, StatusEnum
from common.settings import REDIS_URL
from tasks import do_echo, do_fib, do_upper

QUEUE_KEY = "task_queue"
r = redis.from_url(REDIS_URL)

def process(job):
    ttype = job.get("type")
    payload = job.get("payload", {})
    if ttype == "demo.echo":
        return do_echo(payload)
    if ttype == "demo.fib":
        return do_fib(payload)
    if ttype == "demo.upper":
        return do_upper(payload)
    return {"info": "no-op", "type": ttype}

def main():
    print("Worker started.")
    while True:
        try:
            res = r.brpop(QUEUE_KEY, timeout=5)
            if not res:
                continue
            _, data = res
            job = json.loads(data.decode("utf-8"))
            task_id = job["id"]
            with SessionLocal() as session:
                mark_task_status(session, task_id, StatusEnum.processing)
                try:
                    result = process(job)
                    mark_task_status(session, task_id, StatusEnum.done, result=result)
                    print(f"Processed {task_id} -> {result}")
                except Exception as e:
                    mark_task_status(session, task_id, StatusEnum.failed, result={"error": str(e)})
                    print("Worker error:", e, flush=True)
        except Exception as e:
            print("Loop error:", e, flush=True)
            time.sleep(1)

if __name__ == "__main__":
    main()
