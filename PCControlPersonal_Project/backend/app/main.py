from datetime import datetime
import ipaddress
from pathlib import Path

import time
from collections import defaultdict, deque

from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect, Header, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session


from .api.agent_routes import router as agent_router
from .api.auth_routes import router as auth_router
from .api.camera import router as camera_router
from .api.files import router as files_router
from .api.home_routes import router as home_router
from .api.mobile_routes import router as mobile_router
from .api.monitor_routes import router as monitor_router
from .api.processes import router as processes_router
from .api.screenshots import router as screenshots_router
from .api.server import router as server_info_router
from .api.system_routes import router as system_router
from .auth import get_current_admin_ws, verify_server_access_key
from .config import get_settings
from .database import Base, SessionLocal, engine, ensure_database_schema, get_db
from .models import Agent, Task
from .services.agent_service import compute_agent_status, update_heartbeat
from .services.log_service import add_log
from .services.task_service import finish_task, next_task, create_task

from .utils.logging import setup_logging
from .websocket.manager import ws_manager


settings = get_settings()
setup_logging()
RATE_BUCKETS: dict[str, deque[float]] = defaultdict(deque)
TAILSCALE_NETWORK = ipaddress.ip_network("100.64.0.0/10")

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Personal PC control server with REST API, WebSocket, Telegram bot and agent queue.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.trusted_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    # Public paths — always accessible, even in local_only mode (needed for Google, bots, etc.)
    public_paths = {
        "/", "/panel", "/manifest.json", "/service-worker.js", "/favicon.ico",
        "/api/health", "/api/ping", "/robots.txt", "/sitemap.xml", "/sitemap",
        "/pcmanager.online/sitemap.xml", "/https://pcmanager.online/sitemap.xml",
        "/http://pcmanager.online/sitemap.xml", "/www.pcmanager.online/sitemap.xml",
        "/https://www.pcmanager.online/sitemap.xml",
        "/api/agents/version/latest", "/releases/agent.exe", "/releases/PCManager_Agent.exe"
    }
    if request.url.path in public_paths or request.url.path.startswith("/assets/"):
        return await call_next(request)

    is_allowed_local = False
    if settings.local_only and request.client:
        try:
            client_ip = ipaddress.ip_address(request.client.host)
            is_allowed_local = client_ip.is_loopback or client_ip.is_private or client_ip in TAILSCALE_NETWORK
            if not is_allowed_local:
                from fastapi.responses import JSONResponse
                return JSONResponse({"detail": "Server is in LOCAL_ONLY mode"}, status_code=403)
        except ValueError:
            from fastapi.responses import JSONResponse
            return JSONResponse({"detail": "Invalid client address"}, status_code=403)
    elif request.client:
        try:
            client_ip = ipaddress.ip_address(request.client.host)
            is_allowed_local = client_ip.is_loopback or client_ip.is_private or client_ip in TAILSCALE_NETWORK
        except ValueError:
            is_allowed_local = False
    if is_allowed_local:
        return await call_next(request)
    client_ip = request.client.host if request.client else "unknown"
    token = request.headers.get("x-api-key") or request.headers.get("x-agent-token") or request.headers.get("x-server-access-key") or ""
    bucket_key = f"{client_ip}:{token}" if token else client_ip
    bucket = RATE_BUCKETS[bucket_key]

    now = time.time()
    while bucket and now - bucket[0] > 60:
        bucket.popleft()
    limit = min(settings.api_rate_limit_per_minute, 40)
    if len(bucket) >= limit:
        from fastapi.responses import JSONResponse
        return JSONResponse({"detail": "Rate limit exceeded"}, status_code=429)
    bucket.append(now)
    return await call_next(request)


app.include_router(home_router)
app.include_router(monitor_router)
app.include_router(system_router)
app.include_router(auth_router)
app.include_router(mobile_router)
app.include_router(agent_router)
app.include_router(files_router)
app.include_router(server_info_router)
app.include_router(processes_router)
app.include_router(screenshots_router)
app.include_router(camera_router)
# Minecraft integrations removed




