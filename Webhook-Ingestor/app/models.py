from sqlalchemy import Column, String, DateTime, Index, JSON
from sqlalchemy.orm import declarative_base
from datetime import datetime
from pathlib import Path
from app.db import engine

Base = declarative_base()

class Message(Base):
    __tablename__ = "messages"

    message_id = Column(String, primary_key=True, index=True)
    sender = Column(String, index=True, nullable=False)
    received_at = Column(DateTime(timezone=True), index=True, default=datetime.utcnow)
    payload = Column(JSON, nullable=False)

    __table_args__ = (
        Index("ix_sender_received_at", "sender", "received_at"),
        Index("ix_received_at_message_id", "received_at", "message_id"),
    )

def init_db():
    Path(engine.url.database).parent.mkdir(parents=True, exist_ok=True)
    Base.metadata.create_all(bind=engine)
