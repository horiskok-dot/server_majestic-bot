import base64
import json
import shutil
import socket
import time
from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy.orm import Session

from ..auth import get_access_key_admin, get_admin_or_access_key, CurrentUser
from ..config import get_settings
from ..database import get_db
from ..models import Agent, FileAsset, LogEntry, Task
from ..schemas import HealthResponse, TaskCreate
from ..services.agent_service import compute_agent_status, list_agents
from ..services.log_service import add_log
from ..services.task_service import cancel_task, create_task, expire_running_tasks, finish_task, retry_task
from ..services.wol_service import list_wol_devices, wake_device


router = APIRouter(tags=["system"])
settings = get_settings()
STARTED_AT = time.time()


@router.get("/api/health", response_model=HealthResponse)
def health():
    return HealthResponse(status="ok", app=settings.app_name, version=settings.app_version, time=datetime.utcnow())


@router.get("/api/ping")
def ping():
    return {"ok": True, "app": settings.app_name, "version": settings.app_version, "time": datetime.utcnow().isoformat()}


def status_payload(db: Session, current_user: CurrentUser | None = None) -> dict:
    if current_user and not current_user.is_admin and current_user.user_id is not None:
        agents = db.query(Agent).filter(Agent.user_id == current_user.user_id).all()
    else:
        agents = list_agents(db)
        
    online_agents = [agent for agent in agents if compute_agent_status(agent) == "online"]
    primary = online_agents[0] if online_agents else (agents[0] if agents else None)
    sys_info = primary.system_info if primary else {}
    disk = primary.disk_info if primary else {}
    first_drive = (disk.get("drives") or [{}])[0] if isinstance(disk, dict) else {}
    return {
        "online": True,
        "serverStatus": "online",
        "hostName": primary.name if primary else "SERVER",
        "lastUpdate": int(time.time() * 1000),
        "agentVersion": primary.version if primary else settings.app_version,
        "cpu": float(sys_info.get("cpu_percent") or 0),
        "ram": float(sys_info.get("ram_percent") or 0),
        "disk": float(first_drive.get("percent") or 0),
        "temperature": None,
        "fps": None,
        "uptime": f"{int(time.time() - STARTED_AT)}s",
        "networkStatus": "online",
        "runningTask": primary.current_task if primary else "",
        "agentsTotal": len(agents),
        "agentsOnline": len(online_agents),
    }


@router.get("/api/status")
def status(db: Session = Depends(get_db), current_user: CurrentUser = Depends(get_access_key_admin)):
    expire_running_tasks(db)
    return status_payload(db, current_user)


@router.get("/api/system/status")
def legacy_status(db: Session = Depends(get_db), current_user: CurrentUser = Depends(get_access_key_admin)):
    expire_running_tasks(db)
    return status_payload(db, current_user)


@router.get("/api/system/metrics")
def legacy_metrics(db: Session = Depends(get_db), current_user: CurrentUser = Depends(get_access_key_admin)):
    data = status_payload(db, current_user)
    data["timestamp"] = int(time.time() * 1000)
    return data


def logs_payload(db: Session, current_user: CurrentUser | None = None) -> list[dict]:
    if current_user and not current_user.is_admin and current_user.user_id is not None:
        user_agents = db.query(Agent).filter(Agent.user_id == current_user.user_id).all()
        agent_ids = [a.agent_id for a in user_agents]
        all_items = db.query(LogEntry).order_by(LogEntry.created_at.desc()).limit(500).all()
        items = []
        for item in all_items:
            meta_val = item.meta or {}
            log_agent_id = meta_val.get("agent_id")
            if log_agent_id in agent_ids:
                items.append(item)
            if len(items) >= 100:
                break
    else:
        items = db.query(LogEntry).order_by(LogEntry.created_at.desc()).limit(100).all()
        
    return [
        {
            "id": str(item.id),
            "level": item.level,
            "message": item.message,
            "source": f"{item.source}/{item.event}",
            "timestamp": int(item.created_at.timestamp() * 1000),
        }
        for item in items
    ]


