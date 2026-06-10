import uuid
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from ..config import get_settings
from ..models import Agent, Task
from .agent_service import DANGEROUS_ACTIONS, SAFE_ACTIONS


settings = get_settings()
ACTIVE_STATUSES = {"queued", "pending", "running"}
FINAL_STATUSES = {"success", "done", "failed", "cancelled", "timeout"}

ACTION_ALIASES = {
    "screenshot": "take_screenshot",
    "system_info": "get_system_info",
    "process_list": "get_process_list",
    "disk_info": "get_disk_info",
    "logs": "agent_logs",
    "input_key": "press_key",
    "key": "press_key",
    "click": "click_preset",
    "launcher": "launch_allowed_app",
    "launch_game": "launch_allowed_app",
    "close_game": "close_allowed_app",
    "close_app": "close_allowed_app",
    "game": "game_status",
    "anti_afk": "anti_afk_start",
    "anti_afk_on": "anti_afk_start",
    "anti_afk_off": "anti_afk_stop",
    "autoscreen": "auto_screen_start",
    "autoscreen_on": "auto_screen_start",
    "autoscreen_off": "auto_screen_stop",
    "autoscreen_start": "auto_screen_start",
    "autoscreen_stop": "auto_screen_stop",
    "auto_screenshot": "auto_screen_start",
    "automation": "automation_status",
    "desktop_prev": "desktop_left",
    "desktop_previous": "desktop_left",
    "desktop_next": "desktop_right",
    "desktop_create": "desktop_new",
}



def is_safe_retry_action(action: str) -> bool:
    return action not in {"shutdown_pc", "restart_pc", "update_agent", "shell", "restart_allowed_app"}


def create_task(
    db: Session,
    agent: Agent,
    action: str,
    payload: dict | None,
    created_by: str,
    confirmed: bool = False,
    request_id: str | None = None,
) -> Task:
    payload = payload or {}
    action = ACTION_ALIASES.get(action, action)
    if action not in SAFE_ACTIONS and action not in DANGEROUS_ACTIONS:
        raise ValueError(f"Action '{action}' is not allowed")
    if action in DANGEROUS_ACTIONS and not settings.allow_dangerous_commands:
        raise ValueError("Dangerous commands are disabled")
    if action in DANGEROUS_ACTIONS and not confirmed:
        raise ValueError("Dangerous action requires confirmation")
    if action in {"get_screenshot", "take_screenshot"} and not settings.enable_screenshot:
        raise ValueError("Screenshot is disabled on server")
    if action == "camera_snapshot" and not settings.enable_camera:
        raise ValueError("Camera is disabled on server")
    if action == "record_video" and not settings.enable_video_recording:
        raise ValueError("Video recording is disabled on server")
    if action == "record_screen" and not settings.enable_screenshot:
        raise ValueError("Screenshot/screen recording is disabled on server")
    if action in {"camera_snapshot", "record_video", "record_screen", "lock_pc", "sleep_pc", "monitor_off"} and not confirmed:
        raise ValueError("Action requires confirmation")
    if action in {"record_video", "record_screen"}:
        payload["duration_seconds"] = max(1, min(int(payload.get("duration_seconds") or 1), settings.max_video_seconds))
    if action == "run_safe_script" and str(payload.get("script_name") or "") not in settings.allowed_scripts:
        raise ValueError("Script is not in allowlist")
    existing = (
        db.query(Task)
        .filter(Task.agent_id == agent.agent_id, Task.action == action, Task.status.in_(["queued", "pending", "running"]))
        .order_by(Task.created_at.desc())
        .first()
    )
    if existing and (existing.payload or {}) == payload:
        return existing
    if request_id:
        previous = db.query(Task).filter(Task.request_id == request_id).first()
        if previous:
            return previous
    request_id = request_id or str(uuid.uuid4())
    task = Task(
        task_id=request_id,
        request_id=request_id,
        agent_id=agent.agent_id,
        action=action,
        payload=payload,
        status="queued",
        timeout_seconds=int(payload.get("timeout_seconds") or settings.task_timeout_seconds),
        requires_confirmation=action in DANGEROUS_ACTIONS,
        confirmed=confirmed,
        safe_to_retry=is_safe_retry_action(action),
        created_by=created_by,
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


def expire_running_tasks(db: Session) -> list[Task]:
    expired = (
        db.query(Task)
        .filter(Task.status == "running", Task.started_at.isnot(None))
        .all()
    )
    now = datetime.utcnow()
    retried: list[Task] = []
    for task in list(expired):
        timeout = int(task.timeout_seconds or settings.task_timeout_seconds)
        if task.started_at and task.started_at >= now - timedelta(seconds=timeout):
            expired.remove(task)
            continue
        task.status = "timeout"
        task.finished_at = now
        task.error = task.error or f"Task timed out after {timeout}s"
        agent = db.query(Agent).filter(Agent.agent_id == task.agent_id).first()
        if agent:
            agent.current_task = ""
            db.add(agent)
        db.add(task)
        if task.safe_to_retry and task.retry_count < settings.safe_retry_count and agent:
            retry_id = str(uuid.uuid4())
            retried.append(
                Task(
                    task_id=retry_id,
                    request_id=retry_id,
                    agent_id=task.agent_id,
                    action=task.action,
                    payload=task.payload or {},
                    status="queued",
                    retry_count=task.retry_count + 1,
                    timeout_seconds=timeout,
                    requires_confirmation=task.requires_confirmation,
                    confirmed=task.confirmed,
                    safe_to_retry=True,
                    created_by=task.created_by,
                )
            )
    if expired or retried:
        for item in retried:
            db.add(item)
        db.commit()
    return expired


def next_task(db: Session, agent: Agent) -> Task | None:
    expire_running_tasks(db)
    task = (
        db.query(Task)
        .filter(Task.agent_id == agent.agent_id, Task.status.in_(["queued", "pending"]))
        .order_by(Task.created_at.asc())
        .first()
    )
    if not task:
        return None
    task.status = "running"
    task.started_at = datetime.utcnow()
    agent.current_task = task.action
    db.add_all([task, agent])
    db.commit()
    db.refresh(task)
    return task


def finish_task(db: Session, task: Task, status: str, result: str = "", error: str = "") -> Task:
    final_status = {"done": "success", "error": "failed"}.get(status, status)
    task.status = final_status
    task.result = result[: settings.max_result_bytes]
    task.error = error[:8000]
    task.updated_at = datetime.utcnow()
    if final_status in {"success", "failed", "cancelled", "timeout"}:
        task.finished_at = datetime.utcnow()
        agent = db.query(Agent).filter(Agent.agent_id == task.agent_id).first()
        if agent:
            agent.current_task = ""
            if error:
                agent.last_error = error[:8000]
            db.add(agent)
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


def cancel_task(db: Session, task: Task) -> Task:
    if task.status not in FINAL_STATUSES:
        task.status = "cancelled"
        task.finished_at = datetime.utcnow()
        db.add(task)
        db.commit()
        db.refresh(task)
    return task


def retry_task(db: Session, task: Task, created_by: str) -> Task:
    if not task.safe_to_retry:
        raise ValueError("This task is not safe to retry")
    agent = db.query(Agent).filter(Agent.agent_id == task.agent_id).first()
    if not agent:
        raise ValueError("Agent not found")
    return create_task(db, agent, task.action, task.payload or {}, created_by=created_by, confirmed=True)
