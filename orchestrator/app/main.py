
import uvicorn
from fastapi import FastAPI
from .api import router
from .db import engine, Base
from .settings import PORT, HEARTBEAT_TTL
from .background import RequeueThread

app = FastAPI(title="Distributed Task Scheduler Orchestrator", version="1.0.0")
app.include_router(router)

@app.on_event("startup")
def on_startup():
    # models are created by migrations; but creating again is harmless for local dev
    Base.metadata.create_all(bind=engine)
    RequeueThread(ttl_seconds=HEARTBEAT_TTL).start()

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=PORT, reload=False)