@router.get("/api/logs")
def logs(db: Session = Depends(get_db), current_user: CurrentUser = Depends(get_access_key_admin)):
    return logs_payload(db, current_user)


@router.get("/api/system/logs")
def legacy_logs(db: Session = Depends(get_db), current_user: CurrentUser = Depends(get_access_key_admin)):
    return logs_payload(db, current_user)


@router.get("/api/agents")
def api_agents(db: Session = Depends(get_db), current_user: CurrentUser = Depends(get_access_key_admin)):
    if not current_user.is_admin and current_user.user_id is not None:
        agents = db.query(Agent).filter(Agent.user_id == current_user.user_id).all()
    else:
        agents = list_agents(db)
    return [
        {
            "agent_id": agent.agent_id,
            "name": agent.name,
            "status": compute_agent_status(agent),
            "last_seen": agent.last_seen_at.isoformat() if agent.last_seen_at else None,
            "latency": agent.latency_ms,
            "version": agent.version,
            "current_task": agent.current_task,
            "last_error": agent.last_error,
        }
        for agent in agents
    ]


@router.get("/api/agents/{agent_id}")
def api_agent_detail(agent_id: str, db: Session = Depends(get_db), current_user: CurrentUser = Depends(get_access_key_admin)):
    query = db.query(Agent).filter(Agent.agent_id == agent_id)
    if not current_user.is_admin and current_user.user_id is not None:
        query = query.filter(Agent.user_id == current_user.user_id)
    agent = query.first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return {
        "agent_id": agent.agent_id,
        "name": agent.name,
        "status": compute_agent_status(agent),
        "hostname": agent.hostname,
        "username": agent.username,
        "os": agent.os_name,
        "version": agent.version,
        "local_ip": agent.local_ip,
        "public_ip": agent.public_ip,
        "connection_ip": agent.connection_ip,
        "last_seen": agent.last_seen_at.isoformat() if agent.last_seen_at else None,
        "latency": agent.latency_ms,
        "current_task": agent.current_task,
        "last_error": agent.last_error,
        "system_info": agent.system_info,
        "disk_info": agent.disk_info,
        "network_info": agent.network_info,
        "process_info": agent.process_info,
    }


@router.get("/api/agents/{agent_id}/status")
def api_agent_status(agent_id: str, db: Session = Depends(get_db), current_user: CurrentUser = Depends(get_access_key_admin)):
    return api_agent_detail(agent_id, db, current_user)


@router.get("/api/agents/{agent_id}/tasks")
def api_agent_tasks(agent_id: str, db: Session = Depends(get_db), current_user: CurrentUser = Depends(get_access_key_admin)):
    query = db.query(Agent).filter(Agent.agent_id == agent_id)
    if not current_user.is_admin and current_user.user_id is not None:
        query = query.filter(Agent.user_id == current_user.user_id)
    agent = query.first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return db.query(Task).filter(Task.agent_id == agent_id).order_by(Task.created_at.desc()).limit(100).all()


def _create_agent_task(agent_id: str, action: str, payload: dict | None, db: Session, current_user: CurrentUser) -> Task:
    query = db.query(Agent).filter(Agent.agent_id == agent_id)
    if not current_user.is_admin and current_user.user_id is not None:
        query = query.filter(Agent.user_id == current_user.user_id)
    agent = query.first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    try:
        task = create_task(db, agent, action, payload or {}, "web-api", confirmed=True)
        if not current_user.is_admin and current_user.user_id is not None:
            task.user_id = current_user.user_id
            db.add(task)
            db.commit()
        return task
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/api/agents/{agent_id}/screenshot")
def api_agent_screenshot(agent_id: str, db: Session = Depends(get_db), current_user: CurrentUser = Depends(get_admin_or_access_key)):
    return _create_agent_task(agent_id, "take_screenshot", {"save_to_server": True, "quality": 80}, db, current_user)


