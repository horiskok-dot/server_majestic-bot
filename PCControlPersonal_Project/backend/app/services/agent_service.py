import secrets
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from ..config import get_settings
from ..models import Agent, LogEntry


SAFE_ACTIONS = {
    "ping",
    "system_info",
    "get_system_info",
    "process_list",
    "get_process_list",
    "disk_info",
    "get_disk_info",
    "agent_logs",
    "press_key",
    "click_preset",
    "release_keys",
    "launch_allowed_app",
    "close_allowed_app",
    "open_url",
    "volume_up",
    "volume_down",
    "game_status",
    "anti_afk_start",
    "anti_afk_stop",
    "auto_screen_start",
    "auto_screen_stop",
    "automation_status",
    "cleanup_screenshots",
    "desktop_new",
    "desktop_close",
    "desktop_left",
    "desktop_right",
    "get_network_info",
    "screenshot",
    "restart_agent",
    "update_agent",
    "get_screenshot",
    "take_screenshot",
    "restart_allowed_app",
    "camera_snapshot",
    "record_video",
    "record_screen",
    "lock_pc",
    "sleep_pc",
    "monitor_off",
    "run_safe_script",
    "remote_input",
    "start_timer",
    "cancel_timer",
    "add_automation_rule",
    "delete_automation_rule",
}

DANGEROUS_ACTIONS = {"restart_pc", "shutdown_pc"}


def compute_agent_status(agent: Agent) -> str:
    if not agent.last_seen_at:
        return "offline"
    delta = datetime.utcnow() - agent.last_seen_at
    if delta <= timedelta(seconds=35):
        return "online"
    if delta <= timedelta(seconds=120):
        return "unstable"
    return "offline"


def ensure_agent(db: Session, agent_id: str, defaults: dict) -> Agent:
    agent = db.query(Agent).filter(Agent.agent_id == agent_id).first()
    if agent:
        return agent
    agent = Agent(
        agent_id=agent_id,
        agent_token=secrets.token_urlsafe(32),
        name=defaults.get("name") or agent_id,
        version=defaults.get("version") or "unknown",
        platform=defaults.get("platform") or "Windows",
        hostname=defaults.get("hostname") or defaults.get("name") or agent_id,
        username=defaults.get("username") or "",
        os_name=defaults.get("os_name") or defaults.get("platform") or "Windows",
        local_ip=defaults.get("local_ip") or "",
        public_ip=defaults.get("public_ip") or "",
        screenshot_enabled=bool(defaults.get("screenshot_enabled")),
        camera_enabled=bool(defaults.get("camera_enabled")),
        video_enabled=bool(defaults.get("video_enabled")),
    )
    db.add(agent)
    db.commit()
    db.refresh(agent)
    return agent


def update_heartbeat(db: Session, agent: Agent, data: dict) -> tuple[str, Agent]:
    previous = compute_agent_status(agent)
    agent.status = "online"
    agent.latency_ms = int(data.get("latency_ms") or 0)
    agent.current_task = str(data.get("current_task") or "")
    
    # Store or retrieve throttling state (15-minute alert interval)
    previous_system_info = agent.system_info or {}
    last_alerts = previous_system_info.get("last_alerts") or {}
    
    # Update system_info with incoming payload and preserve last_alerts throttling state
    new_system_info = data.get("system_info") or {}
    new_system_info["last_alerts"] = last_alerts
    agent.system_info = new_system_info
    
    agent.disk_info = data.get("disk_info") or {}
    agent.network_info = data.get("network_info") or {}
    agent.process_info = data.get("process_info") or {}
    
    if agent.network_info:
        agent.local_ip = str(agent.network_info.get("ip") or agent.local_ip or "")
        agent.public_ip = str(agent.network_info.get("public_ip") or agent.public_ip or "")
    if agent.system_info:
        agent.version = str(agent.system_info.get("agent_version") or agent.version or "unknown")
        agent.platform = str(agent.system_info.get("platform") or agent.platform or "Windows")
        agent.hostname = str(agent.system_info.get("hostname") or agent.hostname or "")
        agent.username = str(agent.system_info.get("username") or agent.username or "")
        agent.os_name = str(agent.system_info.get("platform") or agent.os_name or "")
    agent.last_error = str(data.get("last_error") or "")
    agent.last_seen_at = datetime.utcnow()
    agent.updated_at = datetime.utcnow()
    
    # Threshold Checking and Throttled Alerting
    now_dt = datetime.utcnow()
    throttle_delta = timedelta(minutes=15)
    
    temp_dict = agent.system_info.get("temperature")
    temp = None
    if isinstance(temp_dict, dict):
        temp = temp_dict.get("max_c")
        
    alerts_triggered = []
    
    # Check Temperature threshold (> 80°C)
    if temp is not None and isinstance(temp, (int, float)) and temp > 80.0:
        last_temp = last_alerts.get("temp")
        should_alert = True
        if last_temp:
            try:
                if now_dt - datetime.fromisoformat(last_temp) < throttle_delta:
                    should_alert = False
            except Exception:
                pass
        if should_alert:
            alerts_triggered.append(("temp", f"🌡️ *Перегрев процессора превысил 80°C!*\nТекущая температура: `{temp}°C`"))
            last_alerts["temp"] = now_dt.isoformat()
            
    # Create database warning records for any triggered alerts
    for metric, alert_text in alerts_triggered:
        alert_msg = (
            f"⚠️ *Предупреждение о превышении порогов!*\n"
            f"🖥️ Компьютер: *{agent.name}* (`{agent.agent_id}`)\n"
            f"👤 Пользователь: `{agent.username}`\n\n"
            f"{alert_text}"
        )
        alert_entry = LogEntry(
            level="warning",
            source="agent",
            event="threshold_alert",
            message=alert_msg,
            meta={"agent_id": agent.agent_id, "metric": metric}
        )
        db.add(alert_entry)
        
    db.add(agent)
    db.commit()
    db.refresh(agent)
    return previous, agent


def list_agents(db: Session) -> list[Agent]:
    agents = db.query(Agent).order_by(Agent.updated_at.desc()).all()
    for agent in agents:
        agent.status = compute_agent_status(agent)
    return agents


def agent_to_mobile(agent: Agent) -> dict:
    return {
        "agent_id": agent.agent_id,
        "name": agent.name,
        "status": compute_agent_status(agent),
        "last_seen": agent.last_seen_at.isoformat() if agent.last_seen_at else None,
        "latency": agent.latency_ms,
        "version": agent.version,
        "platform": agent.platform,
        "hostname": agent.hostname,
        "username": agent.username,
        "os": agent.os_name,
        "local_ip": agent.local_ip,
        "public_ip": agent.public_ip,
        "connection_ip": agent.connection_ip,
        "current_task": agent.current_task,
        "last_error": agent.last_error,
        "screenshot_enabled": agent.screenshot_enabled,
        "camera_enabled": agent.camera_enabled,
        "video_enabled": agent.video_enabled,
        "system_info": agent.system_info,
        "disk_info": agent.disk_info,
        "network_info": agent.network_info,
        "process_info": agent.process_info,
    }


def screenshot_allowed(agent: Agent) -> bool:
    settings = get_settings()
    return settings.enable_screenshot and agent.screenshot_enabled
