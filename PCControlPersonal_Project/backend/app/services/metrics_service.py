from __future__ import annotations

import json
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

import psutil

from ..config import get_settings
from .network_monitor_service import network_status
from .temperature_service import temperature_status


def metrics_path() -> Path:
    path = Path(get_settings().data_dir) / "metrics.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def collect_metric(health_score: int | None = None) -> dict[str, Any]:
    disk = shutil.disk_usage("/")
    net = network_status()
    temp = temperature_status()
    item = {
        "time": datetime.utcnow().isoformat(),
        "cpu_percent": psutil.cpu_percent(interval=0.2),
        "ram_percent": psutil.virtual_memory().percent,
        "disk_percent": round(disk.used * 100 / disk.total, 1) if disk.total else 0,
        "temperature_c": temp.get("max_c"),
        "router_ping_ms": net.get("router_ping", {}).get("ms"),
        "google_ping_ms": net.get("google_ping", {}).get("ms"),
        "cloudflare_ping_ms": net.get("cloudflare_ping", {}).get("ms"),
        "internet_ok": bool(net.get("internet_ok")),
        "traffic_rx": net.get("traffic", {}).get("rx_bytes", 0),
        "traffic_tx": net.get("traffic", {}).get("tx_bytes", 0),
        "health_score": health_score,
    }
    with metrics_path().open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(item, ensure_ascii=False) + "\n")
    prune_metrics()
    return item


def _read_metrics() -> list[dict[str, Any]]:
    path = metrics_path()
    if not path.exists():
        return []
    rows = []
    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        try:
            rows.append(json.loads(line))
        except Exception:
            continue
    return rows


def latest_metric() -> dict[str, Any]:
    rows = _read_metrics()
    return rows[-1] if rows else collect_metric()


def metrics_history(range_value: str = "24h") -> list[dict[str, Any]]:
    now = datetime.utcnow()
    delta = timedelta(hours=24)
    if range_value == "7d":
        delta = timedelta(days=7)
    elif range_value == "30d":
        delta = timedelta(days=30)
    cutoff = now - delta
    result = []
    for item in _read_metrics():
        try:
            when = datetime.fromisoformat(str(item.get("time", "")))
        except Exception:
            continue
        if when >= cutoff:
            result.append(item)
    return result[-2000:]


def prune_metrics() -> int:
    settings = get_settings()
    cutoff = datetime.utcnow() - timedelta(days=settings.metrics_retention_days)
    kept = []
    removed = 0
    for item in _read_metrics():
        try:
            when = datetime.fromisoformat(str(item.get("time", "")))
        except Exception:
            when = datetime.utcnow()
        if when < cutoff:
            removed += 1
        else:
            kept.append(item)
    metrics_path().write_text("\n".join(json.dumps(x, ensure_ascii=False) for x in kept) + ("\n" if kept else ""), encoding="utf-8")
    return removed