@router.post("/api/agents/{agent_id}/system-info")
def api_agent_system_info(agent_id: str, db: Session = Depends(get_db), current_user: CurrentUser = Depends(get_admin_or_access_key)):
    return _create_agent_task(agent_id, "get_system_info", {}, db, current_user)


@router.post("/api/agents/{agent_id}/ping")
def api_agent_ping(agent_id: str, db: Session = Depends(get_db), current_user: CurrentUser = Depends(get_admin_or_access_key)):
    return _create_agent_task(agent_id, "ping", {}, db, current_user)


@router.post("/api/agents/{agent_id}/disk-info")
def api_agent_disk_info(agent_id: str, db: Session = Depends(get_db), current_user: CurrentUser = Depends(get_admin_or_access_key)):
    return _create_agent_task(agent_id, "get_disk_info", {}, db, current_user)


@router.post("/api/agents/{agent_id}/logs")
def api_agent_logs(agent_id: str, db: Session = Depends(get_db), current_user: CurrentUser = Depends(get_admin_or_access_key)):
    return _create_agent_task(agent_id, "agent_logs", {}, db, current_user)


@router.post("/api/agents/{agent_id}/processes")
def api_agent_processes(agent_id: str, db: Session = Depends(get_db), current_user: CurrentUser = Depends(get_admin_or_access_key)):
    return _create_agent_task(agent_id, "get_process_list", {}, db, current_user)


@router.post("/api/agents/{agent_id}/restart-app")
def api_agent_restart_app(agent_id: str, app_name: str, db: Session = Depends(get_db), current_user: CurrentUser = Depends(get_admin_or_access_key)):
    if not app_name or any(token in app_name for token in ["\\", "/", "..", ";", "&", "|"]):
        raise HTTPException(status_code=400, detail="Invalid app name")
    return _create_agent_task(agent_id, "restart_allowed_app", {"app_name": app_name}, db, current_user)


@router.post("/api/agents/{agent_id}/input/key")
def api_agent_input_key(agent_id: str, key: str, duration_seconds: float = 2.0, db: Session = Depends(get_db), current_user: CurrentUser = Depends(get_admin_or_access_key)):
    clean_key = key.lower().strip()
    if clean_key not in {"w", "a", "s", "d", "z", "e", "esc", "space", "enter", "tab", "shift"}:
        raise HTTPException(status_code=400, detail="Key is not allowed")
    return _create_agent_task(agent_id, "press_key", {"key": clean_key, "duration_seconds": duration_seconds}, db, current_user)


@router.post("/api/agents/{agent_id}/input/click")
def api_agent_input_click(agent_id: str, preset: str, db: Session = Depends(get_db), current_user: CurrentUser = Depends(get_admin_or_access_key)):
    clean_preset = preset.lower().strip()
    if clean_preset not in {"play", "char1", "char2", "house", "spawn", "spawn2"}:
        raise HTTPException(status_code=400, detail="Click preset is not allowed")
    return _create_agent_task(agent_id, "click_preset", {"preset": clean_preset}, db, current_user)


@router.post("/api/agents/{agent_id}/input/release-keys")
def api_agent_release_keys(agent_id: str, db: Session = Depends(get_db), current_user: CurrentUser = Depends(get_admin_or_access_key)):
    return _create_agent_task(agent_id, "release_keys", {}, db, current_user)


def _cleanup_uploaded_agent_screenshots(db: Session, agent_id: str, keep_last: int) -> dict[str, int]:
    assets = (
        db.query(FileAsset)
        .filter(
            FileAsset.public_type == "agent_screenshot",
            FileAsset.agent_id == agent_id,
            FileAsset.is_active == True,  # noqa: E712
        )
        .order_by(FileAsset.created_at.desc())
        .all()
    )
    storage_root = Path(settings.storage_dir).resolve()
    removed = 0
    freed = 0
    for asset in assets[keep_last:]:
        try:
            path = Path(asset.stored_path).resolve()
            if str(path).startswith(str(storage_root)) and path.exists():
                size = path.stat().st_size
                path.unlink()
                freed += size
        except Exception as exc:
            add_log(db, "warning", "files", "agent_screenshot_cleanup_failed", str(exc), {"file_id": asset.id, "agent_id": agent_id})
        asset.is_active = False
        removed += 1
    if removed:
        db.commit()
        add_log(db, "info", "files", "agent_screenshots_cleaned", "Old uploaded agent screenshots cleaned", {"agent_id": agent_id, "removed": removed, "freed_bytes": freed, "keep_last": keep_last})
    return {"server_removed": removed, "server_freed_bytes": freed, "server_total_before": len(assets), "server_total_after": max(0, len(assets) - removed)}


