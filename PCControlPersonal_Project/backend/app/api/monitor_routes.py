from __future__ import annotations

import shutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

import psutil
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..auth import get_admin_or_access_key
from ..config import get_settings
from ..database import get_db
from ..models import Agent, LogEntry
from ..services.agent_service import compute_agent_status
from ..services.command_service import run_safe
from ..services.event_service import acknowledge_event, add_event, clear_old_events, list_events
from ..services.log_service import add_log
from ..services.metrics_service import collect_metric, latest_metric, metrics_history
from ..services.network_monitor_service import devices_from_neigh, mark_known, network_status, rename_device, scan_lan, traffic_stats
from ..services.notify_service import telegram_notify
from ..services.temperature_service import temperature_status


router = APIRouter(tags=["monitor"])
settings = get_settings()


def _service_active(name: str) -> bool:
    code, out = run_safe(["systemctl", "is-active", name], timeout=5)
    return code == 0 and out.strip() == "active"


def _api_ping_ok() -> bool:
    code, _ = run_safe(["curl", "-fsS", "http://127.0.0.1:8765/api/ping"], timeout=8)
    return code == 0


def _latest_backup_age_days() -> int | None:
    roots = [Path("/data/backups"), Path("/home/pc/backups")]
    backups: list[Path] = []
    for root in roots:
        try:
            if root.exists():
                backups.extend([p for p in root.glob("*.tar.gz") if p.is_file()])
        except PermissionError:
            continue
    if not backups:
        return None
    latest = max(backups, key=lambda p: p.stat().st_mtime)
    return int((datetime.utcnow() - datetime.utcfromtimestamp(latest.stat().st_mtime)).total_seconds() // 86400)


def _error_count(db: Session) -> int:
    since = datetime.utcnow() - timedelta(hours=24)
    return db.query(LogEntry).filter(LogEntry.created_at >= since, LogEntry.level.in_(["ERROR", "WARNING"])).count()


def compute_health_score(db: Session) -> dict[str, Any]:
    score = 100
    reasons: list[str] = []
    components: dict[str, str] = {}
    server_active = _service_active("pcmanager-server")
    bot_active = _service_active("pcmanager-bot")
    api_ok = _api_ping_ok()
    net = network_status()
    temp = temperature_status()
    disk = shutil.disk_usage("/")
    disk_percent = disk.used * 100 / disk.total if disk.total else 0
    backup_age = _latest_backup_age_days()
    agents = db.query(Agent).all()
    online_agents = [a for a in agents if compute_agent_status(a) == "online"]
    errors = _error_count(db)

    if not server_active:
        score -= 40; reasons.append("pcmanager-server не active")
    if not bot_active:
        score -= 15; reasons.append("pcmanager-bot не active")
    if not api_ok:
        score -= 35; reasons.append("/api/ping не отвечает")
    if not net.get("internet_ok"):
        score -= 20; reasons.append("интернет недоступен")
    if not net.get("router_ping", {}).get("ok"):
        score -= 10; reasons.append("роутер не отвечает на ping")
    if disk_percent > 95:
        score -= 30; reasons.append("диск заполнен больше 95%")
    elif disk_percent > 85:
        score -= 15; reasons.append("диск заполнен больше 85%")
    if temp.get("max_c") is not None and temp["max_c"] >= settings.temp_critical_c:
        score -= 30; reasons.append("температура CPU критическая")
    elif temp.get("max_c") is not None and temp["max_c"] >= settings.temp_warning_c:
        score -= 15; reasons.append("температура CPU высокая")
    if backup_age is None or backup_age > 7:
        score -= 10; reasons.append("backup старше 7 дней или отсутствует")
    if errors:
        score -= 10; reasons.append(f"есть ошибки в логах за 24ч: {errors}")
    if agents and not online_agents:
        score -= 10; reasons.append("Windows agent offline")

    components["network"] = "OK" if net.get("internet_ok") and net.get("router_ping", {}).get("ok") else "WARNING"
    components["disk"] = "OK" if disk_percent <= 85 else ("ERROR" if disk_percent > 95 else "WARNING")
    components["services"] = "OK" if server_active and api_ok else "ERROR"
    components["temperature"] = str(temp.get("status", "warning")).upper()
    components["backups"] = "OK" if backup_age is not None and backup_age <= 7 else "WARNING"
    components["bot"] = "OK" if bot_active else "WARNING"
    components["agent"] = "OK" if online_agents else ("WARNING" if agents else "WARNING")
    score = max(0, min(100, score))
    return {"score": score, "components": components, "reasons": reasons, "time": datetime.utcnow().isoformat()}


@router.get("/api/network/status")
def api_network_status():
    return network_status()


@router.get("/api/network/devices")
def api_network_devices():
    return {"devices": devices_from_neigh(update_store=True)}


@router.get("/api/network/traffic")
def api_network_traffic():
    return traffic_stats()


@router.post("/api/network/scan", dependencies=[Depends(get_admin_or_access_key)])
def api_network_scan(db: Session = Depends(get_db)):
    result = scan_lan()
    add_log(db, "INFO", "network", "lan_scan_completed", "LAN scan completed", {"devices": len(result.get("devices", []))})
    return result


@router.post("/api/network/devices/{device_id}/rename", dependencies=[Depends(get_admin_or_access_key)])
def api_device_rename(device_id: str, name: str, db: Session = Depends(get_db)):
    try:
        result = rename_device(device_id, name)
    except KeyError:
        raise HTTPException(status_code=404, detail="Device not found")
    add_log(db, "INFO", "network", "device_renamed", f"Device {device_id} renamed", {"device_id": device_id})
    return result


@router.post("/api/network/devices/{device_id}/mark-known", dependencies=[Depends(get_admin_or_access_key)])
def api_device_mark_known(device_id: str, db: Session = Depends(get_db)):
    try:
        result = mark_known(device_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Device not found")
    add_log(db, "INFO", "network", "device_marked_known", f"Device {device_id} marked known", {"device_id": device_id})
    return result


@router.get("/api/system/temperature")
def api_temperature():
    return temperature_status()


@router.get("/api/health-score")
def api_health_score(db: Session = Depends(get_db)):
    return compute_health_score(db)


@router.get("/api/metrics/latest")
def api_metrics_latest():
    return latest_metric()


@router.get("/api/metrics/history")
def api_metrics_history(range: str = Query(default="24h")):
    if range not in {"24h", "7d", "30d"}:
        raise HTTPException(status_code=400, detail="Invalid range")
    return {"range": range, "items": metrics_history(range)}


@router.post("/api/metrics/collect", dependencies=[Depends(get_admin_or_access_key)])
def api_metrics_collect(db: Session = Depends(get_db)):
    health = compute_health_score(db)
    item = collect_metric(health["score"])
    add_log(db, "INFO", "metrics", "metrics_collected", "Metrics collected manually", {})
    return item


@router.get("/api/events")
def api_events(severity: str | None = None, limit: int = 100):
    return {"events": list_events(limit=limit, severity=severity)}


@router.get("/api/events/latest")
def api_events_latest():
    return {"events": list_events(limit=50)}


@router.post("/api/events/acknowledge/{event_id}", dependencies=[Depends(get_admin_or_access_key)])
def api_event_ack(event_id: str):
    if not acknowledge_event(event_id):
        raise HTTPException(status_code=404, detail="Event not found")
    return {"ok": True}


@router.post("/api/events/clear-old", dependencies=[Depends(get_admin_or_access_key)])
def api_events_clear_old(days: int = 30):
    return {"removed": clear_old_events(days)}


@router.post("/api/maintenance/check-updates", dependencies=[Depends(get_admin_or_access_key)])
def maintenance_check_updates(db: Session = Depends(get_db)):
    code, out = run_safe(["bash", "-lc", "apt list --upgradable 2>/dev/null | tail -n +2"], timeout=60)
    add_log(db, "INFO", "maintenance", "updates_checked", "Ubuntu updates checked", {"code": code})
    return {"ok": code == 0, "updates": [line for line in out.splitlines() if line.strip()][:200]}


@router.post("/api/maintenance/cleanup-logs", dependencies=[Depends(get_admin_or_access_key)])
def maintenance_cleanup_logs(db: Session = Depends(get_db)):
    root = Path(settings.logs_dir)
    cutoff = datetime.utcnow() - timedelta(days=settings.log_retention_days)
    removed: list[str] = []
    if root.exists():
        for path in root.glob("*.log*"):
            if not path.is_file() or path.name in {"server.log", "bot.log", "errors.log"}:
                continue
            if datetime.utcfromtimestamp(path.stat().st_mtime) < cutoff:
                removed.append(str(path))
                path.unlink(missing_ok=True)
    add_log(db, "INFO", "maintenance", "logs_cleanup_completed", f"Old logs removed: {len(removed)}", {"removed": removed})
    add_event("cleanup_logs", "info", "Старые логи очищены", f"Удалено файлов: {len(removed)}", "maintenance")
    return {"removed": removed, "retention_days": settings.log_retention_days}


@router.post("/api/maintenance/cleanup-backups", dependencies=[Depends(get_admin_or_access_key)])
def maintenance_cleanup_backups(db: Session = Depends(get_db)):
    roots = [Path("/data/backups"), Path("/home/pc/backups")]
    all_backups: list[Path] = []
    for root in roots:
        if root.exists():
            all_backups.extend([p for p in root.glob("*.tar.gz") if p.is_file()])
    all_backups.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    keep = set(all_backups[: settings.backup_keep_last])
    cutoff = datetime.utcnow() - timedelta(days=settings.backup_retention_days)
    removed = []
    for path in all_backups:
        if path in keep:
            continue
        if datetime.utcfromtimestamp(path.stat().st_mtime) < cutoff:
            removed.append(str(path))
            path.unlink(missing_ok=True)
    add_log(db, "WARNING", "maintenance", "backups_cleanup_completed", f"Old backups removed: {len(removed)}", {"removed": removed})
    add_event("cleanup_backups", "info", "Старые backups очищены", f"Удалено файлов: {len(removed)}", "maintenance")
    return {"removed": removed, "keep_last": settings.backup_keep_last, "retention_days": settings.backup_retention_days}


@router.post("/api/maintenance/restart-backend", dependencies=[Depends(get_admin_or_access_key)])
def maintenance_restart_backend(db: Session = Depends(get_db)):
    add_log(db, "WARNING", "maintenance", "backend_restart_requested", "Backend restart requested", {})
    add_event("backend_restart", "warning", "Backend перезапускается", "Запрошен перезапуск pcmanager-server", "maintenance")
    telegram_notify("PC Manager\nBackend перезапускается с сайта")
    code, out = run_safe(["sudo", "-n", "systemctl", "restart", "pcmanager-server.service"], timeout=20)
    if code != 0:
        raise HTTPException(status_code=500, detail=out)
    return {"ok": True}


@router.post("/api/maintenance/restart-bot", dependencies=[Depends(get_admin_or_access_key)])
def maintenance_restart_bot(db: Session = Depends(get_db)):
    code, out = run_safe(["sudo", "-n", "systemctl", "restart", "pcmanager-bot.service"], timeout=20)
    add_log(db, "WARNING" if code == 0 else "ERROR", "maintenance", "bot_restart_requested", "Bot restart requested", {"code": code})
    add_event("bot_restart", "warning" if code == 0 else "error", "Bot restart", out or "pcmanager-bot restart requested", "maintenance")
    if code != 0:
        raise HTTPException(status_code=500, detail=out)
    return {"ok": True}


@router.post("/api/maintenance/check-all", dependencies=[Depends(get_admin_or_access_key)])
def maintenance_check_all(db: Session = Depends(get_db)):
    code, out = run_safe(["bash", "/home/pc/PCControlPersonal_Project/scripts/local_check.sh"], timeout=180)
    add_log(db, "INFO" if code == 0 else "WARNING", "maintenance", "full_check_completed", "Full local check completed", {"code": code})
    return {"ok": code == 0, "output": out[-5000:]}
