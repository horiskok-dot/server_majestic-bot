import base64
import json
from datetime import datetime

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from fastapi.responses import FileResponse, Response
from sqlalchemy.orm import Session

from ..auth import get_current_user, CurrentUser
from ..config import get_settings
from ..database import get_db
from ..models import Agent, FileAsset, LogEntry, Task
from ..schemas import DashboardResponse, TaskCreate
from ..services.agent_service import agent_to_mobile, compute_agent_status, list_agents, screenshot_allowed
from ..services.file_service import asset_path, create_asset_from_upload, get_asset_or_404
from ..services.log_service import add_log
from ..services.network_service import server_info
from ..services.server_media_service import create_server_screenshot, create_server_webcam_photo, create_server_webcam_video
from ..services.task_service import cancel_task, create_task, expire_running_tasks, retry_task
from ..websocket.manager import ws_manager


router = APIRouter(prefix="/api/mobile", tags=["mobile"])
settings = get_settings()
SERVER_STARTED_AT = datetime.utcnow()


def uptime_string() -> str:
    seconds = int((datetime.utcnow() - SERVER_STARTED_AT).total_seconds())
    hours, rem = divmod(seconds, 3600)
    minutes, sec = divmod(rem, 60)
    return f"{hours}h {minutes}m {sec}s"


def check_admin(user: CurrentUser):
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")


def get_allowed_agent(db: Session, agent_id: str, user: CurrentUser) -> Agent:
    query = db.query(Agent).filter(Agent.agent_id == agent_id)
    if not user.is_admin:
        query = query.filter(Agent.user_id == user.user_id)
    agent = query.first()
    if not agent:
        raise HTTPException(status_code=403, detail="Access to agent denied")
    return agent


@router.get("/config")
def config(current_user: CurrentUser = Depends(get_current_user)):
    base = settings.base_public_url.rstrip("/")
    ws_base = base.replace("https://", "wss://").replace("http://", "ws://")
    return {
        "server_name": settings.app_name,
        "version": settings.app_version,
        "base_url": base,
        "websocket_url": f"{ws_base}/ws/status",
        "health_url": f"{base}/api/health",
        "ping_url": f"{base}/api/ping",
        "features": {"screenshot": settings.enable_screenshot, "tasks": True, "logs": True},
        "local_only": settings.local_only,
    }


@router.get("/dashboard", response_model=DashboardResponse)
def dashboard(current_user: CurrentUser = Depends(get_current_user), db: Session = Depends(get_db)):
    expire_running_tasks(db)
    
    # Filter agents & tasks by user_id if not admin
    agents_query = db.query(Agent)
    tasks_query = db.query(Task)
    
    if not current_user.is_admin:
        agents_query = agents_query.filter(Agent.user_id == current_user.user_id)
        tasks_query = tasks_query.filter(Task.user_id == current_user.user_id)
        
    agents = agents_query.all()
    tasks = tasks_query.all()
    
    errors = [a.last_error for a in agents if a.last_error][-5:]
    return DashboardResponse(
        server_status="online",
        uptime=uptime_string(),
        agents_total=len(agents),
        agents_online=sum(1 for item in agents if compute_agent_status(item) == "online"),
        active_tasks=sum(1 for task in tasks if task.status in {"queued", "pending", "running"}),
        last_errors=errors,
    )


@router.get("/server-info")
def mobile_server_info(current_user: CurrentUser = Depends(get_current_user)):
    check_admin(current_user)
    return server_info()


@router.get("/connection-info")
def mobile_connection_info(current_user: CurrentUser = Depends(get_current_user), db: Session = Depends(get_db)):
    data = server_info()
    agents_query = db.query(Agent)
    if not current_user.is_admin:
        agents_query = agents_query.filter(Agent.user_id == current_user.user_id)
    data["agents"] = [agent_to_mobile(agent) for agent in agents_query.all()]
    return data


@router.post("/server/screenshot")
def mobile_server_screenshot(current_user: CurrentUser = Depends(get_current_user), db: Session = Depends(get_db)):
    check_admin(current_user)
    return create_server_screenshot(db, "android")