@router.post("/api/agents/{agent_id}/cleanup-screenshots")
def api_agent_cleanup_screenshots(
    agent_id: str,
    keep_last: int = 10,
    force: bool = True,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_admin_or_access_key)
):
    clean_keep_last = max(0, min(keep_last, 200))
    # Verify agent ownership
    query = db.query(Agent).filter(Agent.agent_id == agent_id)
    if not current_user.is_admin and current_user.user_id is not None:
        query = query.filter(Agent.user_id == current_user.user_id)
    agent = query.first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
        
    server_cleanup = _cleanup_uploaded_agent_screenshots(db, agent_id, clean_keep_last)
    return _create_agent_task(
        agent_id,
        "cleanup_screenshots",
        {"force": force, "keep_last": clean_keep_last, "server_cleanup": server_cleanup},
        db,
        current_user
    )


@router.post("/api/agents/{agent_id}/desktop/{direction}")
def api_agent_desktop_switch(agent_id: str, direction: str, db: Session = Depends(get_db), current_user: CurrentUser = Depends(get_admin_or_access_key)):
    if direction not in {"left", "right", "new", "close"}:
        raise HTTPException(status_code=400, detail="Desktop direction must be left, right, new or close")
    return _create_agent_task(agent_id, f"desktop_{direction}", {}, db, current_user)


@router.post("/api/agents/{agent_id}/launch")
def api_agent_launch(agent_id: str, app_key: str = "majestic_launcher", db: Session = Depends(get_db), current_user: CurrentUser = Depends(get_admin_or_access_key)):
    clean_app = app_key.lower().strip()
    if clean_app not in {"majestic_launcher"}:
        raise HTTPException(status_code=400, detail="Launcher is not allowed")
    return _create_agent_task(agent_id, "launch_allowed_app", {"app_key": clean_app}, db, current_user)


@router.post("/api/agents/{agent_id}/open-url")
def api_agent_open_url(agent_id: str, url: str, db: Session = Depends(get_db), current_user: CurrentUser = Depends(get_admin_or_access_key)):
    if not (url.startswith("http://") or url.startswith("https://")) or any(ch.isspace() for ch in url):
        raise HTTPException(status_code=400, detail="Only http:// and https:// URLs are allowed")
    return _create_agent_task(agent_id, "open_url", {"url": url}, db, current_user)


@router.post("/api/agents/{agent_id}/volume/{direction}")
def api_agent_volume(agent_id: str, direction: str, db: Session = Depends(get_db), current_user: CurrentUser = Depends(get_admin_or_access_key)):
    if direction not in {"up", "down"}:
        raise HTTPException(status_code=400, detail="Invalid volume direction")
    return _create_agent_task(agent_id, f"volume_{direction}", {}, db, current_user)


@router.post("/api/agents/{agent_id}/game-status")
def api_agent_game_status(agent_id: str, db: Session = Depends(get_db), current_user: CurrentUser = Depends(get_admin_or_access_key)):
    return _create_agent_task(agent_id, "game_status", {}, db, current_user)


@router.post("/api/agents/{agent_id}/anti-afk/start")
def api_agent_anti_afk_start(agent_id: str, min_minutes: int = 10, max_minutes: int = 20, db: Session = Depends(get_db), current_user: CurrentUser = Depends(get_admin_or_access_key)):
    min_minutes = max(1, min(int(min_minutes), 120))
    max_minutes = max(min_minutes, min(int(max_minutes), 120))
    return _create_agent_task(agent_id, "anti_afk_start", {"min_minutes": min_minutes, "max_minutes": max_minutes}, db, current_user)


