from __future__ import annotations

import json
import os
import shutil
import socket
import subprocess
import tarfile
import time
from datetime import datetime
from pathlib import Path
from typing import Any

import psutil
from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from ..auth import get_admin_or_access_key
from ..config import get_settings
from ..database import get_db
from ..models import Agent, LogEntry, Task
from ..services.agent_service import compute_agent_status, list_agents
from ..services.log_service import add_log
from ..services.network_service import server_info
from ..services.notify_service import telegram_notify


router = APIRouter(tags=["home"], dependencies=[Depends(get_admin_or_access_key)])
settings = get_settings()
STARTED_AT = time.time()
DATA_ROOT = Path("/data").resolve()
PROJECT_ROOT = Path("/home/pc/PCControlPersonal_Project")
RUNTIME_ROOT = Path("/opt/pcmanager")
REPORT_DIR = Path(os.getenv("PCMANAGER_REPORT_DIR", "/var/lib/pcmanager/reports"))


def run(command: list[str], timeout: int = 15) -> tuple[int, str]:
    try:
        proc = subprocess.run(command, text=True, capture_output=True, timeout=timeout)
        return proc.returncode, (proc.stdout + proc.stderr).strip()
    except Exception as exc:
        return 1, str(exc)


def ensure_data_dirs() -> None:
    for rel in [
        "files",
        "backups",
        "screenshots",
        "uploads",
        "media",
        "media/movies",
        "media/music",
        "media/photos",
    ]:
        (DATA_ROOT / rel).mkdir(parents=True, exist_ok=True)


def safe_data_path(raw: str = "") -> Path:
    ensure_data_dirs()
    value = (raw or "").strip().replace("\\", "/").lstrip("/")
    target = (DATA_ROOT / value).resolve()
    if target != DATA_ROOT and DATA_ROOT not in target.parents:
        raise HTTPException(status_code=400, detail="Path is outside /data")
    return target


def relative_data_path(path: Path) -> str:
    return path.resolve().relative_to(DATA_ROOT).as_posix()


def safe_data_filename(filename: str) -> str:
    cleaned = Path(filename or "upload.bin").name.strip().replace("\\", "_").replace("/", "_")
    return cleaned.strip(" .") or "upload.bin"


def unique_data_file_path(folder: Path, filename: str) -> Path:
    safe_name = safe_data_filename(filename)
    candidate = safe_data_path(f"{relative_data_path(folder)}/{safe_name}")
    if not candidate.exists():
        return candidate
    stem = candidate.stem or "file"
    suffix = candidate.suffix
    for index in range(1, 1000):
        next_candidate = safe_data_path(f"{relative_data_path(folder)}/{stem}_{index}{suffix}")
        if not next_candidate.exists():
            return next_candidate
    raise HTTPException(status_code=409, detail="Too many files with similar names")


async def save_data_uploads(folder_path: str, uploads: list[UploadFile], db: Session) -> dict[str, Any]:
    if not uploads:
        raise HTTPException(status_code=400, detail="No files uploaded")
    if len(uploads) > 100:
        raise HTTPException(status_code=400, detail="Too many files in one upload")
    folder = safe_data_path(folder_path)
    folder.mkdir(parents=True, exist_ok=True)
    max_bytes = settings.max_upload_mb * 1024 * 1024
    saved: list[dict[str, Any]] = []
    total_bytes = 0
    errors: list[dict[str, str]] = []
    for upload in uploads:
        original_name = upload.filename or "upload.bin"
        try:
            target = unique_data_file_path(folder, original_name)
            data = await upload.read(max_bytes + 1)
            if len(data) > max_bytes:
                raise HTTPException(status_code=413, detail=f"File is too large: {original_name}")
            target.write_bytes(data)
            size = target.stat().st_size
            total_bytes += size
            item = {
                "ok": True,
                "filename": target.name,
                "original_filename": Path(original_name).name,
                "path": relative_data_path(target),
                "size_bytes": size,
            }
            saved.append(item)
            add_log(db, "INFO", "files", "data_file_uploaded", f"Uploaded {relative_data_path(target)}", item)
        except HTTPException:
            raise
        except Exception as exc:
            errors.append({"filename": Path(original_name).name, "error": str(exc)})
    return {
        "ok": not errors,
        "count": len(saved),
        "total_bytes": total_bytes,
        "folder": relative_data_path(folder),
        "uploaded": saved,
        "errors": errors,
        "path": saved[0]["path"] if saved else "",
        "size_bytes": saved[0]["size_bytes"] if saved else 0,
    }


