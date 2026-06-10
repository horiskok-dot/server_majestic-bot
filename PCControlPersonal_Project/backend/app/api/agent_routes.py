import json
from datetime import datetime

from fastapi import APIRouter, Depends, File, Header, HTTPException, Request, UploadFile
from sqlalchemy.orm import Session

from ..auth import get_admin_or_access_key, get_agent_from_token
from ..config import get_settings
from ..database import get_db
from ..models import Agent, Task, User, ActivationKey
from ..schemas import AgentHeartbeatRequest, AgentRegisterRequest, TaskResultUpdate, AgentActivateRequest
from ..services.agent_service import compute_agent_status, ensure_agent, update_heartbeat
from ..services.file_service import create_asset_from_upload
from ..services.log_service import add_log
from ..services.task_service import finish_task, next_task
from ..websocket.manager import ws_manager


router = APIRouter(prefix="/api/agents", tags=["agents"])
settings = get_settings()


def _agent_public_payload(agent: Agent) -> dict:
    return {
        "agent_id": agent.agent_id,
        "name": agent.name,
        "status": compute_agent_status(agent),
        "version": agent.version,
        "hostname": agent.hostname,
        "username": agent.username,
        "os": agent.os_name,
        "local_ip": agent.local_ip,
        "public_ip": agent.public_ip,
        "connection_ip": agent.connection_ip,
        "latency_ms": agent.latency_ms,
        "current_task": agent.current_task,
        "last_error": agent.last_error,
        "last_seen": agent.last_seen_at.isoformat() if agent.last_seen_at else None,
    }


@router.post("/register")
async def register(
    payload: AgentRegisterRequest,
    request: Request,
    db: Session = Depends(get_db),
    x_agent_token: str = Header(default="", alias="X-Agent-Token"),
):
    if x_agent_token != settings.agent_bootstrap_token:
        raise HTTPException(status_code=403, detail="Bootstrap token invalid")
    data = payload.model_dump()
    data["connection_ip"] = request.client.host if request.client else ""
    agent = ensure_agent(db, payload.agent_id, data)
    agent.connection_ip = data["connection_ip"]
    db.add(agent)
    db.commit()
    add_log(db, "info", "agent", "agent_registered", f"Agent {agent.agent_id} registered", {"agent_id": agent.agent_id})
    await ws_manager.broadcast("status", "agent_online", {"agent_id": agent.agent_id, "name": agent.name})
    return {"registered": True, "agent_id": agent.agent_id, "agent_token": agent.agent_token}


@router.post("/heartbeat")
async def heartbeat(
    payload: AgentHeartbeatRequest,
    request: Request,
    agent: Agent = Depends(get_agent_from_token),
    db: Session = Depends(get_db),
):
    agent.connection_ip = request.client.host if request.client else agent.connection_ip
    previous, updated = update_heartbeat(db, agent, payload.model_dump())
    if previous != "online":
        add_log(db, "info", "agent", "agent_online", f"Agent {updated.agent_id} is online", {"agent_id": updated.agent_id})
        await ws_manager.broadcast("status", "agent_online", {"agent_id": updated.agent_id, "name": updated.name})
    return {"ok": True, "server_time": datetime.utcnow().isoformat(), "status": compute_agent_status(updated)}


@router.post("/{agent_id}/heartbeat", dependencies=[Depends(get_admin_or_access_key)])
async def heartbeat_by_agent_id(
    agent_id: str,
    payload: AgentHeartbeatRequest,
    request: Request,
    db: Session = Depends(get_db),
):
    agent = db.query(Agent).filter(Agent.agent_id == agent_id).first()
    if not agent:
        defaults = {
            "name": agent_id,
            "version": payload.system_info.get("agent_version") or "unknown",
            "platform": payload.system_info.get("platform") or "Windows",
            "hostname": payload.system_info.get("hostname") or agent_id,
            "username": payload.system_info.get("username") or "",
            "os_name": payload.system_info.get("os") or payload.system_info.get("platform") or "Windows",
            "local_ip": payload.network_info.get("ip") or "",
            "screenshot_enabled": True,
        }
        agent = ensure_agent(db, agent_id, defaults)
    agent.connection_ip = request.client.host if request.client else agent.connection_ip
    previous, updated = update_heartbeat(db, agent, payload.model_dump())
    if previous != "online":
        add_log(db, "info", "agent", "agent_online", f"Agent {updated.agent_id} is online", {"agent_id": updated.agent_id})
        await ws_manager.broadcast("status", "agent_online", {"agent_id": updated.agent_id, "name": updated.name})
    await ws_manager.broadcast("status", "agent_updated", _agent_public_payload(updated))
    return {"ok": True, "server_time": datetime.utcnow().isoformat(), "status": compute_agent_status(updated)}


@router.post("/{agent_id}/status", dependencies=[Depends(get_admin_or_access_key)])
async def status_by_agent_id(
    agent_id: str,
    payload: AgentHeartbeatRequest,
    request: Request,
    db: Session = Depends(get_db),
):
    return await heartbeat_by_agent_id(agent_id, payload, request, db)


