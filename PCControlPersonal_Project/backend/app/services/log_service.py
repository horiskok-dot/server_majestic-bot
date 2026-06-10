from datetime import datetime

from sqlalchemy.orm import Session

from ..models import LogEntry
from ..utils.logging import append_json_log


def add_log(db: Session, level: str, source: str, event: str, message: str, meta: dict | None = None) -> LogEntry:
    entry = LogEntry(level=level.upper(), source=source, event=event, message=message, meta=meta or {})
    db.add(entry)
    db.commit()
    db.refresh(entry)
    append_json_log(
        f"{source}.jsonl",
        {"time": datetime.utcnow().isoformat(), "level": entry.level, "event": event, "message": message, "meta": meta or {}},
    )
    return entry