def service_active(name: str) -> bool:
    code, out = run(["systemctl", "is-active", name], timeout=5)
    return code == 0 and out.strip() == "active"


def ethernet_speed() -> str:
    code, out = run(["bash", "-lc", "command -v ethtool >/dev/null && ethtool enp4s0 2>/dev/null | grep 'Speed:' | awk '{print $2}' || true"], timeout=5)
    return out.strip() if code == 0 and out.strip() else "unknown"


def internet_ok() -> bool:
    try:
        socket.create_connection(("1.1.1.1", 53), timeout=3).close()
        return True
    except Exception:
        return False


def dns_ok() -> bool:
    try:
        socket.gethostbyname("api.telegram.org")
        return True
    except Exception:
        return False


def last_report() -> dict[str, Any]:
    path = REPORT_DIR / "latest.json"
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {"status": "ERROR", "summary": "Latest report is corrupted"}


def latest_backup() -> dict[str, Any]:
    ensure_data_dirs()
    backups = sorted((DATA_ROOT / "backups").glob("*.tar.gz"), key=lambda p: p.stat().st_mtime, reverse=True)
    if not backups:
        return {}
    item = backups[0]
    return {"name": item.name, "size_bytes": item.stat().st_size, "created_at": datetime.fromtimestamp(item.stat().st_mtime).isoformat()}


def recent_errors(db: Session, limit: int = 10) -> list[dict[str, Any]]:
    rows = (
        db.query(LogEntry)
        .filter(LogEntry.level.in_(["ERROR", "WARNING", "error", "warning"]))
        .order_by(LogEntry.created_at.desc())
        .limit(limit)
        .all()
    )
    return [
        {
            "time": row.created_at.isoformat() if row.created_at else "",
            "level": row.level,
            "source": row.source,
            "event": row.event,
            "message": row.message,
        }
        for row in rows
    ]


def system_metrics() -> dict[str, Any]:
    disk = shutil.disk_usage("/")
    data_disk = shutil.disk_usage(DATA_ROOT if DATA_ROOT.exists() else "/")
    temps: list[float] = []
    try:
        for entries in psutil.sensors_temperatures(fahrenheit=False).values():
            for entry in entries:
                if entry.current:
                    temps.append(float(entry.current))
    except Exception:
        pass
    return {
        "cpu_percent": psutil.cpu_percent(interval=0.2),
        "ram_percent": psutil.virtual_memory().percent,
        "ram_used": psutil.virtual_memory().used,
        "ram_total": psutil.virtual_memory().total,
        "disk_percent": round((disk.used / disk.total) * 100, 1),
        "disk_used": disk.used,
        "disk_total": disk.total,
        "data_free": data_disk.free,
        "temperature": round(max(temps), 1) if temps else None,
        "load": os.getloadavg() if hasattr(os, "getloadavg") else [0, 0, 0],
    }


