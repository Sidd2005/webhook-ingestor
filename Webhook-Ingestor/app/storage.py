import time
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, OperationalError
from sqlalchemy import text, String
from app.models import Message

class Storage:
    def __init__(self, db: Session):
        self.db = db

    def _retry(self, func, retries=3):
        for attempt in range(retries):
            try:
                return func()
            except OperationalError as e:
                if "database is locked" in str(e) and attempt < retries - 1:
                    time.sleep(0.1 * (2 ** attempt))
                    continue
                raise

    def upsert_message(self, message_id: str, sender: str, payload: dict):
        def operation():
            msg = Message(
                message_id=message_id,
                sender=sender,
                payload=payload,
            )
            self.db.add(msg)
            self.db.commit()
            return msg

        try:
            return self._retry(operation)
        except IntegrityError:
            self.db.rollback()
            return (
                self.db.query(Message)
                .filter(Message.message_id == message_id)
                .first()
            )

    def get_messages(
        self,
        sender: str | None = None,
        q: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ):
        query = self.db.query(Message)

        if sender:
            query = query.filter(Message.sender == sender)

        if q:
            query = query.filter(
                text("json_extract(payload, '$') LIKE :q")
                .bindparams(q=f"%{q}%", type_=String)
            )

        total = query.count()

        results = (
            query.order_by(Message.received_at.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )

        return total, results

    def get_stats(self):
        total = self.db.query(Message).count()

        per_sender = (
            self.db.query(Message.sender, text("COUNT(*) as count"))
            .group_by(Message.sender)
            .all()
        )

        return {
            "total_messages": total,
            "messages_per_sender": {
                sender: count for sender, count in per_sender
            },
        }
