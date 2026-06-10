import subprocess
import re
import json
import gzip
import glob
from pathlib import Path
from fastapi import APIRouter, Depends
from pydantic import BaseModel

from ..auth import get_admin_or_access_key
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Agent, Task
from ..services.task_service import create_task
from ..services.agent_service import compute_agent_status
import time

router = APIRouter(prefix="/api/minecraft", tags=["Minecraft"], dependencies=[Depends(get_admin_or_access_key)])

def run_sudo(cmd: str) -> str:
    try:
        result = subprocess.run(f"echo '8008' | sudo -S {cmd}", shell=True, capture_output=True, text=True, timeout=10)
        out = result.stdout.strip()
        if not out and result.stderr:
            return "ERR: " + result.stderr.strip()
        return out
    except Exception as e:
        return str(e)

STATS_FILE = "/var/lib/pcmanager/mc_player_stats.json"
MC_LOGS = "/opt/minecraft/server/logs"

def refresh_player_stats():
    stats = {}
    log_files = sorted(glob.glob(f"{MC_LOGS}/*.log*"), key=lambda x: Path(x).stat().st_mtime)
    for log_path in log_files:
        try:
            if log_path.endswith(".gz"):
                with gzip.open(log_path, 'rt', encoding='utf-8', errors='replace') as f:
                    lines = f.readlines()
            else:
                with open(log_path, 'r', encoding='utf-8', errors='replace') as f:
                    lines = f.readlines()
            for line in lines:
                m = re.search(r'\[(\d{2}:\d{2}:\d{2})\].*?(\w+) joined the game', line)
                if m:
                    time_str = m.group(1)
                    player = m.group(2)
                    if player not in stats:
                        stats[player] = {"joins": 0, "last_seen": ""}
                    stats[player]["joins"] += 1
                    fname = Path(log_path).stem
                    date_part = re.search(r'(\d{4}-\d{2}-\d{2})', fname)
                    if date_part:
                        stats[player]["last_seen"] = f"{date_part.group(1)} {time_str}"
                    else:
                        from datetime import date
                        stats[player]["last_seen"] = f"{date.today()} {time_str}"
        except Exception:
            pass
    try:
        with open(STATS_FILE, 'w') as f:
            json.dump(stats, f, ensure_ascii=False)
    except Exception:
        pass
    return stats

@router.get("/status")
def get_status():
    status_output = run_sudo("systemctl is-active minecraft")
    is_online = status_output == "active"

    ram = "0 MB"
    cpu = "0%"
    if is_online:
        try:
            ps_out = run_sudo("ps -C java -o %cpu,rss --no-headers | head -n 1")
            if ps_out and not ps_out.startswith(("sudo:", "ERR:")):
                parts = ps_out.split()
                if len(parts) >= 2:
                    cpu = f"{parts[0]}%"
                    ram = f"{int(parts[1]) // 1024} MB"
        except:
            pass

    return {
        "status": "online" if is_online else "offline",
        "cpu": cpu,
        "ram": ram,
    }

class ActionRequest(BaseModel):
    action: str

@router.post("/action")
def perform_action(req: ActionRequest):
    if req.action in ["start", "stop", "restart"]:
        run_sudo(f"systemctl {req.action} minecraft")
        return {"ok": True, "action": req.action}
    return {"ok": False, "error": "Invalid action"}

@router.get("/logs")
def get_logs():
    logs = run_sudo("tail -n 100 /opt/minecraft/server/logs/latest.log")
    return {"text": logs}

class CommandRequest(BaseModel):
    command: str

@router.post("/command")
def run_command_rcon(req: CommandRequest):
    cmd = req.command.replace('"', '\\"')
    out = run_sudo(f'mcrcon -H 127.0.0.1 -P 25575 -p "SecretRconPass123" "{cmd}"')
    return {"ok": True, "output": out}

@router.get("/player-stats")
def get_player_stats():
    try:
        stats = refresh_player_stats()
        players = [
            {"name": k, "joins": v["joins"], "last_seen": v["last_seen"]}
            for k, v in sorted(stats.items(), key=lambda x: -x[1]["joins"])
        ]
        return {"players": players, "total": len(players)}
    except Exception as e:
        return {"players": [], "total": 0, "error": str(e)}