@router.get("/api/home/status")
def home_status(db: Session = Depends(get_db)):
    ensure_data_dirs()
    agents = list_agents(db)
    online = [agent for agent in agents if compute_agent_status(agent) == "online"]
    info = server_info()
    report = last_report()
    return {
        "server": {
            "online": True,
            "uptime_seconds": int(time.time() - STARTED_AT),
            "uptime": f"{int(time.time() - STARTED_AT)}s",
            "hostname": socket.gethostname(),
            "local_ip": info.get("local_ip"),
            "base_url": info.get("base_url"),
            "public_url": settings.base_public_url,
            "port": settings.server_port,
            "version": settings.app_version,
            "telegram_bot": "online" if service_active("pcmanager-bot") else "offline",
            "pcmanager_server": "online" if service_active("pcmanager-server") else "offline",
        },
        "network": {"internet": internet_ok(), "internet_ok": internet_ok(), "dns": dns_ok(), "lan_speed": ethernet_speed(), "ethernet_speed": ethernet_speed()},
        "metrics": system_metrics(),
        "system": system_metrics(),
        "services": {"server": "online" if service_active("pcmanager-server") else "offline", "bot": "online" if service_active("pcmanager-bot") else "offline"},
        "agents": {
            "total": len(agents),
            "online": len(online),
            "offline": max(len(agents) - len(online), 0),
            "windows_agent": "online" if online else "offline",
        },
        "tasks": {
            "active": db.query(Task).filter(Task.status.in_(["queued", "pending", "running"])).count(),
            "failed": db.query(Task).filter(Task.status.in_(["failed", "error", "timeout"])).count(),
        },
        "latest_backup": latest_backup(),
        "backup": {"latest": latest_backup().get("name")},
        "latest_report": {
            "status": report.get("status"),
            "time": report.get("time"),
            "summary": report.get("summary"),
        },
        "diagnostics": {"latest_status": report.get("status"), "latest_time": report.get("time"), "summary": report.get("summary")},
        "errors": recent_errors(db, 5),
    }


@router.get("/api/home/errors")
def home_errors(db: Session = Depends(get_db)):
    return recent_errors(db, 50)


@router.post("/api/home/check")
def home_check(db: Session = Depends(get_db)):
    code, out = run(["bash", str(PROJECT_ROOT / "scripts" / "local_check.sh")], timeout=120)
    add_log(db, "INFO" if code == 0 else "WARNING", "web", "local_check_run", "Local diagnostics executed from Web UI", {"code": code})
    if code != 0:
        telegram_notify("PC Manager Local Check\nStatus: WARNING\nTriggered from Web UI")
    return {"ok": code == 0, "code": code, "output": out[-4000:], "latest": last_report()}


@router.post("/api/home/restart-server")
def home_restart_server(db: Session = Depends(get_db)):
    add_log(db, "WARNING", "web", "server_restart_requested", "pcmanager-server restart requested from Web UI", {})
    telegram_notify("PC Manager\nКоманда с сайта: перезапуск pcmanager-server.service")
    code, out = run(["sudo", "-n", "systemctl", "restart", "pcmanager-server.service"], timeout=20)
    if code != 0:
        add_log(db, "ERROR", "web", "server_restart_failed", "Server service restart failed", {"error": out})
        raise HTTPException(status_code=500, detail="Restart failed. Check sudoers/systemd permissions.")
    return {"ok": True, "message": "pcmanager-server.service restart requested"}


def create_backup(kind: str = "full") -> dict[str, Any]:
    ensure_data_dirs()
    stamp = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
    target = DATA_ROOT / "backups" / f"pcmanager-{kind}-{stamp}.tar.gz"
    sources = [RUNTIME_ROOT, Path("/etc/pcmanager/pcmanager.env"), Path("/var/lib/pcmanager")]
    if kind == "config":
        sources = [Path("/etc/pcmanager/pcmanager.env"), Path("/etc/systemd/system/pcmanager-server.service"), Path("/etc/systemd/system/pcmanager-bot.service")]
    elif kind == "project":
        sources = [RUNTIME_ROOT]
    def backup_filter(info: tarfile.TarInfo) -> tarfile.TarInfo | None:
        parts = Path(info.name).parts
        ignored = {"venv", ".venv", "__pycache__", ".git", "node_modules", "build", "dist"}
        if any(part in ignored or part.startswith("backup_") for part in parts):
            return None
        if info.name.endswith((".pyc", ".apk", ".idsig", ".jar", ".zip")):
            return None
        return info

    with tarfile.open(target, "w:gz") as tar:
        for source in sources:
            if source.exists():
                try:
                    tar.add(source, arcname=str(source).lstrip("/"), filter=backup_filter)
                except (OSError, PermissionError):
                    continue
    return {"name": target.name, "path": str(target), "size_bytes": target.stat().st_size, "kind": kind, "created_at": datetime.utcnow().isoformat()}