class BotCommandPayload(BaseModel):
    agent_id: str
    action: str
    payload: dict = {}

@app.get("/api/agent/poll")
async def agent_poll(
    x_api_key: str = Header(default="", alias="X-API-Key"),
    x_agent_token: str = Header(default="", alias="X-Agent-Token"),
    db: Session = Depends(get_db)
):
    token = x_api_key or x_agent_token
    if not token:
        raise HTTPException(status_code=401, detail="API Key or Agent Token is missing")
    
    agent = db.query(Agent).filter(Agent.agent_token == token).first()
    if not agent and token != settings.server_access_key:
        raise HTTPException(status_code=403, detail="Invalid API Key or Agent Token")
    
    if agent:
        task = next_task(db, agent)
        if task:
            return {
                "status": "ok",
                "task": {
                    "task_id": task.task_id,
                    "action": task.action,
                    "payload": task.payload
                }
            }
    return {"status": "ok", "task": None}

@app.post("/api/bot/send_command")
async def bot_send_command(
    req: BotCommandPayload,
    x_api_key: str = Header(default="", alias="X-API-Key"),
    x_server_access_key: str = Header(default="", alias="X-Server-Access-Key"),
    db: Session = Depends(get_db)
):
    token = x_api_key or x_server_access_key
    if not token or token not in {settings.server_access_key, settings.admin_token}:
        raise HTTPException(status_code=403, detail="Invalid or missing Access Key")
    
    agent = db.query(Agent).filter(Agent.agent_id == req.agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    try:
        task = create_task(db, agent, req.action, req.payload, created_by="bot", confirmed=True)
        return {"status": "ok", "task_id": task.task_id, "action": task.action}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.on_event("startup")

def startup_event() -> None:
    Base.metadata.create_all(bind=engine)
    ensure_database_schema()
    if settings.start_telegram_bot_with_server:
        from .bot.telegram_bot import start_bot_thread
        start_bot_thread()





@app.get("/")
@app.get("/ru")
@app.get("/ua")
def root():
    landing_file = Path(__file__).resolve().parent / "web" / "landing.html"
    headers = {
        "Cache-Control": "no-store, no-cache, must-revalidate, max-age=0",
        "Pragma": "no-cache",
        "Expires": "0"
    }
    if landing_file.exists():
        return HTMLResponse(landing_file.read_text(encoding="utf-8"), headers=headers)
    panel_file = Path(__file__).resolve().parent / "web" / "panel.html"
    return HTMLResponse(panel_file.read_text(encoding="utf-8"), headers=headers)


@app.get("/panel")
def panel():
    panel_file = Path(__file__).resolve().parent / "web" / "panel.html"
    headers = {
        "Cache-Control": "no-store, no-cache, must-revalidate, max-age=0",
        "Pragma": "no-cache",
        "Expires": "0"
    }
    return HTMLResponse(panel_file.read_text(encoding="utf-8"), headers=headers)


@app.get("/manifest.json")
def pwa_manifest():
    return FileResponse(Path(__file__).resolve().parent / "web" / "manifest.json", media_type="application/manifest+json")


@app.get("/service-worker.js")
def pwa_service_worker():
    return FileResponse(Path(__file__).resolve().parent / "web" / "service-worker.js", media_type="application/javascript")


@app.get("/robots.txt")
def robots():
    return FileResponse(Path(__file__).resolve().parent / "web" / "robots.txt", media_type="text/plain")


@app.get("/assets/{filename}")
def get_asset(filename: str):
    asset_path = Path(__file__).resolve().parent / "web" / "assets" / filename
    if asset_path.exists():
        media_types = {
            ".png": "image/png",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".svg": "image/svg+xml",
            ".ico": "image/x-icon"
        }
        media_type = media_types.get(asset_path.suffix.lower(), "application/octet-stream")
        return FileResponse(asset_path, media_type=media_type)
    from fastapi import HTTPException
    raise HTTPException(status_code=404, detail="Asset not found")


@app.get("/sitemap.xml")
@app.get("/sitemap")
@app.get("/pcmanager.online/sitemap.xml")
@app.get("/https://pcmanager.online/sitemap.xml")
@app.get("/http://pcmanager.online/sitemap.xml")
@app.get("/www.pcmanager.online/sitemap.xml")
@app.get("/https://www.pcmanager.online/sitemap.xml")
def sitemap():
    return FileResponse(Path(__file__).resolve().parent / "web" / "sitemap.xml", media_type="application/xml")


@app.get("/api/agents/version/latest")
def get_latest_agent_version():
    return {
        "latest_version": settings.latest_agent_version,
        "download_url": "/releases/agent.exe"
    }


@app.get("/releases/agent.exe")
@app.get("/releases/PCManager_Agent.exe")
def download_agent_exe():
    exe_path = Path(__file__).resolve().parent.parent.parent / "releases" / "agent.exe"
    if not exe_path.exists():
        py_path = Path(__file__).resolve().parent.parent.parent / "pc-agent" / "agent.py"
        if py_path.exists():
            return FileResponse(py_path, media_type="application/x-python", filename="PCManager_Agent.py")
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Release file not found")
    headers = {
        "Cache-Control": "no-store, no-cache, must-revalidate, max-age=0",
        "Pragma": "no-cache",
        "Expires": "0"
    }
    return FileResponse(exe_path, media_type="application/octet-stream", filename="PCManager_Agent.exe", headers=headers)


@app.websocket("/ws/status")
async def status_ws(websocket: WebSocket):
    agent_id = str(websocket.query_params.get("agent_id") or websocket.headers.get("x-agent-id") or "")
    agent_access_key = str(websocket.query_params.get("access_key") or websocket.headers.get("x-server-access-key") or "")
    if agent_id and verify_server_access_key(agent_access_key):
        await ws_manager.connect("agents", websocket)
        await ws_manager.connect(f"agent:{agent_id}", websocket, accept=False)
        await websocket.send_json({"event": "agent_ws_connected", "payload": {"ok": True, "mode": "status"}})
        try:
            while True:
                message = await websocket.receive_json()
                event = str(message.get("event") or "")
                payload = message.get("payload") or {}
                with SessionLocal() as db:
                    agent = db.query(Agent).filter(Agent.agent_id == agent_id).first()
                    if not agent:
                        continue
                    if event == "agent_heartbeat":
                        previous, updated = update_heartbeat(db, agent, payload)
                        if previous != "online":
                            add_log(db, "info", "agent", "agent_online", f"Agent {agent_id} is online", {"agent_id": agent_id})
                            await ws_manager.broadcast("status", "agent_online", {"agent_id": agent_id, "name": updated.name})
                        await ws_manager.broadcast("status", "agent_updated", {"agent_id": agent_id, "status": compute_agent_status(updated)})
                        await websocket.send_json({"event": "heartbeat_ack", "payload": {"status": compute_agent_status(updated), "server_time": datetime.utcnow().isoformat()}})
                    elif event == "task_started":
                        task_id = str(payload.get("task_id") or "")
                        add_log(db, "info", "task", "task_started", f"Task {task_id} started over websocket", {"task_id": task_id, "agent_id": agent_id})
                        await ws_manager.broadcast("status", "task_started", {"task_id": task_id, "agent_id": agent_id})
                    elif event == "task_result":
                        task_id = str(payload.get("task_id") or "")
                        task = db.query(Task).filter(Task.task_id == task_id, Task.agent_id == agent_id).first()
                        if task:
                            updated = finish_task(db, task, str(payload.get("status") or "failed"), str(payload.get("result") or ""), str(payload.get("error") or ""))
                            ws_event = "task_done" if updated.status in {"success", "done"} else "task_failed"
                            add_log(db, "info" if ws_event == "task_done" else "error", "task", ws_event, f"Task {task_id} -> {updated.status}", {"task_id": task_id, "agent_id": agent_id})
                            await ws_manager.broadcast("status", ws_event, {"task_id": task_id, "agent_id": agent_id, "status": updated.status})
        except WebSocketDisconnect:
            ws_manager.disconnect("agents", websocket)
            ws_manager.disconnect(f"agent:{agent_id}", websocket)
        return
    subject = await get_current_admin_ws(websocket)
    if subject.startswith("user:"):
        try:
            websocket.state.user_id = int(subject.split(":", 1)[1])
        except ValueError:
            pass
    await ws_manager.connect("status", websocket)
    await websocket.send_json({"event": "server_status", "payload": {"status": "online", "time": datetime.utcnow().isoformat()}})
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect("status", websocket)


@app.websocket("/ws/agent")
async def agent_ws(websocket: WebSocket):
    token = str(websocket.query_params.get("token") or "")
    if not token:
        await websocket.close(code=4401)
        return
    with SessionLocal() as db:
        agent = db.query(Agent).filter(Agent.agent_token == token).first()
        if not agent:
            await websocket.close(code=4403)
            return
        agent_id = agent.agent_id
    await ws_manager.connect("agents", websocket)
    await ws_manager.connect(f"agent:{agent_id}", websocket, accept=False)
    await websocket.send_json({"event": "agent_ws_connected", "payload": {"ok": True}})
    try:
        while True:
            message = await websocket.receive_json()
            event = str(message.get("event") or "")
            payload = message.get("payload") or {}
            with SessionLocal() as db:
                agent = db.query(Agent).filter(Agent.agent_id == agent_id).first()
                if not agent:
                    await websocket.close(code=4403)
                    return
                if event == "agent_heartbeat":
                    previous, updated = update_heartbeat(db, agent, payload)
                    if previous != "online":
                        add_log(db, "info", "agent", "agent_online", f"Agent {agent_id} is online", {"agent_id": agent_id})
                        await ws_manager.broadcast("status", "agent_online", {"agent_id": agent_id, "name": updated.name})
                    await websocket.send_json({"event": "heartbeat_ack", "payload": {"status": compute_agent_status(updated), "server_time": datetime.utcnow().isoformat()}})
                elif event == "task_started":
                    task_id = str(payload.get("task_id") or "")
                    add_log(db, "info", "task", "task_started", f"Task {task_id} started over websocket", {"task_id": task_id, "agent_id": agent_id})
                    await ws_manager.broadcast("status", "task_started", {"task_id": task_id, "agent_id": agent_id})
                elif event == "task_result":
                    task_id = str(payload.get("task_id") or "")
                    task = db.query(Task).filter(Task.task_id == task_id, Task.agent_id == agent_id).first()
                    if task:
                        updated = finish_task(db, task, str(payload.get("status") or "failed"), str(payload.get("result") or ""), str(payload.get("error") or ""))
                        ws_event = "task_done" if updated.status in {"success", "done"} else "task_failed"
                        add_log(db, "info" if ws_event == "task_done" else "error", "task", ws_event, f"Task {task_id} -> {updated.status}", {"task_id": task_id, "agent_id": agent_id})
                        await ws_manager.broadcast("status", ws_event, {"task_id": task_id, "agent_id": agent_id, "status": updated.status})
                else:
                    add_log(db, "warning", "agent", "unknown_ws_event", f"Unknown agent websocket event: {event}", {"agent_id": agent_id})
    except WebSocketDisconnect:
        ws_manager.disconnect("agents", websocket)
        ws_manager.disconnect(f"agent:{agent_id}", websocket)