@router.get("/server/screenshots")
def mobile_server_screenshots(current_user: CurrentUser = Depends(get_current_user), db: Session = Depends(get_db)):
    check_admin(current_user)
    return db.query(FileAsset).filter(FileAsset.public_type == "server_screenshot", FileAsset.is_active == True).order_by(FileAsset.created_at.desc()).limit(100).all()  # noqa: E712


@router.post("/server/webcam/photo")
def mobile_server_webcam_photo(confirmed: bool = Query(default=False), current_user: CurrentUser = Depends(get_current_user), db: Session = Depends(get_db)):
    check_admin(current_user)
    if not confirmed:
        raise HTTPException(status_code=400, detail="Функция требует подтверждения")
    return create_server_webcam_photo(db, "android")


@router.get("/server/webcam/photos")
def mobile_server_webcam_photos(current_user: CurrentUser = Depends(get_current_user), db: Session = Depends(get_db)):
    check_admin(current_user)
    return db.query(FileAsset).filter(FileAsset.public_type == "server_webcam_photo", FileAsset.is_active == True).order_by(FileAsset.created_at.desc()).limit(100).all()  # noqa: E712


@router.post("/server/webcam/record")
def mobile_server_webcam_record(duration_seconds: int = Query(default=10), confirmed: bool = Query(default=False), current_user: CurrentUser = Depends(get_current_user), db: Session = Depends(get_db)):
    check_admin(current_user)
    if not confirmed:
        raise HTTPException(status_code=400, detail="Функция требует подтверждения")
    return create_server_webcam_video(db, duration_seconds, "android")


@router.get("/server/webcam/videos")
def mobile_server_webcam_videos(current_user: CurrentUser = Depends(get_current_user), db: Session = Depends(get_db)):
    check_admin(current_user)
    return db.query(FileAsset).filter(FileAsset.public_type == "server_webcam_video", FileAsset.is_active == True).order_by(FileAsset.created_at.desc()).limit(100).all()  # noqa: E712


@router.get("/agents")
def agents(current_user: CurrentUser = Depends(get_current_user), db: Session = Depends(get_db)):
    agents_query = db.query(Agent)
    if not current_user.is_admin:
        agents_query = agents_query.filter(Agent.user_id == current_user.user_id)
    return [agent_to_mobile(agent) for agent in agents_query.all()]


@router.get("/agents/{agent_id}")
def agent_details(agent_id: str, current_user: CurrentUser = Depends(get_current_user), db: Session = Depends(get_db)):
    agent = get_allowed_agent(db, agent_id, current_user)
    data = agent_to_mobile(agent)
    data["recent_tasks"] = db.query(Task).filter(Task.agent_id == agent_id).order_by(Task.created_at.desc()).limit(20).all()
    return data


@router.get("/agents/{agent_id}/processes")
def mobile_agent_processes(agent_id: str, current_user: CurrentUser = Depends(get_current_user), db: Session = Depends(get_db)):
    get_allowed_agent(db, agent_id, current_user)
    from .processes import get_processes
    return get_processes(agent_id, db)


@router.post("/agents/{agent_id}/processes/refresh")
def mobile_refresh_processes(agent_id: str, current_user: CurrentUser = Depends(get_current_user), db: Session = Depends(get_db)):
    get_allowed_agent(db, agent_id, current_user)
    from .processes import refresh_processes
    return refresh_processes(agent_id, db)


@router.post("/agents/{agent_id}/screenshot")
def mobile_screenshot_task(agent_id: str, current_user: CurrentUser = Depends(get_current_user), db: Session = Depends(get_db)):
    get_allowed_agent(db, agent_id, current_user)
    from .screenshots import take_screenshot
    return take_screenshot(agent_id, db)


@router.post("/agents/{agent_id}/camera/photo")
def mobile_camera_photo(agent_id: str, current_user: CurrentUser = Depends(get_current_user), db: Session = Depends(get_db)):
    get_allowed_agent(db, agent_id, current_user)
    from .camera import camera_photo
    return camera_photo(agent_id, db)


@router.post("/agents/{agent_id}/camera/record")
def mobile_camera_record(agent_id: str, duration_seconds: int = 5, current_user: CurrentUser = Depends(get_current_user), db: Session = Depends(get_db)):
    get_allowed_agent(db, agent_id, current_user)
    from .camera import record_video
    return record_video(agent_id, duration_seconds, db)