@router.post("/api/home/backup")
def home_backup(kind: str = Query(default="full"), db: Session = Depends(get_db)):
    backup = create_backup(kind)
    add_log(db, "INFO", "backup", "backup_created", f"Backup created: {backup['name']}", {"name": backup["name"], "kind": kind})
    telegram_notify(f"PC Manager\nНовый backup создан: {backup['name']}")
    return backup


@router.get("/api/backups")
def backups():
    ensure_data_dirs()
    items = []
    for path in sorted((DATA_ROOT / "backups").glob("*.tar.gz"), key=lambda p: p.stat().st_mtime, reverse=True):
        items.append({"name": path.name, "size_bytes": path.stat().st_size, "created_at": datetime.fromtimestamp(path.stat().st_mtime).isoformat()})
    return {"backups": items}


@router.post("/api/backups/create")
def backups_create(kind: str = Query(default="full"), db: Session = Depends(get_db)):
    return home_backup(kind, db)


@router.get("/api/backups/download/{name}")
def backups_download(name: str):
    path = safe_data_path(f"backups/{Path(name).name}")
    if not path.exists() or path.suffix != ".gz":
        raise HTTPException(status_code=404, detail="Backup not found")
    return FileResponse(path, filename=path.name, media_type="application/gzip")


@router.post("/api/backups/delete/{name}")
def backups_delete(name: str, confirm: str = Query(default=""), db: Session = Depends(get_db)):
    if confirm != "DELETE":
        raise HTTPException(status_code=400, detail="Type DELETE to confirm")
    path = safe_data_path(f"backups/{Path(name).name}")
    if not path.exists():
        raise HTTPException(status_code=404, detail="Backup not found")
    path.unlink()
    add_log(db, "WARNING", "backup", "backup_deleted", f"Backup deleted: {name}", {"name": name})
    return {"ok": True}


@router.get("/api/files/list")
def data_files_list(path: str = Query(default="")):
    target = safe_data_path(path)
    if not target.exists():
        raise HTTPException(status_code=404, detail="Path not found")
    if target.is_file():
        return {"path": relative_data_path(target), "type": "file", "size_bytes": target.stat().st_size}
    items = []
    def sort_key(p):
        is_dir = p.is_dir()
        if is_dir:
            return (0, 0, p.name.lower())
        else:
            try:
                mtime = p.stat().st_mtime
            except Exception:
                mtime = 0
            return (1, -mtime, p.name.lower())
    for item in sorted(target.iterdir(), key=sort_key):
        if item.name.startswith("."):
            continue
        stat = item.stat()
        items.append({
            "name": item.name,
            "path": relative_data_path(item),
            "type": "dir" if item.is_dir() else "file",
            "size_bytes": stat.st_size,
            "modified_at": datetime.fromtimestamp(stat.st_mtime).isoformat(),
        })
    return {"path": relative_data_path(target) if target != DATA_ROOT else "", "items": items, "storage": storage_info()}


@router.post("/api/files/upload")
async def data_files_upload(path: str = Query(default="uploads"), upload: list[UploadFile] = File(...), db: Session = Depends(get_db)):
    return await save_data_uploads(path, upload, db)


@router.get("/api/files/download")
def data_files_download(path: str):
    target = safe_data_path(path)
    if not target.exists() or not target.is_file():
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(target, filename=target.name)