@router.post("/api/agents/{agent_id}/anti-afk/stop")
def api_agent_anti_afk_stop(agent_id: str, db: Session = Depends(get_db), current_user: CurrentUser = Depends(get_admin_or_access_key)):
    return _create_agent_task(agent_id, "anti_afk_stop", {}, db, current_user)


@router.post("/api/agents/{agent_id}/auto-screen/start")
def api_agent_auto_screen_start(agent_id: str, interval_seconds: int = 300, db: Session = Depends(get_db), current_user: CurrentUser = Depends(get_admin_or_access_key)):
    interval_seconds = max(60, min(int(interval_seconds), 3600))
    return _create_agent_task(agent_id, "auto_screen_start", {"interval_seconds": interval_seconds}, db, current_user)


@router.post("/api/agents/{agent_id}/auto-screen/stop")
def api_agent_auto_screen_stop(agent_id: str, db: Session = Depends(get_db), current_user: CurrentUser = Depends(get_admin_or_access_key)):
    return _create_agent_task(agent_id, "auto_screen_stop", {}, db, current_user)


@router.post("/api/agents/{agent_id}/automation-status")
def api_agent_automation_status(agent_id: str, db: Session = Depends(get_db), current_user: CurrentUser = Depends(get_admin_or_access_key)):
    return _create_agent_task(agent_id, "automation_status", {}, db, current_user)


@router.get("/api/tasks")
def api_tasks(db: Session = Depends(get_db), current_user: CurrentUser = Depends(get_access_key_admin)):
    expire_running_tasks(db)
    query = db.query(Task)
    if not current_user.is_admin and current_user.user_id is not None:
        query = query.filter(Task.user_id == current_user.user_id)
    return query.order_by(Task.created_at.desc()).limit(100).all()


@router.get("/api/tasks/{task_id}")
def api_task_detail(task_id: str, db: Session = Depends(get_db), current_user: CurrentUser = Depends(get_access_key_admin)):
    query = db.query(Task).filter(Task.task_id == task_id)
    if not current_user.is_admin and current_user.user_id is not None:
        query = query.filter(Task.user_id == current_user.user_id)
    task = query.first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.post("/api/tasks")
async def api_create_task(payload: TaskCreate, db: Session = Depends(get_db), current_user: CurrentUser = Depends(get_admin_or_access_key)):
    query = db.query(Agent).filter(Agent.agent_id == payload.agent_id)
    if not current_user.is_admin and current_user.user_id is not None:
        query = query.filter(Agent.user_id == current_user.user_id)
    agent = query.first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    action = payload.action or payload.task_type
    if not action:
        raise HTTPException(status_code=400, detail="Task action is required")
    task_payload = dict(payload.payload or {})
    if payload.timeout_seconds:
        task_payload["timeout_seconds"] = payload.timeout_seconds
    try:
        task = create_task(db, agent, action, task_payload, "web-api", payload.confirmed, payload.request_id)
        if not current_user.is_admin and current_user.user_id is not None:
            task.user_id = current_user.user_id
            db.add(task)
            db.commit()
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    add_log(db, "info", "task", "task_created", f"Task {task.task_id} created", {"task_id": task.task_id, "agent_id": agent.agent_id, "action": task.action})
    return task


@router.post("/api/tasks/{task_id}/cancel")
def api_cancel_task(task_id: str, db: Session = Depends(get_db), current_user: CurrentUser = Depends(get_admin_or_access_key)):
    query = db.query(Task).filter(Task.task_id == task_id)
    if not current_user.is_admin and current_user.user_id is not None:
        query = query.filter(Task.user_id == current_user.user_id)
    task = query.first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return cancel_task(db, task)


