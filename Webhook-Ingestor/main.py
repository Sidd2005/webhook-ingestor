import signal
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db import get_db, engine
from app.models import init_db
from app.storage import Storage

app = FastAPI(title="Webhook Ingestor")

@app.on_event("startup")
def startup():
    init_db()

@app.on_event("shutdown")
def shutdown():
    try:
        with engine.connect() as conn:
            conn.execute("PRAGMA wal_checkpoint(TRUNCATE);")
    finally:
        engine.dispose()

@app.post("/webhook")
def ingest_webhook(payload: dict, db: Session = Depends(get_db)):
    if "message_id" not in payload or "sender" not in payload:
        raise HTTPException(status_code=400, detail="Invalid payload")

    storage = Storage(db)
    msg = storage.upsert_message(
        message_id=payload["message_id"],
        sender=payload["sender"],
        payload=payload,
    )

    return {"status": "ok", "message_id": msg.message_id}

@app.get("/messages")
def list_messages(
    sender: str | None = None,
    q: str | None = None,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
):
    storage = Storage(db)
    total, messages = storage.get_messages(sender, q, limit, offset)

    return {
        "total": total,
        "items": messages,
    }

@app.get("/stats")
def stats(db: Session = Depends(get_db)):
    storage = Storage(db)
    return storage.get_stats()