@router.post("/api/files/mkdir")
def data_files_mkdir(path: str, db: Session = Depends(get_db)):
    target = safe_data_path(path)
    target.mkdir(parents=True, exist_ok=True)
    add_log(db, "INFO", "files", "folder_created", f"Folder created: {relative_data_path(target)}", {"path": relative_data_path(target)})
    return {"ok": True, "path": relative_data_path(target)}


@router.post("/api/files/delete")
def data_files_delete(path: str, confirm: str = Query(default=""), db: Session = Depends(get_db)):
    if confirm != "DELETE":
        raise HTTPException(status_code=400, detail="Type DELETE to confirm")
    target = safe_data_path(path)
    if target == DATA_ROOT or not target.exists():
        raise HTTPException(status_code=404, detail="Path not found")
    if target.is_dir():
        shutil.rmtree(target)
    else:
        target.unlink()
    add_log(db, "WARNING", "files", "data_file_deleted", f"Deleted {path}", {"path": path})
    return {"ok": True}


@router.post("/api/files/rename")
def data_files_rename(path: str, new_name: str, db: Session = Depends(get_db)):
    source = safe_data_path(path)
    if not source.exists():
        raise HTTPException(status_code=404, detail="Path not found")
    target = safe_data_path(f"{relative_data_path(source.parent)}/{Path(new_name).name}")
    source.rename(target)
    add_log(db, "INFO", "files", "data_file_renamed", f"Renamed {path} -> {relative_data_path(target)}", {"path": path, "new_path": relative_data_path(target)})
    return {"ok": True, "path": relative_data_path(target)}


def storage_info() -> dict[str, Any]:
    ensure_data_dirs()
    usage = shutil.disk_usage(DATA_ROOT)
    folders = {}
    for folder in ["files", "backups", "screenshots", "uploads", "media", "media/movies", "media/music", "media/photos"]:
        root = DATA_ROOT / folder
        total = 0
        for item in root.rglob("*"):
            if item.is_file():
                try:
                    total += item.stat().st_size
                except OSError:
                    pass
        folders[folder] = total
    return {
        "root": str(DATA_ROOT),
        "total": usage.total,
        "total_bytes": usage.total,
        "used": usage.used,
        "used_bytes": usage.used,
        "free": usage.free,
        "free_bytes": usage.free,
        "percent_used": round((usage.used / usage.total) * 100, 1) if usage.total else 0,
        "folders": folders,
    }


@router.get("/api/files/storage")
def data_files_storage():
    return storage_info()


def media_items(category: str | None = None) -> list[dict[str, Any]]:
    base = DATA_ROOT / "media"
    folder = base / category if category else base
    folder = safe_data_path(relative_data_path(folder))
    files = []
    for item in folder.rglob("*"):
        if item.is_file():
            files.append({"name": item.name, "path": relative_data_path(item), "size_bytes": item.stat().st_size, "modified_at": datetime.fromtimestamp(item.stat().st_mtime).isoformat()})
    return sorted(files, key=lambda x: x["modified_at"], reverse=True)[:500]


@router.get("/api/media/movies")
def media_movies():
    return {"items": media_items("movies")}


@router.get("/api/media/music")
def media_music():
    return {"items": media_items("music")}


@router.get("/api/media/photos")
def media_photos():
    return {"items": media_items("photos")}


@router.get("/api/media/stream")
def media_stream(path: str):
    target = safe_data_path(path)
    if DATA_ROOT / "media" not in target.parents and target != DATA_ROOT / "media":
        raise HTTPException(status_code=400, detail="Media path required")
    if not target.exists() or not target.is_file():
        raise HTTPException(status_code=404, detail="Media not found")
    return FileResponse(target, filename=target.name)


