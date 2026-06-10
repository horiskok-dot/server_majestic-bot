from __future__ import annotations

import json
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

from ..config import get_settings
from .notify_service import telegram_notify


def events_path() -> Path:
    path = Path(get_settings().data_dir) / "events.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def add_event(event_type: str, severity: str, title: str, message: str, source: str = "server", metadata: dict[str, Any] | None = None) -> dict[str, Any]:
    event = {
        "event_id": uuid.uuid4().hex,
        "time": datetime.utcnow().isoformat(),
        "type": event_type,
        "severity": severity,
        "title": title,
        "message": message,
        "source": source,
        "metadata": metadata or {},
        "acknowledged": False,
    }
    with events_path().open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(event, ensure_ascii=False) + "\n")
    settings = get_settings()
    if settings.telegram_notify_events and (severity in {"warning", "error", "critical"} or settings.telegram_notify_info):
        telegram_notify(f"PC Manager Event\n{severity.upper()}: {title}\n{message[:900]}")
    return event


def list_events(limit: int = 100, severity: str | None = None) -> list[dict[str, Any]]:
    path = events_path()
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        try:
            item = json.loads(line)
        except Exception:
            continue
        if severity and item.get("severity") != severity:
            continue
        rows.append(item)
    return rows[-limit:][::-1]


def acknowledge_event(event_id: str) -> bool:
    path = events_path()
    changed = False
    rows = []
    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines() if path.exists() else []:
        try:
            item = json.loads(line)
            if item.get("event_id") == event_id:
                item["acknowledged"] = True
                changed = True
            rows.append(item)
        except Exception:
            continue
    if changed:
        path.write_text("\n".join(json.dumps(x, ensure_ascii=False) for x in rows) + "\n", encoding="utf-8")
    return changed


def clear_old_events(days: int = 30) -> int:
    path = events_path()
    if not path.exists():
        return 0
    cutoff = datetime.utcnow() - timedelta(days=days)
    kept = []
    removed = 0
    for event in list_events(limit=100000):
        try:
            when = datetime.fromisoformat(str(event.get("time", "")))
        except Exception:
            when = datetime.utcnow()
        if when < cutoff:
            removed += 1
        else:
            kept.append(event)
    path.write_text("\n".join(json.dumps(x, ensure_ascii=False) for x in reversed(kept)) + ("\n" if kept else ""), encoding="utf-8")
    return removed