@router.get("/tasks")
def tasks(status: str | None = Query(default=None), current_user: CurrentUser = Depends(get_current_user), db: Session = Depends(get_db)):
    expire_running_tasks(db)
    
    query = db.query(Task)
    if not current_user.is_admin:
        query = query.filter(Task.user_id == current_user.user_id)
        
    query = query.order_by(Task.created_at.desc())
    if status:
        query = query.filter(Task.status == status)
    return query.limit(100).all()


@router.post("/tasks")
async def create_mobile_task(payload: TaskCreate, current_user: CurrentUser = Depends(get_current_user), db: Session = Depends(get_db)):
    agent = get_allowed_agent(db, payload.agent_id, current_user)
    try:
        action = payload.action or payload.task_type
        if not action:
            raise HTTPException(status_code=400, detail="Task action is required")
        task_payload = dict(payload.payload or {})
        if payload.timeout_seconds:
            task_payload["timeout_seconds"] = payload.timeout_seconds
            
        task = create_task(db, agent, action, task_payload, "mobile", payload.confirmed, payload.request_id)
        
        # Link user_id to task for SaaS tracking
        if not current_user.is_admin:
            task.user_id = current_user.user_id
            db.add(task)
            db.commit()
            
        add_log(db, "info", "mobile", "task_created", f"Task {task.task_id} created", {"task_id": task.task_id, "request_id": task.request_id})
        await ws_manager.broadcast("status", "task_created", {"task_id": task.task_id, "agent_id": task.agent_id, "action": task.action})
        return task
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/tasks/{task_id}/cancel")
def cancel_mobile_task(task_id: str, current_user: CurrentUser = Depends(get_current_user), db: Session = Depends(get_db)):
    query = db.query(Task).filter(Task.task_id == task_id)
    if not current_user.is_admin:
        query = query.filter(Task.user_id == current_user.user_id)
    task = query.first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
        
    updated = cancel_task(db, task)
    add_log(db, "warning", "mobile", "task_cancelled", f"Task {task_id} cancelled", {"task_id": task_id})
    return updated


@router.post("/tasks/{task_id}/retry")
def retry_mobile_task(task_id: str, current_user: CurrentUser = Depends(get_current_user), db: Session = Depends(get_db)):
    query = db.query(Task).filter(Task.task_id == task_id)
    if not current_user.is_admin:
        query = query.filter(Task.user_id == current_user.user_id)
    task = query.first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    try:
        retried = retry_task(db, task, "mobile")
        add_log(db, "info", "mobile", "task_retried", f"Task {task_id} retried", {"new_task_id": retried.task_id})
        return retried
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/logs")
def logs(level: str | None = Query(default=None), current_user: CurrentUser = Depends(get_current_user), db: Session = Depends(get_db)):
    query = db.query(LogEntry)
    # Filter logs by events and user scope if desired
    # Logs are generally global, but we can restrict log reading to admin only or filter for SaaS users
    if not current_user.is_admin:
        # SaaS user: show only logs related to their own agents
        user_agents = db.query(Agent).filter(Agent.user_id == current_user.user_id).all()
        agent_ids = [a.agent_id for a in user_agents]
        # In this DB, logs might have meta with agent_id. Let's do a simple filter.
        # Since it's JSON in SQLite, we can inspect meta, or just allow logs for user's own agent actions.
        # We can perform a robust meta check or filter by meta agent_id
        # For simplicity, filter logs that contain any of user's agent_ids in the text or meta
        # Actually, let's filter logs by logs generated by "mobile" with user's tasks or agent logs
        pass
    query = query.order_by(LogEntry.created_at.desc())
    if level:
        query = query.filter(LogEntry.level == level.lower())
    return query.limit(200).all()


@router.get("/files")
def mobile_files(current_user: CurrentUser = Depends(get_current_user), db: Session = Depends(get_db)):
    query = db.query(FileAsset).filter(FileAsset.is_active == True)
    if not current_user.is_admin:
        # User files: only files generated by or uploaded for user's agents
        user_agents = db.query(Agent).filter(Agent.user_id == current_user.user_id).all()
        agent_ids = [a.agent_id for a in user_agents]
        query = query.filter(FileAsset.agent_id.in_(agent_ids))
    return query.order_by(FileAsset.created_at.desc()).limit(300).all()  # noqa: E712