@router.post("/api/media/upload")
async def media_upload(category: str = Query(default="uploads"), upload: UploadFile = File(...), db: Session = Depends(get_db)):
    if category not in {"movies", "music", "photos"}:
        raise HTTPException(status_code=400, detail="Invalid media category")
    return await save_data_uploads(f"media/{category}", [upload], db)


def _tail_file(path: Path, lines: int = 200) -> str:
    if not path.exists() or not path.is_file():
        return ""
    try:
        return "\n".join(path.read_text(encoding="utf-8", errors="ignore").splitlines()[-lines:])
    except Exception as exc:
        return f"Не удалось прочитать {path}: {exc}"


def _read_service_log(service_name: str, plain_log: Path) -> dict[str, Any]:
    file_text = _tail_file(plain_log)
    code, out = run(["journalctl", "-q", "-u", service_name, "-n", "200", "--no-pager"], timeout=20)
    text = out.strip()
    permission_problem = "No journal files were opened" in text or "insufficient permissions" in text.lower()
    if code == 0 and text and not permission_problem:
        return {"ok": True, "source": "journalctl", "text": text}
    if file_text:
        return {"ok": True, "source": str(plain_log), "text": file_text}
    hint = (
        f"Логи {service_name} пока недоступны для пользователя сервиса.\n"
        "Проверь на сервере:\n"
        f"sudo journalctl -u {service_name} -n 100 --no-pager\n"
        "Если в Web UI снова нет journal-доступа, добавь пользователя pcmanager в группу systemd-journal:\n"
        "sudo usermod -aG systemd-journal pcmanager && sudo systemctl restart pcmanager-server\n"
    )
    if text:
        hint += "\nИсходный ответ journalctl:\n" + text
    return {"ok": False, "source": "fallback", "text": hint}


@router.get("/api/logs/server")
def logs_server():
    return _read_service_log("pcmanager-server", Path("/var/log/pcmanager/server.log"))


@router.get("/api/logs/bot")
def logs_bot():
    return _read_service_log("pcmanager-bot", Path("/var/log/pcmanager/bot.log"))


@router.get("/api/logs/errors")
def logs_errors():
    needles = ("ERROR", "WARNING", "Traceback", "Exception", "failed", "timeout", "disabled", "not configured")
    text = "\n".join([logs_server()["text"], logs_bot()["text"]])
    lines = [line for line in text.splitlines() if any(n.lower() in line.lower() for n in needles)]
    return {"count": len(lines), "lines": lines[-200:]}


@router.get("/api/logs/agent/{agent_id}")
def logs_agent(agent_id: str, db: Session = Depends(get_db)):
    rows = db.query(LogEntry).filter(LogEntry.meta.contains({"agent_id": agent_id})).order_by(LogEntry.created_at.desc()).limit(100).all()
    return [{"time": row.created_at.isoformat(), "level": row.level, "event": row.event, "message": row.message} for row in rows]


@router.get("/api/diagnostics/status")
def diagnostics_status():
    report = last_report()
    return {"available": bool(report), "status": report.get("status"), "time": report.get("time"), "summary": report.get("summary")}


@router.get("/api/diagnostics/latest")
def diagnostics_latest():
    return last_report()


@router.get("/api/diagnostics/reports")
def diagnostics_reports():
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    reports = []
    for path in sorted(REPORT_DIR.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True):
        if path.name == "latest.json":
            continue
        reports.append({"report_id": path.stem, "name": path.name, "created_at": datetime.fromtimestamp(path.stat().st_mtime).isoformat(), "size_bytes": path.stat().st_size})
    return reports[:100]


@router.get("/api/diagnostics/reports/{report_id}")
def diagnostics_report(report_id: str):
    safe = Path(report_id).stem
    path = REPORT_DIR / f"{safe}.json"
    if not path.exists():
        raise HTTPException(status_code=404, detail="Report not found")
    return json.loads(path.read_text(encoding="utf-8"))


@router.post("/api/diagnostics/run")
def diagnostics_run(db: Session = Depends(get_db)):
    return home_check(db)