@router.post("/api/tasks/{task_id}/status")
def api_update_task_status(task_id: str, payload: dict, db: Session = Depends(get_db), current_user: CurrentUser = Depends(get_admin_or_access_key)):
    query = db.query(Task).filter(Task.task_id == task_id)
    if not current_user.is_admin and current_user.user_id is not None:
        query = query.filter(Task.user_id == current_user.user_id)
    task = query.first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    status = str(payload.get("status") or "running")
    result = str(payload.get("result") or "")
    error = str(payload.get("error") or "")
    updated = finish_task(db, task, status, result, error)
    add_log(db, "info", "task", "task_status", f"Task {task_id} -> {updated.status}", {"task_id": task_id, "agent_id": task.agent_id})
    return {"ok": True, "status": updated.status}


@router.post("/api/tasks/{task_id}/result")
def api_update_task_result(task_id: str, payload: dict, db: Session = Depends(get_db), current_user: CurrentUser = Depends(get_admin_or_access_key)):
    query = db.query(Task).filter(Task.task_id == task_id)
    if not current_user.is_admin and current_user.user_id is not None:
        query = query.filter(Task.user_id == current_user.user_id)
    task = query.first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    status = str(payload.get("status") or "failed")
    result = str(payload.get("result") or "")
    error = str(payload.get("error") or "")
    updated = finish_task(db, task, status, result, error)
    event = "task_done" if updated.status in {"success", "done"} else "task_failed"
    meta = {"task_id": task_id, "agent_id": task.agent_id, "request_id": task.request_id, "action": task.action}
    try:
        result_data = json.loads(updated.result or "{}")
        if isinstance(result_data, dict) and result_data.get("file_id"):
            meta["file_id"] = result_data.get("file_id")
    except Exception:
        pass
    add_log(db, "info" if updated.status in {"success", "done"} else "error", "task", event, f"Task {task_id} -> {updated.status}", meta)
    return {"ok": True, "status": updated.status}


@router.post("/api/tasks/{task_id}/retry")
def api_retry_task(task_id: str, db: Session = Depends(get_db), current_user: CurrentUser = Depends(get_admin_or_access_key)):
    query = db.query(Task).filter(Task.task_id == task_id)
    if not current_user.is_admin and current_user.user_id is not None:
        query = query.filter(Task.user_id == current_user.user_id)
    task = query.first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    try:
        return retry_task(db, task, "web")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/api/server/features")
def server_features(current_user: CurrentUser = Depends(get_admin_or_access_key)):
    return {
        "enable_server_screenshot": settings.enable_server_screenshot,
        "enable_server_webcam": settings.enable_server_webcam,
        "enable_server_webcam_video": settings.enable_server_webcam_video,
        "enable_agent_screenshot": settings.enable_screenshot,
        "enable_agent_camera": settings.enable_camera,
        "enable_agent_video_recording": settings.enable_video_recording,
        "enable_process_kill": settings.enable_process_kill,
        "local_only": settings.local_only,
        "trusted_origins": settings.trusted_origins,
        "base_public_url": settings.base_public_url,
        "max_server_webcam_video_seconds": settings.max_server_webcam_video_seconds,
        "tailscale_local_only_allowed": True,
        "wol_devices_count": len(list_wol_devices()) if current_user.is_admin else 0,
    }