@router.get("/tasks/next")
async def get_next_task(agent: Agent = Depends(get_agent_from_token), db: Session = Depends(get_db)):
    task = next_task(db, agent)
    if not task:
        return {"task": None}
    add_log(db, "info", "task", "task_started", f"Task {task.task_id} started", {"task_id": task.task_id, "request_id": task.request_id, "agent_id": task.agent_id})
    await ws_manager.broadcast("status", "task_started", {"task_id": task.task_id, "request_id": task.request_id, "agent_id": task.agent_id, "action": task.action})
    return {"task": {"task_id": task.task_id, "request_id": task.request_id, "action": task.action, "payload": task.payload}}


@router.get("/{agent_id}/tasks/next", dependencies=[Depends(get_admin_or_access_key)])
async def get_next_task_by_agent_id(agent_id: str, db: Session = Depends(get_db)):
    agent = db.query(Agent).filter(Agent.agent_id == agent_id).first()
    if not agent:
        return {"task": None}
    task = next_task(db, agent)
    if not task:
        return {"task": None}
    add_log(db, "info", "task", "task_started", f"Task {task.task_id} started", {"task_id": task.task_id, "request_id": task.request_id, "agent_id": task.agent_id})
    await ws_manager.broadcast("status", "task_started", {"task_id": task.task_id, "request_id": task.request_id, "agent_id": task.agent_id, "action": task.action})
    return {"task": {"task_id": task.task_id, "request_id": task.request_id, "action": task.action, "task_type": task.action, "payload": task.payload, "timeout_seconds": task.timeout_seconds}}


@router.post("/tasks/{task_id}/result")
async def result(
    task_id: str,
    payload: TaskResultUpdate,
    agent: Agent = Depends(get_agent_from_token),
    db: Session = Depends(get_db),
):
    task = db.query(Task).filter(Task.task_id == task_id, Task.agent_id == agent.agent_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    updated = finish_task(db, task, payload.status, payload.result, payload.error)
    event = "task_done" if updated.status in {"success", "done"} else "task_failed"
    meta = {"task_id": updated.task_id, "request_id": updated.request_id, "agent_id": updated.agent_id, "action": updated.action}
    try:
        result_data = json.loads(updated.result or "{}")
        if isinstance(result_data, dict) and result_data.get("file_id"):
            meta["file_id"] = result_data.get("file_id")
    except Exception:
        pass
    add_log(db, "info" if updated.status in {"success", "done"} else "error", "task", event, f"Task {updated.task_id} -> {updated.status}", meta)
    await ws_manager.broadcast("status", event, {"task_id": updated.task_id, "agent_id": updated.agent_id, "status": updated.status})
    return {"ok": True}


@router.post("/{agent_id}/screenshot/upload", dependencies=[Depends(get_admin_or_access_key)])
async def upload_agent_screenshot(
    agent_id: str,
    upload: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    agent = db.query(Agent).filter(Agent.agent_id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    asset = await create_asset_from_upload(db, upload, "agent_screenshot", "agent", agent_id=agent_id, description="Windows agent screenshot")
    add_log(db, "info", "agent", "agent_screenshot_uploaded", f"Screenshot uploaded by {agent_id}", {"agent_id": agent_id, "file_id": asset.id})
    await ws_manager.broadcast("status", "screenshot_created", {"agent_id": agent_id, "file_id": asset.id})
    return {"ok": True, "file_id": asset.id, "filename": asset.filename}


@router.post("/activate")
async def activate_agent(
    payload: AgentActivateRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    key_entry = db.query(ActivationKey).filter(ActivationKey.key == payload.activation_key.strip(), ActivationKey.is_used == False).first()
    if not key_entry:
        raise HTTPException(status_code=400, detail="Неверный или уже использованный ключ активации.")
    
    import secrets
    import uuid
    
    agent_id = f"pc-{str(uuid.uuid4())[:8]}"
    agent_token = secrets.token_urlsafe(32)
    
    defaults = {
        "name": f"ПК {payload.hostname or 'Без имени'}",
        "version": "1.6.0",
        "platform": payload.platform,
        "hostname": payload.hostname,
        "username": payload.username,
        "os_name": payload.os_name,
        "local_ip": payload.local_ip,
        "screenshot_enabled": True,
    }
    
    agent = ensure_agent(db, agent_id, defaults)
    agent.agent_token = agent_token
    agent.user_id = key_entry.user_id
    
    key_entry.is_used = True
    db.add(agent)
    db.add(key_entry)
    db.commit()
    
    add_log(db, "info", "agent", "agent_activated", f"Agent {agent_id} activated using key {payload.activation_key}", {"agent_id": agent_id, "user_id": key_entry.user_id})
    await ws_manager.broadcast("status", "agent_online", {"agent_id": agent_id, "name": agent.name})
    
    # Clean URL logic (removes api prefix path if base_url is used)
    server_url = str(request.base_url).rstrip("/")
    
    return {
        "ok": True,
        "agent_id": agent_id,
        "agent_token": agent_token,
        "server_url": server_url
    }