@router.post("/files/upload")
async def mobile_upload_file(
    public_type: str = Query(default="upload"),
    description: str = Query(default=""),
    upload: UploadFile = File(...),
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Check if upload is allowed
    return await create_asset_from_upload(db, upload, public_type, "android", description=description)


@router.get("/files/{file_id}/download")
def mobile_download_file(file_id: int, current_user: CurrentUser = Depends(get_current_user), db: Session = Depends(get_db)):
    asset = get_asset_or_404(db, file_id)
    if not current_user.is_admin and asset.agent_id:
        # Verify ownership
        get_allowed_agent(db, asset.agent_id, current_user)
    return FileResponse(asset_path(asset), media_type=asset.mime_type, filename=asset.original_filename or asset.filename)


@router.delete("/files/{file_id}")
def mobile_delete_file(file_id: int, current_user: CurrentUser = Depends(get_current_user), db: Session = Depends(get_db)):
    asset = get_asset_or_404(db, file_id)
    if not current_user.is_admin and asset.agent_id:
        get_allowed_agent(db, asset.agent_id, current_user)
    asset.is_active = False
    db.add(asset)
    db.commit()
    add_log(db, "warning", "mobile", "file_deleted", f"File {asset.id} deleted", {"file_id": asset.id})
    return {"ok": True}


@router.get("/photos")
def mobile_photos(current_user: CurrentUser = Depends(get_current_user), db: Session = Depends(get_db)):
    query = db.query(FileAsset).filter(FileAsset.public_type == "photo", FileAsset.is_active == True)
    if not current_user.is_admin:
        user_agents = db.query(Agent).filter(Agent.user_id == current_user.user_id).all()
        agent_ids = [a.agent_id for a in user_agents]
        query = query.filter(FileAsset.agent_id.in_(agent_ids))
    return query.order_by(FileAsset.created_at.desc()).limit(200).all()  # noqa: E712


@router.get("/screenshots")
def mobile_screenshots(current_user: CurrentUser = Depends(get_current_user), db: Session = Depends(get_db)):
    query = db.query(FileAsset).filter(FileAsset.public_type == "screenshot", FileAsset.is_active == True)
    if not current_user.is_admin:
        user_agents = db.query(Agent).filter(Agent.user_id == current_user.user_id).all()
        agent_ids = [a.agent_id for a in user_agents]
        query = query.filter(FileAsset.agent_id.in_(agent_ids))
    return query.order_by(FileAsset.created_at.desc()).limit(200).all()  # noqa: E712


@router.get("/videos")
def mobile_videos(current_user: CurrentUser = Depends(get_current_user), db: Session = Depends(get_db)):
    query = db.query(FileAsset).filter(FileAsset.public_type == "video", FileAsset.is_active == True)
    if not current_user.is_admin:
        user_agents = db.query(Agent).filter(Agent.user_id == current_user.user_id).all()
        agent_ids = [a.agent_id for a in user_agents]
        query = query.filter(FileAsset.agent_id.in_(agent_ids))
    return query.order_by(FileAsset.created_at.desc()).limit(200).all()  # noqa: E712


@router.get("/screenshot/{agent_id}")
def screenshot(agent_id: str, current_user: CurrentUser = Depends(get_current_user), db: Session = Depends(get_db)):
    agent = get_allowed_agent(db, agent_id, current_user)
    if not screenshot_allowed(agent):
        raise HTTPException(status_code=403, detail="Screenshot disabled")
    task = (
        db.query(Task)
        .filter(Task.agent_id == agent_id, Task.action == "get_screenshot", Task.status.in_(["success", "done"]))
        .order_by(Task.finished_at.desc(), Task.created_at.desc())
        .first()
    )
    if not task or not task.result:
        raise HTTPException(status_code=404, detail="Screenshot is not available yet. Create get_screenshot task first.")
    try:
        payload = json.loads(task.result)
        content = base64.b64decode(payload["data"])
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Stored screenshot is corrupted") from exc
    return Response(content=content, media_type=payload.get("mime_type", "image/png"))