@router.get("/api/diagnostics")
def diagnostics(db: Session = Depends(get_db), current_user: CurrentUser = Depends(get_admin_or_access_key)):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Diagnostics only available to admins")
    agents = list_agents(db)
    tasks_running = db.query(Task).filter(Task.status.in_(["queued", "pending", "running"])).count()
    logs_dir = Path(settings.logs_dir)
    storage_dir = Path(settings.storage_dir)
    data_dir = Path(settings.data_dir)

    def writable(path: Path) -> bool:
        try:
            path.mkdir(parents=True, exist_ok=True)
            test = path / ".write_test"
            test.write_text("ok", encoding="utf-8")
            test.unlink(missing_ok=True)
            return True
        except Exception:
            return False

    telegram_dns_ok = False
    telegram_dns_error = ""
    try:
        socket.gethostbyname("api.telegram.org")
        telegram_dns_ok = True
    except Exception as exc:
        telegram_dns_error = str(exc)

    return {
        "server": {
            "app": settings.app_name,
            "version": settings.app_version,
            "hostname": socket.gethostname(),
            "port": settings.server_port,
            "local_only": settings.local_only,
            "base_public_url": settings.base_public_url,
        },
        "telegram": {
            "enabled": settings.telegram_bot_enabled,
            "token_configured": bool(settings.telegram_bot_token),
            "owner_ids_configured": bool(settings.allowed_telegram_ids),
            "dns_ok": telegram_dns_ok,
            "dns_error": telegram_dns_error,
        },
        "storage": {
            "data_dir": str(data_dir),
            "logs_dir": str(logs_dir),
            "storage_dir": str(storage_dir),
            "data_writable": writable(data_dir),
            "logs_writable": writable(logs_dir),
            "storage_writable": writable(storage_dir),
            "free_mb": round(shutil.disk_usage(data_dir).free / 1024 / 1024, 1) if data_dir.exists() else None,
        },
        "agents": {
            "total": len(agents),
            "online": sum(1 for agent in agents if compute_agent_status(agent) == "online"),
        },
        "tasks": {
            "active": tasks_running,
        },
        "wol": {
            "devices_count": len(list_wol_devices()),
            "broadcast": settings.wol_broadcast,
            "port": settings.wol_port,
        },
    }


@router.get("/api/wol/devices")
def wol_devices(current_user: CurrentUser = Depends(get_admin_or_access_key)):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Wake-on-LAN only available to admins")
    return [{"name": device.name, "mac": device.mac} for device in list_wol_devices()]


@router.post("/api/wol/wake/{device_name}")
def wol_wake(device_name: str, db: Session = Depends(get_db), current_user: CurrentUser = Depends(get_admin_or_access_key)):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Wake-on-LAN only available to admins")
    try:
        result = wake_device(device_name)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except OSError as exc:
        raise HTTPException(status_code=500, detail=f"Не удалось отправить Wake-on-LAN пакет: {exc}") from exc
    add_log(db, "INFO", "server", "wol_wake", f"Wake-on-LAN отправлен для {device_name}", result)
    return result


@router.get("/api/media")
def api_media(db: Session = Depends(get_db), current_user: CurrentUser = Depends(get_admin_or_access_key)):
    media_types = {
        "server_screenshot",
        "agent_screenshot",
        "server_webcam_photo",
        "agent_camera_photo",
        "server_webcam_video",
        "agent_camera_video",
        "photo",
        "screenshot",
        "video",
    }
    query = db.query(FileAsset).filter(FileAsset.is_active == True, FileAsset.public_type.in_(media_types))
    if not current_user.is_admin and current_user.user_id is not None:
        user_agents = db.query(Agent).filter(Agent.user_id == current_user.user_id).all()
        agent_ids = [a.agent_id for a in user_agents]
        query = query.filter(FileAsset.agent_id.in_(agent_ids))
    return (
        query.order_by(FileAsset.created_at.desc())
        .limit(300)
        .all()
    )


def _first_agent(db: Session, current_user: CurrentUser) -> Agent:
    query = db.query(Agent)
    if not current_user.is_admin and current_user.user_id is not None:
        query = query.filter(Agent.user_id == current_user.user_id)
    agent = query.order_by(Agent.updated_at.desc()).first()
    if not agent:
        raise HTTPException(status_code=404, detail="No agents connected")
    return agent


@router.post("/api/system/optimize/quick")
def legacy_optimize_quick(db: Session = Depends(get_db), current_user: CurrentUser = Depends(get_access_key_admin)):
    agent = _first_agent(db, current_user)
    task = create_task(db, agent, "run_safe_script", {"script_name": "cleanup_temp"}, "android-legacy")
    if not current_user.is_admin and current_user.user_id is not None:
        task.user_id = current_user.user_id
        db.add(task)
        db.commit()
    return {"success": True, "message": f"Cleanup task queued: {task.task_id}", "cleanedMb": 0, "durationMs": 0}


@router.post("/api/system/optimize/deep")
def legacy_optimize_deep(db: Session = Depends(get_db), current_user: CurrentUser = Depends(get_access_key_admin)):
    agent = _first_agent(db, current_user)
    task = create_task(db, agent, "run_safe_script", {"script_name": "collect_diagnostics"}, "android-legacy")
    if not current_user.is_admin and current_user.user_id is not None:
        task.user_id = current_user.user_id
        db.add(task)
        db.commit()
    return {"success": True, "message": f"Diagnostics task queued: {task.task_id}", "cleanedMb": 0, "durationMs": 0}


@router.post("/api/system/optimize/temp")
def legacy_optimize_temp(db: Session = Depends(get_db), current_user: CurrentUser = Depends(get_access_key_admin)):
    return legacy_optimize_quick(db, current_user)


@router.post("/api/system/restart-agent")
def legacy_restart_agent(db: Session = Depends(get_db), current_user: CurrentUser = Depends(get_access_key_admin)):
    agent = _first_agent(db, current_user)
    task = create_task(db, agent, "restart_agent", {}, "android-legacy")
    if not current_user.is_admin and current_user.user_id is not None:
        task.user_id = current_user.user_id
        db.add(task)
        db.commit()
    return {"success": True, "message": f"Restart agent task queued: {task.task_id}"}


@router.post("/api/system/restart-pc")
def legacy_restart_pc(current_user: CurrentUser = Depends(get_access_key_admin)):
    raise HTTPException(status_code=403, detail="Dangerous command is disabled by default")


@router.post("/api/system/shutdown-pc")
def legacy_shutdown_pc(current_user: CurrentUser = Depends(get_access_key_admin)):
    raise HTTPException(status_code=403, detail="Dangerous command is disabled by default")


@router.get("/api/files")
def files(db: Session = Depends(get_db), current_user: CurrentUser = Depends(get_access_key_admin)):
    query = db.query(FileAsset).filter(FileAsset.is_active == True)
    if not current_user.is_admin and current_user.user_id is not None:
        user_agents = db.query(Agent).filter(Agent.user_id == current_user.user_id).all()
        agent_ids = [a.agent_id for a in user_agents]
        query = query.filter(FileAsset.agent_id.in_(agent_ids))
    return query.order_by(FileAsset.created_at.desc()).limit(300).all()  # noqa: E712


@router.get("/api/files/{file_id}")
def file_details(file_id: int, db: Session = Depends(get_db), current_user: CurrentUser = Depends(get_access_key_admin)):
    asset = db.query(FileAsset).filter(FileAsset.id == file_id, FileAsset.is_active == True).first()  # noqa: E712
    if not asset:
        raise HTTPException(status_code=404, detail="File not found")
    if not current_user.is_admin and current_user.user_id is not None:
        if asset.agent_id:
            agent = db.query(Agent).filter(Agent.agent_id == asset.agent_id, Agent.user_id == current_user.user_id).first()
            if not agent:
                raise HTTPException(status_code=403, detail="Access denied")
        else:
            raise HTTPException(status_code=403, detail="Access denied")
    return asset


@router.get("/api/mobile/screenshot")
def legacy_server_screen(db: Session = Depends(get_db), current_user: CurrentUser = Depends(get_access_key_admin)):
    query = db.query(Task).filter(Task.action == "get_screenshot", Task.status.in_(["success", "done"]))
    if not current_user.is_admin and current_user.user_id is not None:
        query = query.filter(Task.user_id == current_user.user_id)
    task = query.order_by(Task.finished_at.desc(), Task.created_at.desc()).first()
    if not task or not task.result:
        raise HTTPException(status_code=404, detail="Screenshot not available. Queue get_screenshot for an agent first.")
    try:
        payload = json.loads(task.result)
        content = base64.b64decode(payload["data"])
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Screenshot data is corrupted") from exc
    return Response(content=content, media_type=payload.get("mime_type", "image/png"))
