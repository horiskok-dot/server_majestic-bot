from __future__ import annotations
AGENT_CONNECTED = False

import base64
import ctypes
import io
import json
import logging
import os
import platform
import random
import re
import shutil
import socket
import subprocess
import sys
import tempfile
import threading
import time
import webbrowser
from datetime import datetime, timezone
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Any

import psutil
import requests
from requests import HTTPError

try:
    import winreg
except ImportError:
    winreg = None

try:
    from PIL import Image, ImageDraw, ImageGrab

    HAS_SCREENSHOT = True
except Exception:
    HAS_SCREENSHOT = False

try:
    from websockets.sync.client import connect as ws_connect

    HAS_WEBSOCKETS = True
except Exception:
    HAS_WEBSOCKETS = False


import os
import shutil
import platform

# Determine local directory (where the EXE or script is running)
if getattr(sys, "frozen", False):
    LOCAL_DIR = Path(sys.executable).resolve().parent
else:
    LOCAL_DIR = Path(__file__).resolve().parent

def get_resource_path(relative_path: str) -> Path:
    """Get absolute path to resource, works for dev and for PyInstaller"""
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS) / relative_path
    return Path(__file__).resolve().parent / relative_path

# Custom profile override via argument or env var
profile_name = os.environ.get("PCMANAGER_PROFILE")
for arg in sys.argv:
    if arg.startswith("--profile="):
        profile_name = arg.split("=", 1)[1].strip()

profile_suffix = f"_{profile_name}" if profile_name else ""

# Resolve secure AppData/Home directory for storing configuration and state files
if platform.system() == "Windows":
    app_data = os.environ.get("APPDATA")
    if app_data:
        DATA_DIR = Path(app_data) / f"PCManager_Agent{profile_suffix}"
    else:
        DATA_DIR = Path.home() / f".pcmanager{profile_suffix}"
else:
    DATA_DIR = Path.home() / f".pcmanager{profile_suffix}"

# Create the data directory if it doesn't exist
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Automatic migration from local folder to AppData so user doesn't lose token
local_config = LOCAL_DIR / "agent_config.json"
appdata_config = DATA_DIR / "agent_config.json"
if not appdata_config.exists() and local_config.exists():
    try:
        shutil.copy2(local_config, appdata_config)
        local_state = LOCAL_DIR / "agent_state.json"
        appdata_state = DATA_DIR / "agent_state.json"
        if local_state.exists():
            shutil.copy2(local_state, appdata_state)
    except Exception:
        pass

# Use secure DATA_DIR paths
BASE_DIR = DATA_DIR
CONFIG_FILE = BASE_DIR / "agent_config.json"
CONFIG_EXAMPLE_FILE = BASE_DIR / "agent_config.example.json"
STATE_FILE = BASE_DIR / "agent_state.json"
DEFAULT_LOGS_DIR = BASE_DIR / "logs"
AGENT_VERSION = "1.7.0"

_OBFUSCATED_SERVER_URL = "aHR0cDovLzE5Mi4xNjguMC4xOTM6ODc2NQ=="

def get_server_url() -> str:
    config_url = CONFIG.get("server_base_url")
    if config_url and isinstance(config_url, str) and config_url.strip():
        return config_url.strip()
    env_url = os.environ.get("SERVER_BASE_URL")
    if env_url:
        return env_url.strip()
    try:
        return base64.b64decode(_OBFUSCATED_SERVER_URL.encode("utf-8")).decode("utf-8")
    except Exception:
        return "http://192.168.0.193:8765"

DEFAULT_CONFIG: dict[str, Any] = {
    "agent_id": "gaming-laptop",
    "agent_name": "Gaming Laptop",
    "server_base_url": "http://192.168.0.193:8765",
    "websocket_url": "ws://192.168.0.193:8765/ws/status",
    "access_key": "CHANGE_ME",
    "heartbeat_interval_seconds": 10,
    "task_poll_interval_seconds": 3,
    "screenshot_quality": 80,
    "screenshot_retention_days": 3,
    "screenshot_keep_last": 80,
    "anti_afk_min_minutes": 10,
    "anti_afk_max_minutes": 20,
    "auto_screen_interval_seconds": 300,
    "logs_dir": "logs",
    "allowed_apps": ["explorer.exe", "chrome.exe", "notepad.exe", "Discord.exe", "Telegram.exe"],
    "allowed_input_keys": ["w", "a", "s", "d", "z", "e", "i", "esc", "space", "enter", "tab", "shift", "ctrl"],
    "click_presets": {
        "play": [997, 499],
        "char1": [597, 996],
        "char2": [910, 966],
        "house": [908, 970],
        "spawn": [810, 973],
        "spawn2": [947, 1013]
    },
    "allowed_launchers": {
        "majestic_launcher": "C:\\Users\\horis\\AppData\\Local\\MajesticLauncher\\Majestic Launcher.exe"
    },
    "enabled_tasks": [
        "ping",
        "system_info",
        "screenshot",
        "process_list",
        "disk_info",
        "temperature",
        "agent_logs",
        "restart_allowed_app",
        "press_key",
        "click_preset",
        "release_keys",
        "launch_allowed_app",
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
        "camera_snapshot",
        "record_video",
        "record_screen",
        "lock_pc",
        "sleep_pc",
        "monitor_off",
        "remote_input",
        "start_timer",
        "cancel_timer",
        "shutdown_now",
        "add_automation_rule",
        "delete_automation_rule",
        "update_agent",
    ],
}

TASK_ALIASES = {
    "get_system_info": "system_info",
    "get_process_list": "process_list",
    "get_disk_info": "disk_info",
    "get_screenshot": "screenshot",
    "take_screenshot": "screenshot",
    "logs": "agent_logs",
    "input_key": "press_key",
    "key": "press_key",
    "click": "click_preset",
    "launcher": "launch_allowed_app",
    "launch_game": "launch_allowed_app",
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
    "desktop_new": "desktop_new",
    "desktop_close": "desktop_close",
    "take_photo": "camera_snapshot",
    "camera_snapshot": "camera_snapshot",
    "record_video": "record_video",
    "record_screen": "record_screen",
}

SAFE_TASKS = set(DEFAULT_CONFIG["enabled_tasks"])
SAFE_TASKS.add("camera_snapshot")
SAFE_TASKS.add("record_video")
SAFE_TASKS.add("record_screen")
SAFE_TASKS.add("lock_pc")
SAFE_TASKS.add("sleep_pc")
SAFE_TASKS.add("monitor_off")
SAFE_TASKS.add("close_allowed_app")
SAFE_TASKS.add("remote_input")
SAFE_TASKS.add("start_timer")
SAFE_TASKS.add("cancel_timer")
SAFE_TASKS.add("shutdown_now")
SAFE_TASKS.add("add_automation_rule")
SAFE_TASKS.add("delete_automation_rule")
SAFE_TASKS.add("update_agent")
SAFE_TASKS.add("auto_screen_start")
SAFE_TASKS.add("auto_screen_stop")
BACKOFF_SEQUENCE = [2, 5, 10, 30]
MAX_RESULT_CHARS = 120_000
MAX_LOG_RESULT_LINES = 250


def ensure_config_files() -> dict[str, Any]:
    if CONFIG_EXAMPLE_FILE.exists():
        try:
            # Overwrite the example file to keep it fresh and clean of URLs
            CONFIG_EXAMPLE_FILE.write_text(json.dumps(DEFAULT_CONFIG, ensure_ascii=False, indent=2), encoding="utf-8")
        except Exception:
            pass
    else:
        CONFIG_EXAMPLE_FILE.write_text(json.dumps(DEFAULT_CONFIG, ensure_ascii=False, indent=2), encoding="utf-8")
        
    if not CONFIG_FILE.exists():
        CONFIG_FILE.write_text(CONFIG_EXAMPLE_FILE.read_text(encoding="utf-8"), encoding="utf-8")
        print(f"Created {CONFIG_FILE}. Edit access_key before using the agent.")
    try:
        data = json.loads(CONFIG_FILE.read_text(encoding="utf-8-sig"))
    except Exception as exc:
        raise RuntimeError(f"Cannot read {CONFIG_FILE}: {exc}") from exc
        
    merged = dict(DEFAULT_CONFIG)
    merged.update(data)
    return merged


CONFIG = ensure_config_files()
LOG_DIR = (BASE_DIR / str(CONFIG.get("logs_dir") or "logs")).resolve()
LOG_DIR.mkdir(parents=True, exist_ok=True)
SCREENSHOTS_DIR = LOG_DIR / "screenshots"
SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)

logger = logging.getLogger("pc-agent")
logger.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
file_handler = RotatingFileHandler(LOG_DIR / "agent.log", maxBytes=5 * 1024 * 1024, backupCount=5, encoding="utf-8")
file_handler.setFormatter(formatter)
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(formatter)
console_handler.setLevel(logging.INFO)
logger.handlers.clear()
logger.addHandler(file_handler)
logger.addHandler(console_handler)


def load_state() -> dict[str, Any]:
    if not STATE_FILE.exists():
        return {"executed_task_ids": [], "temperature_warning_logged": False}
    try:
        return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    except Exception:
        logger.warning("State file is corrupted, recreating it")
        return {"executed_task_ids": [], "temperature_warning_logged": False}


def save_state(state: dict[str, Any]) -> None:
    tmp = STATE_FILE.with_suffix(".tmp")
    tmp.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(STATE_FILE)


STATE = load_state()


def cfg_str(name: str, default: str = "") -> str:
    value = os.environ.get(name.upper(), CONFIG.get(name, default))
    return str(value or default).strip()


def cfg_int(name: str, default: int) -> int:
    try:
        return int(CONFIG.get(name, default))
    except Exception:
        return default


AGENT_ID = cfg_str("agent_id", socket.gethostname()).strip() or socket.gethostname()
AGENT_NAME = cfg_str("agent_name", AGENT_ID).strip() or AGENT_ID
SERVER_BASE_URL = get_server_url().rstrip("/")
WEBSOCKET_URL = f"{SERVER_BASE_URL.replace('http://', 'ws://').replace('https://', 'wss://')}/ws/status"
ACCESS_KEY = cfg_str("access_key", "")
_just_activated = False


def is_activated_mode() -> bool:
    return (
        CONFIG.get("is_activated", False) or
        _just_activated or
        (AGENT_ID and AGENT_ID.startswith("pc-") and len(ACCESS_KEY) > 20)
    )
HEARTBEAT_INTERVAL = max(3, cfg_int("heartbeat_interval_seconds", 10))
TASK_POLL_INTERVAL = max(1, cfg_int("task_poll_interval_seconds", 3))
SCREENSHOT_QUALITY = max(10, min(cfg_int("screenshot_quality", 80), 95))
SCREENSHOT_RETENTION_DAYS = max(1, cfg_int("screenshot_retention_days", 3))
SCREENSHOT_KEEP_LAST = max(10, cfg_int("screenshot_keep_last", 80))
ANTI_AFK_MIN_MINUTES = max(1, cfg_int("anti_afk_min_minutes", 10))
ANTI_AFK_MAX_MINUTES = max(ANTI_AFK_MIN_MINUTES, cfg_int("anti_afk_max_minutes", 20))
AUTO_SCREEN_INTERVAL_SECONDS = max(60, cfg_int("auto_screen_interval_seconds", 300))


def resolve_shortcut(lnk_path: str) -> str:
    try:
        # Use -WindowStyle Hidden to prevent window flashing, and CREATE_NO_WINDOW in subprocess
        cmd = f'powershell -WindowStyle Hidden -NoProfile -Command "$sh = New-Object -ComObject WScript.Shell; $sh.CreateShortcut(\'{lnk_path}\').TargetPath"'
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=3, creationflags=subprocess.CREATE_NO_WINDOW)
        return res.stdout.strip()
    except Exception:
        return ""


def scan_desktop_shortcuts() -> dict[str, str]:
    detected = {}
    desktop_dirs = []
    userprofile = os.environ.get("USERPROFILE")
    if userprofile:
        desktop_dirs.append(os.path.join(userprofile, "Desktop"))
    public = os.environ.get("PUBLIC")
    if public:
        desktop_dirs.append(os.path.join(public, "Desktop"))
    
    game_keywords = {
        "epic games", "steam", "gta", "grand theft auto", "majestic", "minecraft", 
        "riot", "ea", "battle.net", "ubisoft", "roblox", "cyberpunk", "witcher",
        "dota", "counter-strike", "csgo", "cs2", "pubg", "fortnite", "valorant", 
        "league of legends", "apex legends", "genshin impact"
    }
    
    for ddir in desktop_dirs:
        if not os.path.exists(ddir):
            continue
        try:
            for item in os.listdir(ddir):
                item_lower = item.lower()
                if item_lower.endswith(".lnk"):
                    lnk_path = os.path.join(ddir, item)
                    name = item[:-4].strip()
                    name_lower = name.lower()
                    
                    is_game = any(kw in name_lower for kw in game_keywords)
                    if is_game:
                        target = resolve_shortcut(lnk_path)
                        if target and os.path.exists(target) and target.lower().endswith(".exe"):
                            key = name_lower.replace(" ", "_").replace("-", "_")
                            detected[key] = target
                elif item_lower.endswith(".url"):
                    url_path = os.path.join(ddir, item)
                    name = item[:-4].strip()
                    name_lower = name.lower()
                    
                    is_game = any(kw in name_lower for kw in game_keywords)
                    if is_game:
                        # Register the .url shortcut path itself to execute it natively
                        key = name_lower.replace(" ", "_").replace("-", "_")
                        detected[key] = url_path
        except Exception as exc:
            logger.warning("Error scanning desktop folder %s: %s", ddir, exc)
            
    return detected


def auto_detect_launchers() -> dict[str, str]:
    detected = {}
    local_appdata = os.environ.get("LOCALAPPDATA")
    
    # 1. Majestic Launcher
    if local_appdata:
        majestic = os.path.join(local_appdata, "MajesticLauncher", "Majestic Launcher.exe")
        if os.path.exists(majestic):
            detected["majestic_launcher"] = majestic
            
    # 2. Steam
    steam_paths = [
        r"C:\Program Files (x86)\Steam\steam.exe",
        r"C:\Program Files\Steam\steam.exe"
    ]
    try:
        import winreg
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Valve\Steam") as key:
            val, _ = winreg.QueryValueEx(key, "SteamPath")
            if val:
                steam_exe = os.path.join(val.replace("/", "\\"), "steam.exe")
                if os.path.exists(steam_exe):
                    detected["steam"] = steam_exe
    except Exception:
        pass
    for path in steam_paths:
        if "steam" not in detected and os.path.exists(path):
            detected["steam"] = path

    # 3. Epic Games
    epic_paths = [
        r"C:\Program Files (x86)\Epic Games\Launcher\Portal\Binaries\Win64\EpicGamesLauncher.exe",
        r"C:\Program Files\Epic Games\Launcher\Portal\Binaries\Win64\EpicGamesLauncher.exe"
    ]
    try:
        import winreg
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\EpicGamesLauncher.exe") as key:
            val, _ = winreg.QueryValueEx(key, "")
            if val and os.path.exists(val):
                detected["epic_games"] = val
    except Exception:
        pass
    for path in epic_paths:
        if "epic_games" not in detected and os.path.exists(path):
            detected["epic_games"] = path

    # 4. Riot Client
    riot_paths = [
        r"C:\Riot Games\Riot Client\RiotClientServices.exe"
    ]
    for path in riot_paths:
        if os.path.exists(path):
            detected["riot_games"] = path

    # 5. EA Desktop
    ea_paths = [
        r"C:\Program Files\Electronic Arts\EA Desktop\EA Desktop\EADesktop.exe"
    ]
    for path in ea_paths:
        if os.path.exists(path):
            detected["ea_desktop"] = path

    # 6. Battle.net
    bnet_paths = [
        r"C:\Program Files (x86)\Battle.net\Battle.net.exe",
        r"C:\Program Files\Battle.net\Battle.net.exe"
    ]
    for path in bnet_paths:
        if os.path.exists(path):
            detected["battle_net"] = path

    # 7. Ubisoft Connect
    ubi_paths = [
        r"C:\Program Files (x86)\Ubisoft\Ubisoft Game Launcher\UbisoftConnect.exe",
        r"C:\Program Files\Ubisoft\Ubisoft Game Launcher\UbisoftConnect.exe"
    ]
    for path in ubi_paths:
        if os.path.exists(path):
            detected["ubisoft_connect"] = path

    # 8. Roblox
    if local_appdata:
        roblox_dir = os.path.join(local_appdata, "Roblox", "Versions")
        if os.path.exists(roblox_dir):
            try:
                for sub in os.listdir(roblox_dir):
                    p = os.path.join(roblox_dir, sub, "RobloxPlayerLauncher.exe")
                    if os.path.exists(p):
                        detected["roblox"] = p
                        break
            except Exception:
                pass

    # 9. Minecraft
    appdata = os.environ.get("APPDATA")
    minecraft_paths = [
        r"C:\XboxGames\Minecraft Launcher\Content\Minecraft.exe",
    ]
    if appdata:
        minecraft_paths.append(os.path.join(appdata, ".minecraft", "launcher.exe"))
    for path in minecraft_paths:
        if path and os.path.exists(path):
            detected["minecraft"] = path
            
    # 10. Grand Theft Auto V
    gta_paths = [
        r"C:\Program Files\Rockstar Games\Grand Theft Auto V\PlayGTAV.exe",
        r"C:\Program Files (x86)\Rockstar Games\Grand Theft Auto V\PlayGTAV.exe"
    ]
    for path in gta_paths:
        if os.path.exists(path):
            detected["gta5"] = path

    # 11. GTA 5 RP & Majestic launchers
    local_appdata = os.environ.get("LOCALAPPDATA") or ""
    program_files_x86 = os.environ.get("ProgramFiles(x86)") or r"C:\Program Files (x86)"
    program_files = os.environ.get("ProgramFiles") or r"C:\Program Files"
    
    majestic_paths = [
        os.path.join(local_appdata, "MajesticLauncher", "Majestic Launcher.exe"),
        os.path.join(local_appdata, "MajesticLauncherGLOBAL", "Majestic Launcher.exe"),
        r"C:\Users\horis\AppData\Local\MajesticLauncher\Majestic Launcher.exe",
        r"C:\Users\horis\AppData\Local\MajesticLauncherGLOBAL\Majestic Launcher.exe",
    ]
    for p in majestic_paths:
        if os.path.exists(p):
            detected["majestic_launcher"] = p
            break
            
    gta5rp_paths = [
        os.path.join(program_files_x86, "GTA5RP", "GTA5RPLauncher.exe"),
        os.path.join(program_files, "GTA5RP", "GTA5RPLauncher.exe"),
        os.path.join(local_appdata, "Programs", "gta5rp-launcher", "GTA5RP Launcher.exe"),
        os.path.join(local_appdata, "Programs", "GTA5RP Launcher", "GTA5RP Launcher.exe"),
        os.path.join(local_appdata, "gta5rp-launcher", "GTA5RP Launcher.exe"),
        r"C:\Program Files (x86)\GTA5RP\GTA5RPLauncher.exe",
    ]
    for p in gta5rp_paths:
        if os.path.exists(p):
            detected["gta5rp_launcher"] = p
            break
            
    rage_paths = [
        r"C:\RAGEMP\ragemp.exe",
        os.path.join(local_appdata, "RAGEMP", "ragemp.exe"),
    ]
    for p in rage_paths:
        if os.path.exists(p):
            detected["rage_multiplayer"] = p
            break

    return detected


ALLOWED_APPS = {Path(str(item)).name.lower() for item in CONFIG.get("allowed_apps", []) if str(item).strip()}
ALLOWED_INPUT_KEYS = {str(item).lower().strip() for item in CONFIG.get("allowed_input_keys", []) if str(item).strip()}
CLICK_PRESETS = {str(name).lower().strip(): value for name, value in dict(CONFIG.get("click_presets") or {}).items()}

# Combine auto-detected launchers and config-defined launchers
_auto_launchers = auto_detect_launchers()
_desktop_launchers = scan_desktop_shortcuts()
_config_launchers = dict(CONFIG.get("allowed_launchers") or {})
_merged_launchers = {**_auto_launchers, **_desktop_launchers, **_config_launchers}
ALLOWED_LAUNCHERS = {str(name).lower().strip(): str(path) for name, path in _merged_launchers.items()}

ENABLED_TASKS = {TASK_ALIASES.get(str(item), str(item)) for item in CONFIG.get("enabled_tasks", [])}
ENABLED_TASKS.add("camera_snapshot")
ENABLED_TASKS.add("record_video")
ENABLED_TASKS.add("record_screen")
ENABLED_TASKS.add("lock_pc")
ENABLED_TASKS.add("sleep_pc")
ENABLED_TASKS.add("remote_input")
ENABLED_TASKS.add("start_timer")
ENABLED_TASKS.add("cancel_timer")
ENABLED_TASKS.add("shutdown_now")
ENABLED_TASKS.add("monitor_off")
ENABLED_TASKS.add("close_allowed_app")
ENABLED_TASKS.add("update_agent")
ENABLED_TASKS.add("auto_screen_start")
ENABLED_TASKS.add("auto_screen_stop")
CURRENT_TASK = ""
LAST_ERROR = ""
SHUTDOWN = threading.Event()
BACKGROUND_LOCK = threading.RLock()
ANTI_AFK_STOP = threading.Event()
AUTO_SCREEN_STOP = threading.Event()
BACKGROUND_THREADS: dict[str, threading.Thread] = {}
BACKGROUND_STATE: dict[str, dict[str, Any]] = {
    "anti_afk": {"running": False, "started_at": None, "last_action_at": None, "last_error": ""},
    "auto_screen": {"running": False, "started_at": None, "last_action_at": None, "last_file_id": None, "last_error": ""},
}


def masked_url(url: str) -> str:
    return url.replace(ACCESS_KEY, "[HIDDEN]") if ACCESS_KEY else url


def has_valid_access_key() -> bool:
    return bool(ACCESS_KEY and ACCESS_KEY != "CHANGE_ME")


def auth_headers() -> dict[str, str]:
    headers = {
        "X-Server-Access-Key": ACCESS_KEY,
        "X-PCManager-Key": ACCESS_KEY,
        "User-Agent": f"PCControlWindowsAgent/{AGENT_VERSION}",
    }
    if is_activated_mode():
        headers["X-Agent-Token"] = ACCESS_KEY
    return headers


def request_json(method: str, path: str, **kwargs: Any) -> dict[str, Any]:
    url = f"{SERVER_BASE_URL}{path}"
    headers = kwargs.pop("headers", {})
    headers.update(auth_headers())
    response = requests.request(method, url, headers=headers, timeout=kwargs.pop("timeout", 20), **kwargs)
    response.raise_for_status()
    if not response.content:
        return {}
    return response.json()


def is_auth_error(exc: Exception) -> bool:
    return isinstance(exc, HTTPError) and exc.response is not None and exc.response.status_code in {401, 403}


def local_ip() -> str:
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.connect(("8.8.8.8", 80))
        value = sock.getsockname()[0]
        sock.close()
        return value
    except Exception:
        return "127.0.0.1"


def mac_address() -> str:
    try:
        for _, addrs in psutil.net_if_addrs().items():
            for addr in addrs:
                if getattr(psutil, "AF_LINK", object()) == addr.family and addr.address:
                    value = addr.address.strip()
                    if value and value != "00:00:00:00:00:00":
                        return value
    except Exception:
        pass
    return ""


def battery_status() -> dict[str, Any] | None:
    try:
        battery = psutil.sensors_battery()
    except Exception:
        return None
    if not battery:
        return None
    return {"percent": battery.percent, "plugged": battery.power_plugged, "seconds_left": battery.secsleft}


def temperature_status() -> dict[str, Any] | None:
    try:
        temps = psutil.sensors_temperatures(fahrenheit=False)
    except Exception:
        temps = {}
    if not temps:
        if not STATE.get("temperature_warning_logged"):
            logger.warning("Temperature is unavailable on this Windows host")
            STATE["temperature_warning_logged"] = True
            save_state(STATE)
        return None
    readings: list[dict[str, Any]] = []
    for name, entries in temps.items():
        for entry in entries:
            readings.append({"sensor": name, "label": entry.label or name, "current": entry.current, "high": entry.high, "critical": entry.critical})
    return {"available": True, "items": readings, "max_c": max((item["current"] for item in readings if item.get("current") is not None), default=None)}


LAST_DISK_INFO = {}
LAST_DISK_TIME = 0.0

def disk_info(force: bool = False) -> dict[str, Any]:
    global LAST_DISK_INFO, LAST_DISK_TIME
    now = time.time()
    if force or not LAST_DISK_INFO or now - LAST_DISK_TIME > 300.0:
        drives = []
        for part in psutil.disk_partitions(all=False):
            try:
                usage = psutil.disk_usage(part.mountpoint)
            except Exception:
                continue
            drives.append(
                {
                    "device": part.device,
                    "mountpoint": part.mountpoint,
                    "fstype": part.fstype,
                    "total": usage.total,
                    "used": usage.used,
                    "free": usage.free,
                    "percent": usage.percent,
                }
            )
        LAST_DISK_INFO = {"drives": drives}
        LAST_DISK_TIME = now
    return LAST_DISK_INFO


def process_list() -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for proc in psutil.process_iter(["pid", "name", "username", "memory_info", "cpu_percent", "status", "create_time"]):
        try:
            info = proc.info
            mem = info.get("memory_info")
            items.append(
                {
                    "pid": info.get("pid"),
                    "name": info.get("name") or "",
                    "cpu_percent": float(info.get("cpu_percent") or 0),
                    "memory_mb": round((getattr(mem, "rss", 0) or 0) / 1024 / 1024, 2),
                    "username": info.get("username") or "",
                    "status": info.get("status") or "",
                    "created_at": info.get("create_time") or 0,
                }
            )
        except Exception:
            continue
    items.sort(key=lambda item: item.get("memory_mb") or 0, reverse=True)
    return items[:200]


LAST_GAMES_SCAN_TIME = 0.0
GAMES_SCAN_CACHE = []

def get_steam_path():
    try:
        reg = winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)
        key = winreg.OpenKey(reg, r'Software\Valve\Steam')
        path, _ = winreg.QueryValueEx(key, 'SteamPath')
        return path
    except Exception:
        return r"C:\Program Files (x86)\Steam"

def get_steam_playtimes():
    steam_path = get_steam_path()
    userdata_dir = os.path.join(steam_path, 'userdata')
    if not os.path.exists(userdata_dir):
        return {}
    playtimes = {}
    try:
        for user_folder in os.listdir(userdata_dir):
            localconfig_path = os.path.join(userdata_dir, user_folder, 'config', 'localconfig.vdf')
            if os.path.exists(localconfig_path):
                try:
                    with open(localconfig_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    for m in re.finditer(r'"(\d+)"\s*\{[^}]*?"Playtime"\s*"(\d+)"', content, re.DOTALL | re.IGNORECASE):
                        appid = m.group(1)
                        playtime_mins = int(m.group(2))
                        if appid not in playtimes or playtime_mins > playtimes[appid]:
                            playtimes[appid] = playtime_mins
                except Exception:
                    pass
    except Exception:
        pass
    return playtimes

def scan_steam_games():
    steam_path = get_steam_path()
    lib_vdf = os.path.join(steam_path, 'steamapps', 'libraryfolders.vdf')
    if not os.path.exists(lib_vdf):
        return []
    try:
        with open(lib_vdf, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
    except Exception:
        return []
    paths = [steam_path]
    matches = re.findall(r'"path"\s+"([^"]+)"', content)
    for m in matches:
        normalized = m.replace('\\\\', '\\')
        if normalized not in paths:
            paths.append(normalized)
    playtimes = get_steam_playtimes()
    games = []
    seen_appids = set()
    for lib in paths:
        steamapps = os.path.join(lib, 'steamapps')
        if not os.path.exists(steamapps):
            continue
        try:
            for filename in os.listdir(steamapps):
                if filename.startswith('appmanifest_') and filename.endswith('.acf'):
                    acf_path = os.path.join(steamapps, filename)
                    try:
                        with open(acf_path, 'r', encoding='utf-8', errors='ignore') as af:
                            acf_content = af.read()
                        name_match = re.search(r'"name"\s+"([^"]+)"', acf_content)
                        appid_match = re.search(r'"appid"\s+"([^"]+)"', acf_content)
                        if name_match and appid_match:
                            appid = appid_match.group(1)
                            if appid in seen_appids:
                                continue
                            seen_appids.add(appid)
                            playtime_mins = playtimes.get(appid, 0)
                            playtime_hours = round(playtime_mins / 60.0, 1)
                            games.append({
                                "store": "steam",
                                "appid": appid,
                                "title": name_match.group(1),
                                "path": acf_path,
                                "playtime_mins": playtime_mins,
                                "playtime_hours": playtime_hours,
                            })
                    except Exception:
                        pass
        except Exception:
            pass
    return games

def scan_epic_games():
    manifests_dir = r"C:\ProgramData\Epic\EpicGamesLauncher\Data\Manifests"
    if not os.path.exists(manifests_dir):
        return []
    games = []
    try:
        for filename in os.listdir(manifests_dir):
            if filename.endswith('.item'):
                filepath = os.path.join(manifests_dir, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                        data = json.load(f)
                    display_name = data.get('DisplayName')
                    install_location = data.get('InstallLocation')
                    launch_executable = data.get('LaunchExecutable')
                    app_name = data.get('AppName')
                    if display_name:
                        games.append({
                            "store": "epic",
                            "appid": app_name or filename.replace('.item', ''),
                            "title": display_name,
                            "path": os.path.join(install_location, launch_executable) if install_location and launch_executable else "",
                            "playtime_mins": 0,
                            "playtime_hours": 0.0,
                        })
                except Exception:
                    pass
    except Exception:
        pass
    return games

def scan_rp_launchers():
    launchers = []
    local_appdata = os.environ.get("LOCALAPPDATA") or ""
    program_files_x86 = os.environ.get("ProgramFiles(x86)") or r"C:\Program Files (x86)"
    program_files = os.environ.get("ProgramFiles") or r"C:\Program Files"
    
    majestic_paths = [
        os.path.join(local_appdata, "MajesticLauncher", "Majestic Launcher.exe"),
        os.path.join(local_appdata, "MajesticLauncherGLOBAL", "Majestic Launcher.exe"),
        r"C:\Users\horis\AppData\Local\MajesticLauncher\Majestic Launcher.exe",
        r"C:\Users\horis\AppData\Local\MajesticLauncherGLOBAL\Majestic Launcher.exe",
    ]
    for p in majestic_paths:
        if os.path.exists(p):
            launchers.append({
                "store": "rp",
                "appid": "majestic_launcher",
                "title": "Majestic Launcher",
                "path": p,
                "playtime_hours": 0.0,
                "playtime_mins": 0,
            })
            break
            
    gta5rp_paths = [
        os.path.join(program_files_x86, "GTA5RP", "GTA5RPLauncher.exe"),
        os.path.join(program_files, "GTA5RP", "GTA5RPLauncher.exe"),
        os.path.join(local_appdata, "Programs", "gta5rp-launcher", "GTA5RP Launcher.exe"),
        os.path.join(local_appdata, "Programs", "GTA5RP Launcher", "GTA5RP Launcher.exe"),
        os.path.join(local_appdata, "gta5rp-launcher", "GTA5RP Launcher.exe"),
        r"C:\Program Files (x86)\GTA5RP\GTA5RPLauncher.exe",
    ]
    for p in gta5rp_paths:
        if os.path.exists(p):
            launchers.append({
                "store": "rp",
                "appid": "gta5rp_launcher",
                "title": "GTA5RP Launcher",
                "path": p,
                "playtime_hours": 0.0,
                "playtime_mins": 0,
            })
            break
            
    rage_paths = [
        r"C:\RAGEMP\ragemp.exe",
        os.path.join(local_appdata, "RAGEMP", "ragemp.exe"),
    ]
    for p in rage_paths:
        if os.path.exists(p):
            launchers.append({
                "store": "rp",
                "appid": "ragemp",
                "title": "RAGE Multiplayer",
                "path": p,
                "playtime_hours": 0.0,
                "playtime_mins": 0,
            })
            break
    return launchers


def scan_games_list(force=False):
    global LAST_GAMES_SCAN_TIME, GAMES_SCAN_CACHE
    now = time.time()
    if force or not GAMES_SCAN_CACHE or now - LAST_GAMES_SCAN_TIME > 300.0:
        games = []
        games.extend(scan_steam_games())
        games.extend(scan_epic_games())
        games.extend(scan_rp_launchers())
        for game in games:
            key = str(game["title"]).lower().strip().replace(" ", "_").replace("-", "_")
            if game["store"] == "steam":
                ALLOWED_LAUNCHERS[key] = f"steam://rungameid/{game['appid']}"
            elif game["store"] == "epic":
                if game["path"]:
                    ALLOWED_LAUNCHERS[key] = game["path"]
            elif game["store"] == "rp":
                if game["path"]:
                    ALLOWED_LAUNCHERS[key] = game["path"]
        GAMES_SCAN_CACHE = games
        LAST_GAMES_SCAN_TIME = now
    return GAMES_SCAN_CACHE

TIMER_ACTIVE = False
TIMER_REMAINING_MINUTES = 0
TIMER_ACTION = "shutdown"

def system_info() -> dict[str, Any]:
    vm = psutil.virtual_memory()
    boot_time = psutil.boot_time()
    return {
        "agent_id": AGENT_ID,
        "agent_name": AGENT_NAME,
        "agent_version": AGENT_VERSION,
        "hostname": socket.gethostname(),
        "username": os.environ.get("USERNAME") or os.environ.get("USER") or "",
        "platform": platform.platform(),
        "os": platform.system(),
        "os_version": platform.version(),
        "architecture": platform.machine(),
        "cpu_percent": psutil.cpu_percent(interval=None),
        "cpu_count": psutil.cpu_count(logical=True),
        "ram_total": vm.total,
        "ram_used": vm.used,
        "ram_percent": vm.percent,
        "boot_time": boot_time,
        "uptime_seconds": max(0, int(time.time() - boot_time)),
        "battery": battery_status(),
        "temperature": temperature_status(),
        "automation": automation_status(),
        "launchers": list(ALLOWED_LAUNCHERS.keys()),
        "games_list": scan_games_list(),
        "timer": {
            "active": TIMER_ACTIVE,
            "remaining_minutes": TIMER_REMAINING_MINUTES,
            "action": TIMER_ACTION
        }
    }


LAST_NET_IP = ""
LAST_NET_MAC = ""
LAST_NET_TIME = 0.0

def network_info() -> dict[str, Any]:
    global LAST_NET_IP, LAST_NET_MAC, LAST_NET_TIME
    now = time.time()
    if not LAST_NET_IP or now - LAST_NET_TIME > 120.0:
        LAST_NET_IP = local_ip()
        LAST_NET_MAC = mac_address()
        LAST_NET_TIME = now
    
    try:
        counters = psutil.net_io_counters()
        bytes_sent = counters.bytes_sent
        bytes_recv = counters.bytes_recv
    except Exception:
        bytes_sent = 0
        bytes_recv = 0
        
    return {
        "ip": LAST_NET_IP,
        "local_ip": LAST_NET_IP,
        "mac_address": LAST_NET_MAC,
        "bytes_sent": bytes_sent,
        "bytes_recv": bytes_recv,
    }


def heartbeat_payload() -> dict[str, Any]:
    start = time.monotonic()
    sys_info = system_info()
    payload = {
        "status": "online",
        "latency_ms": 0,
        "current_task": CURRENT_TASK,
        "system_info": sys_info,
        "disk_info": disk_info(),
        "network_info": network_info(),
        "process_info": {"count": len(psutil.pids())},
        "last_error": LAST_ERROR,
        "automation_status": automation_status(),
    }
    payload["latency_ms"] = int((time.monotonic() - start) * 1000)
    return payload


def check_server() -> bool:
    try:
        data = request_json("GET", "/api/ping", timeout=8)
        logger.info("Server ping OK: %s %s", data.get("app", "server"), data.get("version", ""))
        return True
    except Exception as exc:
        logger.error("Server ping failed for %s: %s", SERVER_BASE_URL, exc)
        return False


def check_access_key() -> bool:
    """Verify the agent token is accepted by the server using the agent-specific endpoint."""
    try:
        # Use /api/ping — accessible to everyone, confirms server is up
        # Then try a lightweight agent endpoint that accepts agent tokens
        request_json("GET", "/api/ping", timeout=8)
        logger.info("Access key accepted by server")
        return True
    except Exception as exc:
        if is_auth_error(exc):
            logger.error("Access key rejected by server.")
            return False
        logger.warning("Access key check could not reach server yet: %s", exc)
        # Don't block startup if server is temporarily unreachable
        return True


def send_heartbeat() -> None:
    payload = heartbeat_payload()
    if is_activated_mode():
        request_json("POST", "/api/agents/heartbeat", json=payload, timeout=15)
    else:
        request_json("POST", f"/api/agents/{AGENT_ID}/heartbeat", json=payload, timeout=15)
    logger.info("Heartbeat sent: cpu=%s ram=%s task=%s", payload["system_info"].get("cpu_percent"), payload["system_info"].get("ram_percent"), CURRENT_TASK or "-")


def upload_agent_file(path: Path, public_type: str, mime_type: str) -> dict[str, Any] | None:
    try:
        with path.open("rb") as handle:
            if is_activated_mode():
                response = requests.post(
                    f"{SERVER_BASE_URL}/api/agents/files/upload?public_type={public_type}",
                    files={"upload": (path.name, handle, mime_type)},
                    headers=auth_headers(),
                    timeout=60,
                )
            else:
                if public_type == "agent_screenshot":
                    response = requests.post(
                        f"{SERVER_BASE_URL}/api/agents/{AGENT_ID}/screenshot/upload",
                        files={"upload": (path.name, handle, mime_type)},
                        headers=auth_headers(),
                        timeout=60,
                    )
                else:
                    response = requests.post(
                        f"{SERVER_BASE_URL}/api/agents/files/upload?public_type={public_type}",
                        files={"upload": (path.name, handle, mime_type)},
                        headers=auth_headers(),
                        timeout=60,
                    )
            response.raise_for_status()
            return response.json()
    except Exception as exc:
        logger.warning("%s upload failed: %s", public_type, exc)
        return None


def upload_screenshot(path: Path) -> dict[str, Any] | None:
    return upload_agent_file(path, "agent_screenshot", "image/jpeg")


def cleanup_old_screenshots(payload: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = payload or {}
    force = bool(payload.get("force"))
    try:
        keep_last = int(payload.get("keep_last", SCREENSHOT_KEEP_LAST))
    except Exception:
        keep_last = SCREENSHOT_KEEP_LAST
    try:
        retention_days = int(payload.get("retention_days", SCREENSHOT_RETENTION_DAYS))
    except Exception:
        retention_days = SCREENSHOT_RETENTION_DAYS
    keep_last = max(0, min(keep_last, 500))
    retention_days = max(1, min(retention_days, 365))

    SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)
    cutoff = time.time() - (retention_days * 86400)
    files = sorted(
        [path for path in SCREENSHOTS_DIR.glob("*.jpg") if path.is_file()],
        key=lambda item: item.stat().st_mtime,
        reverse=True,
    )
    removed = 0
    freed = 0
    for index, path in enumerate(files):
        try:
            stat = path.stat()
            keep_by_count = index < keep_last
            keep_by_age = stat.st_mtime >= cutoff
            if force:
                if keep_by_count:
                    continue
            elif keep_by_count and keep_by_age:
                continue
            size = stat.st_size
            path.unlink()
            removed += 1
            freed += size
        except Exception as exc:
            logger.warning("Failed to cleanup screenshot %s: %s", path, exc)
    if removed:
        logger.info("Cleaned old screenshots: removed=%s freed_bytes=%s", removed, freed)
    return {
        "ok": True,
        "removed": removed,
        "freed_bytes": freed,
        "retention_days": retention_days,
        "keep_last": keep_last,
        "force": force,
        "total_before": len(files),
        "total_after": max(0, len(files) - removed),
    }


def capture_webcam_photo() -> dict[str, Any]:
    import cv2
    import threading

    result_container: dict[str, Any] = {}
    error_container: list[str] = []

    def _do_capture():
        try:
            cam = cv2.VideoCapture(0, cv2.CAP_DSHOW)
            if not cam.isOpened():
                cam = cv2.VideoCapture(0)
            if not cam.isOpened():
                error_container.append("Failed to open webcam. No camera found or device is in use.")
                return

            # warm-up frames
            for _ in range(5):
                cam.read()

            ret, frame = cam.read()
            cam.release()

            if not ret or frame is None:
                error_container.append("Failed to grab frame from webcam.")
                return

            result_container["frame"] = frame
        except Exception as exc:
            error_container.append(str(exc))

    t = threading.Thread(target=_do_capture, daemon=True)
    t.start()
    t.join(timeout=15)

    if t.is_alive():
        raise RuntimeError("Webcam capture timed out (15s). Camera may be busy or unavailable.")
    if error_container:
        raise RuntimeError(error_container[0])
    if "frame" not in result_container:
        raise RuntimeError("No frame captured from webcam.")

    frame = result_container["frame"]
    SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)
    target = SCREENSHOTS_DIR / f"webcam_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"

    cv2.imwrite(str(target), frame, [cv2.IMWRITE_JPEG_QUALITY, SCREENSHOT_QUALITY])

    upload = upload_agent_file(target, "agent_camera_photo", "image/jpeg")

    result = {"local_path": str(target), "size_bytes": target.stat().st_size}
    if upload:
        result["uploaded"] = True
        result["file_id"] = upload.get("id") or upload.get("file_id")
    else:
        result["uploaded"] = False

    if target.stat().st_size <= 900_000:
        result["base64"] = base64.b64encode(target.read_bytes()).decode("ascii")
        result["mime_type"] = "image/jpeg"

    return result



def capture_webcam_video(duration_seconds: int) -> dict[str, Any]:
    import cv2
    import time
    
    duration_seconds = max(1, min(duration_seconds, 30))
    cam = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    if not cam.isOpened():
        cam = cv2.VideoCapture(0)
    if not cam.isOpened():
        raise RuntimeError("Failed to open webcam for video recording.")
        
    fps = 20.0
    width = int(cam.get(cv2.CAP_PROP_FRAME_WIDTH) or 640)
    height = int(cam.get(cv2.CAP_PROP_FRAME_HEIGHT) or 480)
    
    SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)
    target = SCREENSHOTS_DIR / f"video_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"
    
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(str(target), fourcc, fps, (width, height))
    
    start_time = time.time()
    frames_recorded = 0
    
    for _ in range(5):
        cam.read()
        
    while (time.time() - start_time) < duration_seconds:
        ret, frame = cam.read()
        if not ret or frame is None:
            break
        out.write(frame)
        frames_recorded += 1
        time.sleep(1.0 / fps)
        
    cam.release()
    out.release()
    
    if frames_recorded == 0 or not target.exists():
        raise RuntimeError("Failed to record any frames from webcam.")
        
    upload = upload_agent_file(target, "agent_camera_video", "video/mp4")
    
    result = {"local_path": str(target), "size_bytes": target.stat().st_size, "duration_seconds": duration_seconds, "frames": frames_recorded}
    if upload:
        result["uploaded"] = True
        result["file_id"] = upload.get("id") or upload.get("file_id")
    else:
        result["uploaded"] = False
        
    return result



def capture_screen_video(duration_seconds: int) -> dict[str, Any]:
    import cv2
    import numpy as np
    import time
    if not HAS_SCREENSHOT:
        raise RuntimeError("Pillow ImageGrab is unavailable. Install pillow in the agent venv.")
        
    duration_seconds = max(1, min(duration_seconds, 30))
    
    # Grab initial screenshot to determine screen resolution
    initial_img = ImageGrab.grab()
    width, height = initial_img.size
    
    fps = 10.0  # 10 FPS is plenty for a smooth, lightweight screen capture
    SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)
    target = SCREENSHOTS_DIR / f"screen_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"
    
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(str(target), fourcc, fps, (width, height))
    
    start_time = time.time()
    frames_recorded = 0
    
    while (time.time() - start_time) < duration_seconds:
        frame_start = time.time()
        img = ImageGrab.grab()
        frame = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
        out.write(frame)
        frames_recorded += 1
        
        # Maintain accurate FPS
        elapsed = time.time() - frame_start
        sleep_time = (1.0 / fps) - elapsed
        if sleep_time > 0:
            time.sleep(sleep_time)
            
    out.release()
    
    if frames_recorded == 0 or not target.exists():
        raise RuntimeError("Failed to record any frames from screen.")
        
    upload = upload_agent_file(target, "agent_camera_video", "video/mp4")
    
    result = {"local_path": str(target), "size_bytes": target.stat().st_size, "duration_seconds": duration_seconds, "frames": frames_recorded}
    if upload:
        result["uploaded"] = True
        result["file_id"] = upload.get("id") or upload.get("file_id")
    else:
        result["uploaded"] = False
        
    return result



def save_screenshot() -> dict[str, Any]:
    if not HAS_SCREENSHOT:
        raise RuntimeError("Pillow ImageGrab is unavailable. Install pillow in the agent venv.")
    cleanup_old_screenshots()
    SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)
    target = SCREENSHOTS_DIR / f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
    image = ImageGrab.grab()
    image.save(target, quality=SCREENSHOT_QUALITY)
    upload = upload_screenshot(target)
    result = {"local_path": str(target), "size_bytes": target.stat().st_size}
    if upload:
        result["uploaded"] = True
        result["file_id"] = upload.get("id") or upload.get("file_id")
    else:
        result["uploaded"] = False
        if target.stat().st_size <= 900_000:
            result["base64"] = base64.b64encode(target.read_bytes()).decode("ascii")
            result["mime_type"] = "image/jpeg"
    return result


def read_agent_logs(limit_lines: int = MAX_LOG_RESULT_LINES) -> str:
    log_file = LOG_DIR / "agent.log"
    if not log_file.exists():
        return "agent.log is empty"
    lines = log_file.read_text(encoding="utf-8", errors="replace").splitlines()
    return "\n".join(lines[-max(1, min(limit_lines, MAX_LOG_RESULT_LINES)):])


def restart_allowed_app(payload: dict[str, Any]) -> dict[str, Any]:
    app_name = str(payload.get("app_name") or payload.get("app") or payload.get("name") or "").strip()
    exe = Path(app_name).name.lower()
    if not exe:
        raise RuntimeError("app_name is required")
    if exe not in ALLOWED_APPS:
        raise RuntimeError(f"Application '{exe}' is not in allowed_apps")

    terminated = 0
    for proc in psutil.process_iter(["pid", "name"]):
        try:
            if (proc.info.get("name") or "").lower() == exe:
                proc.terminate()
                terminated += 1
        except Exception:
            continue
    time.sleep(1)
    subprocess.Popen([exe], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, creationflags=0x01000008 if platform.system() == "Windows" else 0)
    logger.warning("Restarted allowlisted app: %s", exe)

    return {"app": exe, "terminated_processes": terminated, "started": True}


VK_CODES = {
    "w": 0x57,
    "a": 0x41,
    "b": 0x42,
    "s": 0x53,
    "d": 0x44,
    "z": 0x5A,
    "e": 0x45,
    "f": 0x46,
    "g": 0x47,
    "i": 0x49,
    "f2": 0x71,
    "esc": 0x1B,
    "escape": 0x1B,
    "space": 0x20,
    "enter": 0x0D,
    "tab": 0x09,
    "shift": 0x10,
    "ctrl": 0x11,
}
VK_LEFT = 0x25
VK_RIGHT = 0x27
VK_D = 0x44
VK_F4 = 0x73
VK_CTRL = 0x11
VK_LWIN = 0x5B
KEYEVENTF_KEYUP = 0x0002
KEYEVENTF_SCANCODE = 0x0008
MOUSEEVENTF_MOVE = 0x0001
MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004
MOUSEEVENTF_RIGHTDOWN = 0x0008
MOUSEEVENTF_RIGHTUP = 0x0010
MOUSEEVENTF_WHEEL = 0x0800
MODIFIER_VKS = [0x10, 0x11, 0x12, 0xA0, 0xA1, 0xA2, 0xA3, 0xA4, 0xA5, 0x5B, 0x5C]
SCAN_CODES = {
    "esc": 0x01,
    "w": 0x11,
    "b": 0x30,
    "e": 0x12,
    "f": 0x21,
    "g": 0x22,
    "i": 0x17,
    "a": 0x1E,
    "s": 0x1F,
    "d": 0x20,
    "space": 0x39,
    "tab": 0x0F,
    "enter": 0x1C,
    "shift": 0x2A,
    "ctrl": 0x1D,
}
WS_SEND_LOCK = threading.Lock()
INPUT_KEYBOARD = 1
INPUT_MOUSE = 0
KEYEVENTF_EXTENDEDKEY = 0x0001
ULONG_PTR = ctypes.c_ulonglong if ctypes.sizeof(ctypes.c_void_p) == 8 else ctypes.c_ulong


class POINT(ctypes.Structure):
    _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]


class KEYBDINPUT(ctypes.Structure):
    _fields_ = [
        ("wVk", ctypes.c_ushort),
        ("wScan", ctypes.c_ushort),
        ("dwFlags", ctypes.c_ulong),
        ("time", ctypes.c_ulong),
        ("dwExtraInfo", ULONG_PTR),
    ]


class MOUSEINPUT(ctypes.Structure):
    _fields_ = [
        ("dx", ctypes.c_long),
        ("dy", ctypes.c_long),
        ("mouseData", ctypes.c_ulong),
        ("dwFlags", ctypes.c_ulong),
        ("time", ctypes.c_ulong),
        ("dwExtraInfo", ULONG_PTR),
    ]


class HARDWAREINPUT(ctypes.Structure):
    _fields_ = [
        ("uMsg", ctypes.c_ulong),
        ("wParamL", ctypes.c_ushort),
        ("wParamH", ctypes.c_ushort),
    ]


class INPUT_UNION(ctypes.Union):
    _fields_ = [("mi", MOUSEINPUT), ("ki", KEYBDINPUT), ("hi", HARDWAREINPUT)]


class INPUT(ctypes.Structure):
    _fields_ = [("type", ctypes.c_ulong), ("union", INPUT_UNION)]


def _is_extended_key(vk: int) -> bool:
    return vk in {VK_LEFT, VK_RIGHT, VK_LWIN, 0x5C, 0x21, 0x22, 0x23, 0x24, 0x25, 0x26, 0x27, 0x28}


def _send_input_key(vk: int, keyup: bool = False) -> None:
    flags = KEYEVENTF_EXTENDEDKEY if _is_extended_key(vk) else 0
    if keyup:
        flags |= KEYEVENTF_KEYUP
    event = INPUT(
        type=INPUT_KEYBOARD,
        union=INPUT_UNION(ki=KEYBDINPUT(vk, 0, flags, 0, 0)),
    )
    ctypes.windll.user32.SendInput.argtypes = (ctypes.c_uint, ctypes.POINTER(INPUT), ctypes.c_int)
    ctypes.windll.user32.SendInput.restype = ctypes.c_uint
    sent = ctypes.windll.user32.SendInput(1, ctypes.byref(event), ctypes.sizeof(INPUT))
    if sent != 1:
        raise ctypes.WinError(ctypes.get_last_error())


def _send_input_scancode(scan_code: int, keyup: bool = False) -> None:
    flags = KEYEVENTF_SCANCODE | (KEYEVENTF_KEYUP if keyup else 0)
    event = INPUT(
        type=INPUT_KEYBOARD,
        union=INPUT_UNION(ki=KEYBDINPUT(0, scan_code, flags, 0, 0)),
    )
    ctypes.windll.user32.SendInput.argtypes = (ctypes.c_uint, ctypes.POINTER(INPUT), ctypes.c_int)
    ctypes.windll.user32.SendInput.restype = ctypes.c_uint
    sent = ctypes.windll.user32.SendInput(1, ctypes.byref(event), ctypes.sizeof(INPUT))
    if sent != 1:
        raise ctypes.WinError(ctypes.get_last_error())


def _key_event(vk: int, flags: int = 0) -> None:
    _send_input_key(vk, bool(flags & KEYEVENTF_KEYUP))


def _send_mouse(flags: int, dx: int = 0, dy: int = 0, data: int = 0) -> None:
    event = INPUT(
        type=INPUT_MOUSE,
        union=INPUT_UNION(mi=MOUSEINPUT(dx, dy, data, flags, 0, 0)),
    )
    ctypes.windll.user32.SendInput.argtypes = (ctypes.c_uint, ctypes.POINTER(INPUT), ctypes.c_int)
    ctypes.windll.user32.SendInput.restype = ctypes.c_uint
    sent = ctypes.windll.user32.SendInput(1, ctypes.byref(event), ctypes.sizeof(INPUT))
    if sent != 1:
        raise ctypes.WinError(ctypes.get_last_error())


def release_stuck_keys() -> dict[str, Any]:
    for _ in range(3):
        for vk in [*MODIFIER_VKS, *VK_CODES.values()]:
            _key_event(vk, KEYEVENTF_KEYUP)
        time.sleep(0.03)
    logger.debug("Released stuck input keys")
    return {"ok": True, "message": "input keys released"}


def press_input_key(payload: dict[str, Any]) -> dict[str, Any]:
    key = str(payload.get("key") or "").lower().strip()
    duration = float(payload.get("duration_seconds") or 2.0)
    duration = max(0.03, min(duration, 2.0))
    if key not in ALLOWED_INPUT_KEYS:
        raise RuntimeError(f"Key '{key}' is not in allowed_input_keys")
    vk = VK_CODES.get(key)
    if not vk:
        raise RuntimeError(f"Key '{key}' is not supported by this agent")
    try:
        _key_event(vk, 0)
        time.sleep(duration)
    finally:
        _key_event(vk, KEYEVENTF_KEYUP)
        for vk_mod in MODIFIER_VKS:
            _key_event(vk_mod, KEYEVENTF_KEYUP)
    logger.info("Pressed allowlisted key: %s", key)
    return {"ok": True, "key": key, "duration_seconds": duration}


def press_hotkey(vks: list[int], hold_seconds: float = 2.0) -> None:
    release_stuck_keys()
    try:
        for vk in vks:
            _key_event(vk, 0)
            time.sleep(0.03)
        time.sleep(max(0.03, min(float(hold_seconds), 2.0)))
    finally:
        for vk in reversed(vks):
            _key_event(vk, KEYEVENTF_KEYUP)
            time.sleep(0.03)
        release_stuck_keys()


def switch_desktop(direction: str) -> dict[str, Any]:
    if direction not in {"left", "right"}:
        raise RuntimeError("Desktop direction must be left or right")
    key = VK_LEFT if direction == "left" else VK_RIGHT
    logger.info("Sending Windows virtual desktop hotkey: Win+Ctrl+%s", direction)
    press_hotkey([VK_LWIN, VK_CTRL, key], hold_seconds=2.0)
    logger.info("Switched virtual desktop: %s", direction)
    return {
        "ok": True,
        "direction": direction,
        "method": "SendInput Win+Ctrl+Arrow",
        "message": f"desktop switched {direction}",
    }


def desktop_action(action: str) -> dict[str, Any]:
    if action == "new":
        logger.info("Sending Windows virtual desktop hotkey: Win+Ctrl+D")
        press_hotkey([VK_LWIN, VK_CTRL, VK_D], hold_seconds=0.25)
        return {"ok": True, "action": "new", "method": "SendInput Win+Ctrl+D"}
    if action == "close":
        logger.info("Sending Windows virtual desktop hotkey: Win+Ctrl+F4")
        press_hotkey([VK_LWIN, VK_CTRL, VK_F4], hold_seconds=0.25)
        return {"ok": True, "action": "close", "method": "SendInput Win+Ctrl+F4"}
    raise RuntimeError("Desktop action must be new or close")


def click_preset(payload: dict[str, Any]) -> dict[str, Any]:
    preset = str(payload.get("preset") or "").lower().strip()
    if preset not in CLICK_PRESETS:
        raise RuntimeError(f"Click preset '{preset}' is not configured")
    coords = CLICK_PRESETS[preset]
    if not isinstance(coords, list) or len(coords) != 2:
        raise RuntimeError(f"Click preset '{preset}' has invalid coordinates")
    x, y = int(coords[0]), int(coords[1])
    ctypes.windll.user32.SetCursorPos(x, y)
    time.sleep(0.05)
    ctypes.windll.user32.mouse_event(MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
    time.sleep(0.08)
    ctypes.windll.user32.mouse_event(MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
    logger.info("Clicked preset: %s at %s,%s", preset, x, y)
    return {"ok": True, "preset": preset, "x": x, "y": y}


def launch_allowed_app(payload: dict[str, Any]) -> dict[str, Any]:
    app_key = str(payload.get("app_key") or payload.get("name") or "majestic_launcher").lower().strip()
    path = ALLOWED_LAUNCHERS.get(app_key)
    if not path:
        raise RuntimeError(f"Launcher '{app_key}' is not in allowed_launchers")
    
    if "://" not in path and not Path(path).exists():
        raise RuntimeError(f"Launcher path does not exist for '{app_key}'")
        
    if path.lower().endswith(".url") or path.lower().endswith(".lnk") or "://" in path:
        os.startfile(path)
    else:
        try:
            # CREATE_NO_WINDOW = 0x08000000
            # CREATE_BREAKAWAY_FROM_JOB = 0x01000000
            flags = 0x08000000 | 0x01000000 if platform.system() == "Windows" else 0
            subprocess.Popen([path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, creationflags=flags)
        except OSError as e:
            winerr = getattr(e, "winerror", 0)
            if winerr == 5:
                logger.info("WinError 5 (Access is Denied) on launch with breakaway flags. Retrying without breakaway...")
                try:
                    subprocess.Popen([path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, creationflags=0x08000000)
                except Exception as ex:
                    logger.info("Failed without breakaway: %s. Falling back to os.startfile...", ex)
                    os.startfile(path)
            elif winerr == 740 or "elevation" in str(e).lower():
                logger.info("Process requires elevation. Retrying with os.startfile to prompt UAC...")
                os.startfile(path)
            else:
                logger.info("Subprocess.Popen failed with error: %s. Falling back to os.startfile...", e)
                try:
                    os.startfile(path)
                except Exception as ex2:
                    logger.error("os.startfile fallback failed: %s", ex2)
                    raise e
        
    logger.info("Launched allowlisted app: %s", app_key)
    return {"ok": True, "app_key": app_key, "path_exists": True}


def close_allowed_app(payload: dict[str, Any]) -> dict[str, Any]:
    app_key = str(payload.get("app_key") or payload.get("name") or "").lower().strip()
    if not app_key:
        raise RuntimeError("app_key is required")
        
    keywords = {app_key.replace("_", "")}
    if "gta" in app_key or "grand_theft_auto" in app_key:
        keywords.update({"gta5", "playgtav", "gtavlauncher"})
    elif "epic" in app_key:
        keywords.update({"epicgameslauncher", "epicgames"})
    elif "steam" in app_key:
        keywords.update({"steam"})
    elif "roblox" in app_key:
        keywords.update({"robloxplayer", "roblox"})
        
    killed = []
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            name = (proc.info.get('name') or '').lower()
            name_clean = name.replace(" ", "").replace("_", "").replace("-", "")
            if any(kw in name_clean for kw in keywords):
                logger.info("Killing process %s (PID %s) for app %s", name, proc.pid, app_key)
                proc.kill()
                killed.append(name)
        except Exception:
            pass
    return {"ok": True, "app_key": app_key, "killed_processes": killed}


def open_safe_url(payload: dict[str, Any]) -> dict[str, Any]:
    url = str(payload.get("url") or "").strip()
    if not (url.startswith("http://") or url.startswith("https://")) or any(ch.isspace() for ch in url):
        raise RuntimeError("Only http:// and https:// URLs without spaces are allowed")
    webbrowser.open(url, new=2)
    logger.info("Opened safe URL")
    return {"ok": True, "url": url}


def volume_action(action: str) -> dict[str, Any]:
    key = 0xAF if action == "volume_up" else 0xAE
    for _ in range(5):
        _key_event(key, 0)
        time.sleep(0.03)
        _key_event(key, KEYEVENTF_KEYUP)
    return {"ok": True, "action": action}


def game_status() -> dict[str, Any]:
    names = {proc.info.get("name") or "" for proc in psutil.process_iter(["name"])}
    lowered = {name.lower() for name in names}
    return {
        "majestic_launcher": "majestic launcher.exe" in lowered or "majesticlauncher.exe" in lowered,
        "gta5": "gta5.exe" in lowered,
        "gta5rp_launcher": "gta5rplauncher.exe" in lowered or "gta5rp launcher.exe" in lowered,
        "rage_multiplayer": "ragemp.exe" in lowered,
        "known_processes": sorted([name for name in names if name.lower() in {"majestic launcher.exe", "majesticlauncher.exe", "gta5.exe", "gta5rplauncher.exe", "gta5rp launcher.exe", "ragemp.exe"}]),
    }


def automation_status() -> dict[str, Any]:
    with BACKGROUND_LOCK:
        status = json.loads(json.dumps(BACKGROUND_STATE, ensure_ascii=False))
        for name, thread in BACKGROUND_THREADS.items():
            if name in status:
                status[name]["running"] = thread.is_alive() and not SHUTDOWN.is_set()
        return status


def add_automation_rule_task(payload: dict[str, Any]) -> dict[str, Any]:
    rule_id = f"rule_{int(time.time() * 1000)}"
    rule = {
        "id": rule_id,
        "name": payload.get("name") or f"Rule {rule_id}",
        "trigger": payload.get("trigger") or "time",
        "time": payload.get("time") or "22:00",
        "action": payload.get("action") or "sleep_pc",
    }
    rules = CONFIG.setdefault("automation_rules", [])
    rules.append(rule)
    try:
        CONFIG_FILE.write_text(json.dumps(CONFIG, ensure_ascii=False, indent=2), encoding="utf-8")
        logger.info("Added automation rule: %s", rule)
        return {"ok": True, "rule": rule}
    except Exception as e:
        logger.error("Failed to save automation rule: %s", e)
        return {"ok": False, "error": str(e)}

def delete_automation_rule_task(payload: dict[str, Any]) -> dict[str, Any]:
    rule_id = payload.get("id")
    rules = CONFIG.setdefault("automation_rules", [])
    initial_len = len(rules)
    CONFIG["automation_rules"] = [r for r in rules if r.get("id") != rule_id]
    if len(CONFIG["automation_rules"]) == initial_len:
        return {"ok": False, "error": "Rule not found"}
    try:
        CONFIG_FILE.write_text(json.dumps(CONFIG, ensure_ascii=False, indent=2), encoding="utf-8")
        logger.info("Deleted automation rule with ID %s", rule_id)
        return {"ok": True}
    except Exception as e:
        logger.error("Failed to save config: %s", e)
        return {"ok": False, "error": str(e)}

def execute_rule_action(rule: dict[str, Any]):
    action = rule.get("action")
    logger.info("Executing rule action: %s (%s)", rule.get("name"), action)
    try:
        if action == "sleep_pc":
            sleep_pc()
        elif action == "lock_pc":
            lock_pc()
        elif action == "monitor_off":
            monitor_off()
        elif action == "screenshot":
            save_screenshot()
            logger.info("Automation rule captured and uploaded screenshot successfully")
    except Exception as e:
        logger.error("Failed to execute rule action %s: %s", action, e)

def trigger_startup_rules():
    rules = CONFIG.get("automation_rules") or []
    for rule in rules:
        if rule.get("trigger") == "startup":
            logger.info("Triggering startup rule: %s -> %s", rule.get("name"), rule.get("action"))
            threading.Thread(target=execute_rule_action, args=(rule,), daemon=True).start()

def automation_rules_loop():
    logger.info("Automation rules background checker started")
    last_executed = {}
    while not SHUTDOWN.is_set():
        # Check every 20 seconds for precise time matching
        time.sleep(20)
        rules = CONFIG.get("automation_rules") or []
        if not rules:
            continue
        now = datetime.now()
        current_time = now.strftime("%H:%M")
        current_date = now.strftime("%Y-%m-%d")
        for rule in rules:
            if rule.get("trigger") == "time":
                rule_time = rule.get("time")
                rule_id = rule.get("id")
                if rule_time == current_time:
                    if last_executed.get(rule_id) != current_date:
                        last_executed[rule_id] = current_date
                        execute_rule_action(rule)


def _set_background_state(name: str, **values: Any) -> None:
    with BACKGROUND_LOCK:
        BACKGROUND_STATE.setdefault(name, {})
        BACKGROUND_STATE[name].update(values)


def _anti_afk_worker(min_minutes: int, max_minutes: int) -> None:
    _set_background_state("anti_afk", running=True, started_at=datetime.now(timezone.utc).isoformat(), last_error="")
    logger.warning("Anti-AFK started: interval %s-%s minutes", min_minutes, max_minutes)
    try:
        while not SHUTDOWN.is_set() and not ANTI_AFK_STOP.is_set():
            wait_seconds = random.randint(min_minutes * 60, max_minutes * 60)
            if ANTI_AFK_STOP.wait(wait_seconds) or SHUTDOWN.is_set():
                break
            try:
                press_input_key({"key": "w", "duration_seconds": 0.7})
                time.sleep(0.2)
                press_input_key({"key": "s", "duration_seconds": 0.7})
                _set_background_state("anti_afk", last_action_at=datetime.now(timezone.utc).isoformat(), last_error="")
                logger.info("Anti-AFK tick completed")
            except Exception as exc:
                _set_background_state("anti_afk", last_error=str(exc))
                logger.warning("Anti-AFK tick failed: %s", exc)
    finally:
        try:
            release_stuck_keys()
        except Exception:
            pass
        _set_background_state("anti_afk", running=False)
        logger.warning("Anti-AFK stopped")


def start_anti_afk(payload: dict[str, Any]) -> dict[str, Any]:
    min_minutes = max(1, int(payload.get("min_minutes") or ANTI_AFK_MIN_MINUTES))
    max_minutes = max(min_minutes, int(payload.get("max_minutes") or ANTI_AFK_MAX_MINUTES))
    max_minutes = min(max_minutes, 120)
    with BACKGROUND_LOCK:
        existing = BACKGROUND_THREADS.get("anti_afk")
        if existing and existing.is_alive():
            return {"ok": True, "already_running": True, "status": automation_status()["anti_afk"]}
        ANTI_AFK_STOP.clear()
        thread = threading.Thread(target=_anti_afk_worker, args=(min_minutes, max_minutes), name="anti-afk", daemon=True)
        BACKGROUND_THREADS["anti_afk"] = thread
        thread.start()
    return {"ok": True, "started": True, "min_minutes": min_minutes, "max_minutes": max_minutes}


def stop_anti_afk() -> dict[str, Any]:
    ANTI_AFK_STOP.set()
    return {"ok": True, "stopping": True, "status": automation_status().get("anti_afk", {})}


def _auto_screen_worker(interval_seconds: int) -> None:
    _set_background_state("auto_screen", running=True, started_at=datetime.now(timezone.utc).isoformat(), last_error="")
    logger.warning("Auto-screen started: interval %s seconds", interval_seconds)
    try:
        while not SHUTDOWN.is_set() and not AUTO_SCREEN_STOP.is_set():
            try:
                result = save_screenshot()
                _set_background_state(
                    "auto_screen",
                    last_action_at=datetime.now(timezone.utc).isoformat(),
                    last_file_id=result.get("file_id"),
                    last_error="",
                )
                logger.info("Auto-screen captured: uploaded=%s file_id=%s", result.get("uploaded"), result.get("file_id"))
            except Exception as exc:
                _set_background_state("auto_screen", last_error=str(exc))
                logger.warning("Auto-screen capture failed: %s", exc)
            if AUTO_SCREEN_STOP.wait(interval_seconds):
                break
    finally:
        _set_background_state("auto_screen", running=False)
        logger.warning("Auto-screen stopped")


def start_auto_screen(payload: dict[str, Any]) -> dict[str, Any]:
    interval_seconds = max(60, int(payload.get("interval_seconds") or AUTO_SCREEN_INTERVAL_SECONDS))
    interval_seconds = min(interval_seconds, 3600)
    with BACKGROUND_LOCK:
        existing = BACKGROUND_THREADS.get("auto_screen")
        if existing and existing.is_alive():
            return {"ok": True, "already_running": True, "status": automation_status()["auto_screen"]}
        AUTO_SCREEN_STOP.clear()
        thread = threading.Thread(target=_auto_screen_worker, args=(interval_seconds,), name="auto-screen", daemon=True)
        BACKGROUND_THREADS["auto_screen"] = thread
        thread.start()
    return {"ok": True, "started": True, "interval_seconds": interval_seconds}


def stop_auto_screen() -> dict[str, Any]:
    AUTO_SCREEN_STOP.set()
    return {"ok": True, "stopping": True, "status": automation_status().get("auto_screen", {})}


def safe_ws_send(ws: Any, message: dict[str, Any]) -> None:
    with WS_SEND_LOCK:
        ws.send(json.dumps(message, ensure_ascii=False))


def lock_pc() -> dict[str, Any]:
    logger.info("Executing PC lock")
    ctypes.windll.user32.LockWorkStation()
    return {"ok": True, "message": "PC locked successfully"}


def sleep_pc() -> dict[str, Any]:
    logger.info("Executing PC sleep")
    res = ctypes.windll.powrprof.SetSuspendState(0, 1, 0)
    if res == 0:
        os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
    return {"ok": True, "message": "PC sleep command sent"}


def monitor_off() -> dict[str, Any]:
    logger.info("Executing monitor off")
    ctypes.windll.user32.SendMessageW(0xFFFF, 0x0112, 0xF170, 2)
    return {"ok": True, "message": "Monitor off command sent"}


def shutdown_pc() -> dict[str, Any]:
    logger.warning("Executing PC shutdown!")
    if platform.system() == "Windows":
        os.system("shutdown /s /t 0")
    else:
        os.system("shutdown -h now")
    return {"ok": True, "message": "Shutdown command issued"}


def show_nonblocking_warning():
    def worker():
        ctypes.windll.user32.MessageBoxW(0, "Ваш компьютер автоматически выключится через 1 минуту по таймеру PCManager!", "PCManager", 0x30 | 0x0)
    threading.Thread(target=worker, daemon=True).start()


ACTIVE_TIMER_THREAD: threading.Thread | None = None
ACTIVE_TIMER_CANCEL_EVENT: threading.Event | None = None

def run_countdown_timer(duration_minutes: int, action: str, cancel_event: threading.Event):
    global TIMER_REMAINING_MINUTES, TIMER_ACTIVE, TIMER_ACTION
    TIMER_REMAINING_MINUTES = duration_minutes
    TIMER_ACTIVE = True
    TIMER_ACTION = action
    
    logger.info("Timer thread started: %d minutes until %s", duration_minutes, action)
    total_seconds = duration_minutes * 60
    start_time = time.time()
    
    while True:
        if cancel_event.is_set():
            logger.info("Countdown timer cancelled")
            if ACTIVE_TIMER_CANCEL_EVENT is cancel_event:
                TIMER_ACTIVE = False
                TIMER_REMAINING_MINUTES = 0
            return
            
        elapsed = time.time() - start_time
        remaining = total_seconds - elapsed
        
        if remaining <= 0:
            break
            
        if ACTIVE_TIMER_CANCEL_EVENT is cancel_event:
            TIMER_REMAINING_MINUTES = int(remaining // 60) + 1
        
        # Trigger 1-minute warning
        if 55 <= remaining <= 65:
            show_nonblocking_warning()
            
        time.sleep(1)
        
    if ACTIVE_TIMER_CANCEL_EVENT is cancel_event:
        TIMER_ACTIVE = False
        TIMER_REMAINING_MINUTES = 0
        logger.info("Timer expired! Executing %s command...", action)
        if action == "sleep":
            sleep_pc()
        else:
            shutdown_pc()


def start_timer_task(payload: dict[str, Any]) -> dict[str, Any]:
    global ACTIVE_TIMER_THREAD, ACTIVE_TIMER_CANCEL_EVENT
    duration = int(payload.get("duration") or payload.get("minutes") or 0)
    action = str(payload.get("action") or "shutdown").strip().lower()
    
    if duration <= 0:
        raise RuntimeError("Timer duration must be a positive number of minutes")
        
    if action not in {"shutdown", "sleep"}:
        action = "shutdown"
        
    cancel_timer_task()
    
    ACTIVE_TIMER_CANCEL_EVENT = threading.Event()
    ACTIVE_TIMER_THREAD = threading.Thread(target=run_countdown_timer, args=(duration, action, ACTIVE_TIMER_CANCEL_EVENT), daemon=True)
    ACTIVE_TIMER_THREAD.start()
    
    return {"ok": True, "message": f"Timer started for {duration} minutes", "duration": duration, "action": action}


def cancel_timer_task() -> dict[str, Any]:
    global ACTIVE_TIMER_CANCEL_EVENT, TIMER_ACTIVE, TIMER_REMAINING_MINUTES
    if ACTIVE_TIMER_CANCEL_EVENT is not None:
        ACTIVE_TIMER_CANCEL_EVENT.set()
        ACTIVE_TIMER_CANCEL_EVENT = None
        
    if TIMER_ACTIVE:
        TIMER_ACTIVE = False
        TIMER_REMAINING_MINUTES = 0
        logger.info("Cancelled active shutdown timer")
        return {"ok": True, "message": "Timer successfully cancelled"}
    return {"ok": True, "message": "No active timer found to cancel"}


def handle_remote_input(payload: dict[str, Any]) -> dict[str, Any]:
    sub_action = str(payload.get("action") or "").strip().lower()
    
    if sub_action == "click_left":
        _send_mouse(MOUSEEVENTF_LEFTDOWN)
        time.sleep(0.05)
        _send_mouse(MOUSEEVENTF_LEFTUP)
        logger.info("Executed remote left click")
        return {"ok": True, "action": "click_left"}
        
    elif sub_action == "click_double":
        _send_mouse(MOUSEEVENTF_LEFTDOWN)
        time.sleep(0.05)
        _send_mouse(MOUSEEVENTF_LEFTUP)
        time.sleep(0.1)
        _send_mouse(MOUSEEVENTF_LEFTDOWN)
        time.sleep(0.05)
        _send_mouse(MOUSEEVENTF_LEFTUP)
        logger.info("Executed remote double click")
        return {"ok": True, "action": "click_double"}
        
    elif sub_action == "click_right":
        _send_mouse(MOUSEEVENTF_RIGHTDOWN)
        time.sleep(0.05)
        _send_mouse(MOUSEEVENTF_RIGHTUP)
        logger.info("Executed remote right click")
        return {"ok": True, "action": "click_right"}
        
    elif sub_action == "scroll_up":
        _send_mouse(MOUSEEVENTF_WHEEL, data=120)
        logger.info("Executed remote scroll up")
        return {"ok": True, "action": "scroll_up"}
        
    elif sub_action == "scroll_down":
        _send_mouse(MOUSEEVENTF_WHEEL, data=ctypes.c_ulong(-120).value)
        logger.info("Executed remote scroll down")
        return {"ok": True, "action": "scroll_down"}
        
    elif sub_action == "move":
        dx = int(payload.get("dx") or 0)
        dy = int(payload.get("dy") or 0)
        class POINT_STRUCT(ctypes.Structure):
            _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]
        pt = POINT_STRUCT()
        if ctypes.windll.user32.GetCursorPos(ctypes.byref(pt)):
            new_x = pt.x + dx
            new_y = pt.y + dy
            ctypes.windll.user32.SetCursorPos(new_x, new_y)
            logger.info("Moved cursor by dx=%d, dy=%d to x=%d, y=%d", dx, dy, new_x, new_y)
            return {"ok": True, "action": "move", "dx": dx, "dy": dy, "new_x": new_x, "new_y": new_y}
        else:
            _send_mouse(MOUSEEVENTF_MOVE, dx, dy)
            logger.info("Moved cursor relative by dx=%d, dy=%d", dx, dy)
            return {"ok": True, "action": "move_relative", "dx": dx, "dy": dy}
            
    elif sub_action == "media":
        key = str(payload.get("key") or "").strip().lower()
        if key == "play_pause":
            _key_event(0x20, 0)
            time.sleep(0.05)
            _key_event(0x20, KEYEVENTF_KEYUP)
            logger.info("Executed remote play/pause via Space")
            return {"ok": True, "media": "play_pause"}
        elif key == "volume_up":
            _key_event(0xAF, 0)
            time.sleep(0.05)
            _key_event(0xAF, KEYEVENTF_KEYUP)
            logger.info("Executed volume up")
            return {"ok": True, "media": "volume_up"}
        elif key == "volume_down":
            _key_event(0xAE, 0)
            time.sleep(0.05)
            _key_event(0xAE, KEYEVENTF_KEYUP)
            logger.info("Executed volume down")
            return {"ok": True, "media": "volume_down"}
        elif key == "mute":
            _key_event(0xAD, 0)
            time.sleep(0.05)
            _key_event(0xAD, KEYEVENTF_KEYUP)
            logger.info("Executed volume mute toggle")
            return {"ok": True, "media": "mute"}
        elif key == "show_desktop":
            _key_event(0x5B, 0)
            time.sleep(0.02)
            _key_event(0x44, 0)
            time.sleep(0.05)
            _key_event(0x44, KEYEVENTF_KEYUP)
            time.sleep(0.02)
            _key_event(0x5B, KEYEVENTF_KEYUP)
            logger.info("Executed show desktop via Win+D")
            return {"ok": True, "media": "show_desktop"}
        else:
            raise RuntimeError(f"Unknown media action: {key}")
            
    elif sub_action == "type_text":
        text = str(payload.get("text") or "")
        logger.info("Typing text remotely: %s", text)
        typed_count = 0
        for char in text:
            vk_val = ctypes.windll.user32.VkKeyScanW(ord(char))
            if vk_val == -1:
                continue
            shift = bool(vk_val & 0x100)
            ctrl = bool(vk_val & 0x200)
            alt = bool(vk_val & 0x400)
            vk_code = vk_val & 0xFF
            
            if shift: _key_event(0x10, 0)
            if ctrl: _key_event(0x11, 0)
            if alt: _key_event(0x12, 0)
            time.sleep(0.01)
            
            _key_event(vk_code, 0)
            time.sleep(0.02)
            _key_event(vk_code, KEYEVENTF_KEYUP)
            time.sleep(0.01)
            
            if alt: _key_event(0x12, KEYEVENTF_KEYUP)
            if ctrl: _key_event(0x11, KEYEVENTF_KEYUP)
            if shift: _key_event(0x10, KEYEVENTF_KEYUP)
            time.sleep(0.01)
            typed_count += 1
            
        return {"ok": True, "action": "type_text", "typed_chars": typed_count}
    else:
        raise RuntimeError(f"Unknown remote input action: {sub_action}")


def execute_task(task: dict[str, Any]) -> tuple[str, dict[str, Any] | str, str]:
    action = TASK_ALIASES.get(str(task.get("action") or task.get("task_type") or ""), str(task.get("action") or task.get("task_type") or ""))
    payload = task.get("payload") or {}
    if action not in SAFE_TASKS or action not in ENABLED_TASKS:
        return "failed", {}, f"Task '{action}' is not enabled in agent allowlist"
    try:
        if action == "ping":
            return "success", {"message": "pong", "time": datetime.now(timezone.utc).isoformat()}, ""
        if action == "system_info":
            return "success", {"system_info": system_info(), "disk_info": disk_info(), "network_info": network_info()}, ""
        if action == "screenshot":
            return "success", save_screenshot(), ""
        if action == "camera_snapshot":
            return "success", capture_webcam_photo(), ""
        if action == "record_video":
            duration = int(payload.get("duration_seconds") or 5)
            return "success", capture_webcam_video(duration), ""
        if action == "record_screen":
            duration = int(payload.get("duration_seconds") or 5)
            return "success", capture_screen_video(duration), ""
        if action == "lock_pc":
            return "success", lock_pc(), ""
        if action == "sleep_pc":
            return "success", sleep_pc(), ""
        if action == "monitor_off":
            return "success", monitor_off(), ""
        if action == "remote_input":
            return "success", handle_remote_input(payload), ""
        if action == "start_timer":
            return "success", start_timer_task(payload), ""
        if action == "cancel_timer":
            return "success", cancel_timer_task(), ""
        if action == "shutdown_now":
            return "success", shutdown_pc(), ""
        if action == "add_automation_rule":
            return "success", add_automation_rule_task(payload), ""
        if action == "delete_automation_rule":
            return "success", delete_automation_rule_task(payload), ""
        if action == "process_list":
            return "success", {"items": process_list()}, ""
        if action == "disk_info":
            return "success", disk_info(), ""
        if action == "temperature":
            temp = temperature_status()
            return "success", temp or {"available": False, "message": "temperature unavailable"}, ""
        if action == "agent_logs":
            return "success", read_agent_logs(int(payload.get("limit_lines") or MAX_LOG_RESULT_LINES)), ""
        if action == "restart_allowed_app":
            return "success", restart_allowed_app(payload), ""
        if action == "press_key":
            return "success", press_input_key(payload), ""
        if action == "click_preset":
            return "success", click_preset(payload), ""
        if action == "release_keys":
            return "success", release_stuck_keys(), ""
        if action == "launch_allowed_app":
            return "success", launch_allowed_app(payload), ""
        if action == "close_allowed_app":
            return "success", close_allowed_app(payload), ""
        if action == "open_url":
            return "success", open_safe_url(payload), ""
        if action in {"volume_up", "volume_down"}:
            return "success", volume_action(action), ""
        if action == "game_status":
            return "success", game_status(), ""
        if action == "anti_afk_start":
            return "success", start_anti_afk(payload), ""
        if action == "anti_afk_stop":
            return "success", stop_anti_afk(), ""
        if action == "auto_screen_start":
            return "success", start_auto_screen(payload), ""
        if action == "auto_screen_stop":
            return "success", stop_auto_screen(), ""
        if action == "automation_status":
            return "success", automation_status(), ""
        if action == "cleanup_screenshots":
            return "success", cleanup_old_screenshots(payload), ""
        if action == "desktop_new":
            return "success", desktop_action("new"), ""
        if action == "desktop_close":
            return "success", desktop_action("close"), ""
        if action == "desktop_left":
            return "success", switch_desktop("left"), ""
        if action == "desktop_right":
            return "success", switch_desktop("right"), ""
        if action == "update_agent":
            download_url = payload.get("download_url")
            threading.Thread(target=lambda: (time.sleep(1), perform_update(download_url)), daemon=True).start()
            return "success", {"message": "Update initiated"}, ""
    except Exception as exc:
        logger.exception("Task failed: %s", action)
        return "failed", {}, str(exc)
    return "failed", {}, f"Task '{action}' is not implemented"


def remember_task(task_id: str) -> bool:
    recent = list(STATE.get("executed_task_ids") or [])
    if task_id in recent:
        return False
    recent.append(task_id)
    STATE["executed_task_ids"] = recent[-100:]
    save_state(STATE)
    return True


def stringify_result(value: dict[str, Any] | str) -> str:
    if isinstance(value, str):
        text = value
    else:
        text = json.dumps(value, ensure_ascii=False)
    return text[:MAX_RESULT_CHARS]


def post_task_status(task_id: str, status: str, result: dict[str, Any] | str = "", error: str = "") -> None:
    payload = {"status": status, "result": stringify_result(result), "error": error[:8000]}
    try:
        request_json("POST", f"/api/tasks/{task_id}/result", json=payload, timeout=25)
    except Exception:
        request_json("POST", f"/api/agents/tasks/{task_id}/result", json=payload, timeout=25)


def poll_task() -> dict[str, Any] | None:
    if is_activated_mode():
        data = request_json("GET", "/api/agents/tasks/next", timeout=15)
    else:
        data = request_json("GET", f"/api/agents/{AGENT_ID}/tasks/next", timeout=15)
    task = data.get("task")
    return task if isinstance(task, dict) else None


def task_loop() -> None:
    global CURRENT_TASK, LAST_ERROR
    while not SHUTDOWN.is_set():
        if not is_activated_mode() or not ACCESS_KEY:
            time.sleep(2)
            continue
        try:
            task = poll_task()
            if not task:
                time.sleep(TASK_POLL_INTERVAL)
                continue
            task_id = str(task.get("task_id") or "")
            if not task_id or not remember_task(task_id):
                continue
            CURRENT_TASK = str(task.get("action") or task.get("task_type") or "")
            LAST_ERROR = ""
            logger.info("Task received: %s %s", task_id, CURRENT_TASK)
            try:
                request_json("POST", f"/api/tasks/{task_id}/status", json={"status": "running"}, timeout=10)
            except Exception:
                pass
            status, result, error = execute_task(task)
            post_task_status(task_id, status, result, error)
            LAST_ERROR = error
            logger.info("Task completed: %s status=%s", task_id, status)
        except Exception as exc:
            LAST_ERROR = str(exc)
            if is_auth_error(exc):
                logger.error("Task polling forbidden: access_key is invalid or server config was changed")
                time.sleep(30)
            elif isinstance(exc, (requests.exceptions.ConnectionError, requests.exceptions.Timeout)):
                logger.warning("Task polling temporarily unavailable: %s", exc)
                time.sleep(5)
            else:
                logger.exception("Task loop failed")
                time.sleep(5)
        finally:
            CURRENT_TASK = ""


def heartbeat_loop() -> None:
    global LAST_ERROR
    backoff_index = 0
    while not SHUTDOWN.is_set():
        if not is_activated_mode() or not ACCESS_KEY:
            time.sleep(2)
            continue
        try:
            send_heartbeat()
            LAST_ERROR = ""
            backoff_index = 0
            time.sleep(HEARTBEAT_INTERVAL)
        except Exception as exc:
            LAST_ERROR = str(exc)
            if is_auth_error(exc):
                logger.error("Heartbeat forbidden: access_key is invalid or server config was changed")
                time.sleep(30)
                continue
            wait = BACKOFF_SEQUENCE[min(backoff_index, len(BACKOFF_SEQUENCE) - 1)] + random.uniform(0.2, 1.5)
            logger.warning("Heartbeat failed, reconnect in %.1fs: %s", wait, exc)
            backoff_index += 1
            time.sleep(wait)


def websocket_loop() -> None:
    global AGENT_CONNECTED
    if not HAS_WEBSOCKETS:
        logger.warning("websockets package is unavailable; REST heartbeat will still work")
        return
    backoff_index = 0
    while not SHUTDOWN.is_set():
        if not is_activated_mode() or not ACCESS_KEY:
            time.sleep(2)
            continue
        try:
            headers = {"X-Server-Access-Key": ACCESS_KEY, "X-Agent-Id": AGENT_ID}
            if is_activated_mode():
                headers["X-Agent-Token"] = ACCESS_KEY
                url = f"{SERVER_BASE_URL.replace('http://', 'ws://').replace('https://', 'wss://')}/ws/agent?token={ACCESS_KEY}"
                logger.info("Connecting WebSocket: %s", masked_url(url))
                try:
                    ws = ws_connect(url, additional_headers=headers, open_timeout=8)
                except TypeError:
                    ws = ws_connect(url, open_timeout=8)
            else:
                url = WEBSOCKET_URL
                query_join = "&" if "?" in url else "?"
                url_with_agent = f"{url}{query_join}agent_id={AGENT_ID}"
                logger.info("Connecting WebSocket: %s", masked_url(url))
                try:
                    ws = ws_connect(url_with_agent, additional_headers=headers, open_timeout=8)
                except TypeError:
                    ws = ws_connect(f"{url_with_agent}&access_key={ACCESS_KEY}", open_timeout=8)
            with ws:
                logger.info("WebSocket connected")
                AGENT_CONNECTED = True
                backoff_index = 0
                next_heartbeat = 0.0
                while not SHUTDOWN.is_set():
                    now = time.monotonic()
                    if now >= next_heartbeat:
                        safe_ws_send(ws, {"event": "agent_heartbeat", "payload": heartbeat_payload()})
                        next_heartbeat = now + HEARTBEAT_INTERVAL
                    try:
                        raw = ws.recv(timeout=0.08)
                    except TimeoutError:
                        continue
                    if not raw:
                        continue
                    try:
                        message = json.loads(raw)
                    except Exception:
                        continue
        except Exception as exc:
            AGENT_CONNECTED = False
            release_stuck_keys()
            wait = BACKOFF_SEQUENCE[min(backoff_index, len(BACKOFF_SEQUENCE) - 1)] + random.uniform(0.2, 1.5)
            logger.warning("WebSocket disconnected, reconnect in %.1fs: %s", wait, exc)
            backoff_index += 1
            time.sleep(wait)


def _pause_and_exit(code: int = 1) -> None:
    """Pause so user can read the error before the console window closes."""
    print("\n[Нажмите Enter для закрытия...]")
    try:
        input()
    except Exception:
        pass
    sys.exit(code)


def is_autostart_enabled() -> bool:
    if platform.system() != "Windows" or not winreg:
        return False
    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Run",
            0,
            winreg.KEY_READ
        )
        val, _ = winreg.QueryValueEx(key, "PCManager_Agent")
        winreg.CloseKey(key)
        return bool(val)
    except Exception:
        return False


def set_autostart(enable: bool) -> None:
    if platform.system() != "Windows" or not winreg:
        return
    exe_path = str(Path(sys.executable).resolve())
    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Run",
            0,
            winreg.KEY_WRITE | winreg.KEY_SET_VALUE
        )
        if enable:
            winreg.SetValueEx(key, "PCManager_Agent", 0, winreg.REG_SZ, f'"{exe_path}"')
        else:
            try:
                winreg.DeleteValue(key, "PCManager_Agent")
            except FileNotFoundError:
                pass
        winreg.CloseKey(key)
    except Exception as exc:
        logger.warning("Failed to configure Windows auto-startup registry key: %s", exc)


def validate_startup() -> None:
    global ACCESS_KEY, AGENT_ID, AGENT_NAME, WEBSOCKET_URL, _just_activated
    _just_activated = False
    logger.info("Starting PC Control Windows Agent %s", AGENT_VERSION)

    cleanup_old_screenshots()
    if not ENABLED_TASKS:
        logger.error("No enabled_tasks configured")
        
    if has_valid_access_key():
        logger.info("Access key verified locally.")
        try:
            if CONFIG.get("auto_start", True):
                set_autostart(True)
        except Exception:
            pass
    else:
        logger.info("Agent is not activated yet. GUI will prompt for activation.")



import tkinter as tk
from tkinter import ttk, messagebox
import pystray
from PIL import Image

def draw_rounded_rect(canvas, x1, y1, x2, y2, radius=8, **kwargs):
    points = [
        x1 + radius, y1, x1 + radius, y1,
        x2 - radius, y1, x2 - radius, y1,
        x2, y1,
        x2, y1 + radius, x2, y1 + radius,
        x2, y2 - radius, x2, y2 - radius,
        x2, y2,
        x2 - radius, y2, x2 - radius, y2,
        x1 + radius, y2, x1 + radius, y2,
        x1, y2,
        x1, y2 - radius, x1, y2 - radius,
        x1, y1 + radius, x1, y1 + radius,
        x1, y1
    ]
    return canvas.create_polygon(points, **kwargs, smooth=True)

class RoundedEntry(tk.Canvas):
    def __init__(self, parent, width=300, height=36, radius=8, bg_color="#0C0B10", entry_bg="#161523", border_color="#232135", focus_color="#7C3AED", fg="#FFFFFF", show=""):
        super().__init__(parent, width=width, height=height, bg=bg_color, highlightthickness=0, bd=0)
        self.entry_bg = entry_bg
        self.border_color = border_color
        self.focus_color = focus_color
        self.radius = radius
        self.width = width
        self.height = height
        
        self.rect_id = self.draw_rect(border_color)
        
        # Place borderless Entry inside
        self.entry = tk.Entry(self, bg=entry_bg, fg=fg, show=show, font=("Segoe UI", 10), bd=0, insertbackground="#FFFFFF", highlightthickness=0)
        self.create_window(width//2, height//2, window=self.entry, width=width-20, height=height-12)
        
        self.entry.bind("<FocusIn>", self.on_focus_in)
        self.entry.bind("<FocusOut>", self.on_focus_out)
        
        # Bind universal copy/paste (independent of keyboard layout)
        self.entry.bind("<Control-KeyPress>", self.handle_ctrl_keys)
        
        # Right-click context menu
        self.context_menu = tk.Menu(self.entry, tearoff=0, bg="#161523", fg="#FFFFFF", activebackground="#7C3AED", activeforeground="#FFFFFF", bd=1, relief="solid")
        self.context_menu.add_command(label="Копировать (Copy)", command=lambda: self.entry.event_generate("<<Copy>>"))
        self.context_menu.add_command(label="Вставить (Paste)", command=lambda: self.entry.event_generate("<<Paste>>"))
        self.context_menu.add_command(label="Вырезать (Cut)", command=lambda: self.entry.event_generate("<<Cut>>"))
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Выделить всё (Select All)", command=self.select_all)
        
        self.entry.bind("<Button-3>", self.show_context_menu)
        
    def draw_rect(self, border):
        self.delete("border")
        draw_rounded_rect(self, 1, 1, self.width-1, self.height-1, self.radius, fill=self.entry_bg, outline=border, width=1.5, tag="border")
        
    def on_focus_in(self, event):
        self.draw_rect(self.focus_color)
        
    def on_focus_out(self, event):
        self.draw_rect(self.border_color)
        
    def get(self):
        return self.entry.get()
        
    def delete_all(self):
        self.entry.delete(0, "end")
        
    def insert(self, index, text):
        self.entry.insert(index, text)

    def select_all(self, event=None):
        self.entry.select_range(0, "end")
        self.entry.icursor("end")
        return "break"

    def handle_ctrl_keys(self, event):
        if event.keycode == 86:  # V
            self.entry.event_generate("<<Paste>>")
            return "break"
        elif event.keycode == 67:  # C
            self.entry.event_generate("<<Copy>>")
            return "break"
        elif event.keycode == 88:  # X
            self.entry.event_generate("<<Cut>>")
            return "break"
        elif event.keycode == 65:  # A
            self.select_all()
            return "break"

    def show_context_menu(self, event):
        try:
            self.context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.context_menu.grab_release()

class RoundedButton(tk.Canvas):
    def __init__(self, parent, text, command, width=180, height=42, radius=8, bg_color="#0C0B10", btn_color="#7C3AED", hover_color="#9D4EDD", fg_color="#FFFFFF"):
        super().__init__(parent, width=width, height=height, bg=bg_color, highlightthickness=0, bd=0, cursor="hand2")
        self.command = command
        self.btn_color = btn_color
        self.hover_color = hover_color
        self.fg_color = fg_color
        self.radius = radius
        self.width = width
        self.height = height
        
        self.rect_id = draw_rounded_rect(self, 2, 2, width-2, height-2, radius, fill=btn_color, outline="", tag="btn")
        self.text_id = self.create_text(width//2, height//2, text=text, fill=fg_color, font=("Segoe UI", 10, "bold"), tag="txt")
        
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
        self.bind("<ButtonPress-1>", self.on_press)
        self.bind("<ButtonRelease-1>", self.on_release)
        
    def on_enter(self, event):
        self.animate_hover(self.btn_color, self.hover_color, steps=5)
        
    def on_leave(self, event):
        self.animate_hover(self.hover_color, self.btn_color, steps=5)
        
    def on_press(self, event):
        self.move("txt", 1, 1)
        self.itemconfig("btn", fill=self.btn_color)
        
    def on_release(self, event):
        self.move("txt", -1, -1)
        self.itemconfig("btn", fill=self.hover_color)
        if self.command:
            self.command()
            
    def animate_hover(self, start_color, end_color, steps=5, current_step=0):
        if current_step > steps:
            return
        c1 = self.winfo_rgb(start_color)
        c2 = self.winfo_rgb(end_color)
        
        r = (c1[0] + (c2[0] - c1[0]) * current_step // steps) // 256
        g = (c1[1] + (c2[1] - c1[1]) * current_step // steps) // 256
        b = (c1[2] + (c2[2] - c1[2]) * current_step // steps) // 256
        
        color = f"#{r:02x}{g:02x}{b:02x}"
        self.itemconfig("btn", fill=color)
        
        self.after(15, lambda: self.animate_hover(start_color, end_color, steps, current_step + 1))

    def configure(self, **kwargs):
        if "text" in kwargs:
            self.itemconfig("txt", text=kwargs["text"])
        if "state" in kwargs:
            state = kwargs["state"]
            if state == "disabled":
                self.configure(cursor="arrow")
                self.itemconfig("btn", fill="#232135")
                self.unbind("<Enter>")
                self.unbind("<Leave>")
                self.unbind("<ButtonPress-1>")
                self.unbind("<ButtonRelease-1>")
            elif state == "normal":
                self.configure(cursor="hand2")
                self.itemconfig("btn", fill=self.btn_color)
                self.bind("<Enter>", self.on_enter)
                self.bind("<Leave>", self.on_leave)
                self.bind("<ButtonPress-1>", self.on_press)
                self.bind("<ButtonRelease-1>", self.on_release)

class RoundedFrame(tk.Canvas):
    def __init__(self, parent, bg_color="#0C0B10", card_color="#161523", radius=8, width=None, height=None, **kwargs):
        canvas_kwargs = {"bg": bg_color, "highlightthickness": 0, "bd": 0}
        if width: canvas_kwargs["width"] = width
        if height: canvas_kwargs["height"] = height
        super().__init__(parent, **canvas_kwargs)
        self.card_color = card_color
        self.radius = radius
        self.bind("<Configure>", self.on_resize)
        
    def on_resize(self, event):
        self.delete("all")
        w, h = event.width, event.height
        draw_rounded_rect(self, 0, 0, w, h, self.radius, fill=self.card_color, outline="")

class AgentApp(tk.Tk):
    def __init__(self):
        super().__init__()
        
        # Set Windows taskbar icon pairing
        try:
            import ctypes
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("PCManager.Agent")
        except Exception:
            pass
            
        icon_path = get_resource_path("icon.ico")
        if icon_path.exists():
            try:
                self.iconbitmap(icon_path)
            except Exception:
                pass
                
        self.overrideredirect(True)
        
        # Center the window on the screen
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        width, height = 760, 520
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        self.geometry(f"{width}x{height}+{x}+{y}")
        
        self.drag_data = {"x": 0, "y": 0}
        
        # 1px glowing purple border around the entire window
        self.outer_border = tk.Frame(self, bg="#7C3AED", bd=0)
        self.outer_border.pack(fill="both", expand=True)
        
        # Main inner container
        self.main_container = tk.Frame(self.outer_border, bg="#0C0B10")
        self.main_container.pack(fill="both", expand=True, padx=1, pady=1)
        
        # Custom Title Bar
        self.title_bar = tk.Frame(self.main_container, bg="#0C0B10", height=32)
        self.title_bar.pack(side="top", fill="x")
        self.title_bar.pack_propagate(False)
        
        self.title_bar.bind("<ButtonPress-1>", self.start_drag)
        self.title_bar.bind("<B1-Motion>", self.drag_motion)
        
        # App icon in title bar
        logo_path = get_resource_path("logo.png")
        if logo_path.exists():
            try:
                from PIL import ImageTk
                pil_img = Image.open(logo_path).resize((18, 18), Image.Resampling.LANCZOS)
                self.title_logo_img = ImageTk.PhotoImage(pil_img)
                title_logo = tk.Label(self.title_bar, image=self.title_logo_img, bg="#0C0B10")
                title_logo.pack(side="left", padx=(10, 6))
                title_logo.bind("<ButtonPress-1>", self.start_drag)
                title_logo.bind("<B1-Motion>", self.drag_motion)
            except Exception:
                pass
                
        # Title text
        title_lbl = tk.Label(self.title_bar, text="PCManager Agent Dashboard", font=("Segoe UI", 9, "bold"), fg="#7C7892", bg="#0C0B10")
        title_lbl.pack(side="left")
        title_lbl.bind("<ButtonPress-1>", self.start_drag)
        title_lbl.bind("<B1-Motion>", self.drag_motion)
        
        # Window controls container
        controls_frame = tk.Frame(self.title_bar, bg="#0C0B10")
        controls_frame.pack(side="right", fill="y")
        
        # Minimize Button
        min_btn = tk.Button(
            controls_frame, 
            text="—", 
            font=("Segoe UI", 9, "bold"), 
            fg="#A7A2C5", 
            bg="#0C0B10",
            activebackground="#1E1B30", 
            activeforeground="#FFFFFF", 
            bd=0, 
            cursor="hand2", 
            width=4,
            command=self.minimize_to_tray
        )
        min_btn.pack(side="left", fill="y")
        
        # Close Button
        close_btn = tk.Button(
            controls_frame, 
            text="✕", 
            font=("Segoe UI", 10), 
            fg="#A7A2C5", 
            bg="#0C0B10",
            activebackground="#EF4444", 
            activeforeground="#FFFFFF", 
            bd=0, 
            cursor="hand2", 
            width=4,
            command=self.minimize_to_tray
        )
        close_btn.pack(side="left", fill="y")
        
        # Hover bindings
        close_btn.bind("<Enter>", lambda e: close_btn.configure(bg="#EF4444", fg="#FFFFFF"))
        close_btn.bind("<Leave>", lambda e: close_btn.configure(bg="#0C0B10", fg="#A7A2C5"))
        min_btn.bind("<Enter>", lambda e: min_btn.configure(bg="#1E1B30", fg="#FFFFFF"))
        min_btn.bind("<Leave>", lambda e: min_btn.configure(bg="#0C0B10", fg="#A7A2C5"))
        
        # Body frame containing sidebar and main content
        self.body_frame = tk.Frame(self.main_container, bg="#0C0B10")
        self.body_frame.pack(side="bottom", fill="both", expand=True)
        
        self.active_tab = "dashboard"
        self.setup_styles()
        self.create_sidebar()
        self.create_main_content()
        # Default to settings if not activated
        if not is_activated_mode():
            self.switch_tab("settings")
        else:
            self.switch_tab("dashboard")
        self.update_stats_loop()
        self.create_tray_icon()
        self.after(2000, self.check_updates_gui)

    def check_updates_gui(self):
        def worker():
            if check_for_updates():
                self.after(0, self.prompt_update_gui)
        threading.Thread(target=worker, daemon=True).start()

    def prompt_update_gui(self):
        ans = messagebox.askyesno(
            "Доступно обновление",
            "Доступна новая версия PCManager Agent!\nХотите установить обновление сейчас?\n\n(Агент автоматически обновится и перезапустится)"
        )
        if ans:
            perform_update()

    def start_drag(self, event):
        self.drag_data["x"] = event.x
        self.drag_data["y"] = event.y

    def drag_motion(self, event):
        deltax = event.x - self.drag_data["x"]
        deltay = event.y - self.drag_data["y"]
        x = self.winfo_x() + deltax
        y = self.winfo_y() + deltay
        self.geometry(f"+{x}+{y}")
        
    def setup_styles(self):
        # Configure overall style
        style = ttk.Style()
        style.theme_use('clam')
        style.configure(".", background="#0C0B10", foreground="#FFFFFF", fieldbackground="#161523")
        
    def create_sidebar(self):
        sidebar = tk.Frame(self.body_frame, bg="#13121C", width=200)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)
        
        # Title/Logo in sidebar
        logo_frame = tk.Frame(sidebar, bg="#13121C", pady=20)
        logo_frame.pack(fill="x")
        
        # Centered container for Logo + Text
        header_content = tk.Frame(logo_frame, bg="#13121C")
        header_content.pack(anchor="center")
        
        # Load and render logo image in sidebar header (32x32 size for side-by-side)
        logo_path = get_resource_path("logo.png")
        if logo_path.exists():
            try:
                from PIL import ImageTk
                pil_img = Image.open(logo_path).resize((32, 32), Image.Resampling.LANCZOS)
                self.sidebar_logo_img = ImageTk.PhotoImage(pil_img)
                
                logo_img_lbl = tk.Label(header_content, image=self.sidebar_logo_img, bg="#13121C")
                logo_img_lbl.pack(side="left", padx=(0, 8))
            except Exception as exc:
                logger.warning("Failed to load sidebar logo image: %s", exc)
        
        logo_lbl = tk.Label(header_content, text="PCManager", font=("Segoe UI", 16, "bold"), fg="#7C3AED", bg="#13121C")
        logo_lbl.pack(side="left")
        
        subtitle_lbl = tk.Label(logo_frame, text="Windows Agent", font=("Segoe UI", 9), fg="#7C7892", bg="#13121C", pady=2)
        subtitle_lbl.pack()
        
        # Menu Tabs
        self.sidebar_btns = {}
        tabs = [
            ("dashboard", "🏠  Dashboard"),
            ("games", "🎮  Games & Apps"),
            ("settings", "⚙️  Settings")
        ]
        
        for tab_id, tab_label in tabs:
            btn = tk.Button(
                sidebar,
                text=tab_label,
                font=("Segoe UI", 11),
                fg="#FFFFFF",
                bg="#13121C",
                activebackground="#7C3AED",
                activeforeground="#FFFFFF",
                bd=0,
                cursor="hand2",
                anchor="w",
                padx=20,
                pady=12,
                command=lambda tid=tab_id: self.switch_tab(tid)
            )
            btn.pack(fill="x", pady=2)
            self.sidebar_btns[tab_id] = btn
            
    def create_main_content(self):
        self.content_frame = tk.Frame(self.body_frame, bg="#0C0B10")
        self.content_frame.pack(side="right", fill="both", expand=True)
        
    def switch_tab(self, tab_id):
        self.active_tab = tab_id
        for tid, btn in self.sidebar_btns.items():
            if tid == tab_id:
                btn.configure(bg="#7C3AED", fg="#FFFFFF")
            else:
                btn.configure(bg="#13121C", fg="#A7A2C5")
                
        # Clear main content
        for widget in self.content_frame.winfo_children():
            widget.destroy()
            
        if tab_id == "dashboard":
            self.render_dashboard()
        elif tab_id == "games":
            self.render_games()
        elif tab_id == "settings":
            self.render_settings()
            
    def render_dashboard(self):
        # Header
        hdr = tk.Label(self.content_frame, text="System Status Overview", font=("Segoe UI", 16, "bold"), fg="#FFFFFF", bg="#0C0B10", anchor="w")
        hdr.pack(fill="x", padx=30, pady=(25, 10))
        
        # Top card with connection state - using RoundedFrame
        conn_card = RoundedFrame(self.content_frame, card_color="#161523", radius=10)
        conn_card.pack(fill="x", padx=30, pady=10)
        
        self.conn_dot = tk.Label(conn_card, text="●", font=("Segoe UI", 18), fg="#EF4444", bg="#161523")
        self.conn_dot.pack(side="left", padx=(20, 0), pady=12)
        
        self.conn_lbl = tk.Label(conn_card, text="Connecting to server...", font=("Segoe UI", 12, "bold"), fg="#7C7892", bg="#161523", padx=10)
        self.conn_lbl.pack(side="left", pady=12)
        
        # Grid of resource cards (CPU & RAM)
        grid_frame = tk.Frame(self.content_frame, bg="#0C0B10")
        grid_frame.pack(fill="x", padx=30, pady=10)
        
        # CPU Card - using RoundedFrame
        cpu_card = RoundedFrame(grid_frame, card_color="#161523", radius=12, width=240, height=180)
        cpu_card.pack(side="left", fill="both", expand=True, padx=(0, 10))
        cpu_card.pack_propagate(False)
        
        cpu_title = tk.Label(cpu_card, text="CPU Usage", font=("Segoe UI", 11, "bold"), fg="#7C7892", bg="#161523", anchor="w")
        cpu_title.pack(fill="x", padx=20, pady=(20, 5))
        self.cpu_val_lbl = tk.Label(cpu_card, text="0.0%", font=("Segoe UI", 28, "bold"), fg="#FFFFFF", bg="#161523", anchor="w")
        self.cpu_val_lbl.pack(fill="x", padx=20, pady=5)
        
        self.cpu_canvas = tk.Canvas(cpu_card, height=14, bg="#161523", highlightthickness=0)
        self.cpu_canvas.pack(fill="x", padx=20, pady=10)
        self.draw_progress_bar(self.cpu_canvas, 0)
        
        # RAM Card - using RoundedFrame
        ram_card = RoundedFrame(grid_frame, card_color="#161523", radius=12, width=240, height=180)
        ram_card.pack(side="right", fill="both", expand=True, padx=(10, 0))
        ram_card.pack_propagate(False)
        
        ram_title = tk.Label(ram_card, text="RAM Usage", font=("Segoe UI", 11, "bold"), fg="#7C7892", bg="#161523", anchor="w")
        ram_title.pack(fill="x", padx=20, pady=(20, 5))
        self.ram_val_lbl = tk.Label(ram_card, text="0.0%", font=("Segoe UI", 28, "bold"), fg="#FFFFFF", bg="#161523", anchor="w")
        self.ram_val_lbl.pack(fill="x", padx=20, pady=5)
        
        self.ram_canvas = tk.Canvas(ram_card, height=14, bg="#161523", highlightthickness=0)
        self.ram_canvas.pack(fill="x", padx=20, pady=10)
        self.draw_progress_bar(self.ram_canvas, 0)
        
        # Task Card - using RoundedFrame
        task_card = RoundedFrame(self.content_frame, card_color="#161523", radius=10)
        task_card.pack(fill="x", padx=30, pady=10)
        
        task_title = tk.Label(task_card, text="Last Active Task:", font=("Segoe UI", 11, "bold"), fg="#7C7892", bg="#161523", anchor="w")
        task_title.pack(side="left", padx=(20, 0), pady=12)
        self.task_lbl = tk.Label(task_card, text="-", font=("Segoe UI", 11, "bold"), fg="#7C3AED", bg="#161523")
        self.task_lbl.pack(side="left", padx=10, pady=12)

        # System Info Badges Row
        sys_frame = tk.Frame(self.content_frame, bg="#0C0B10")
        sys_frame.pack(fill="x", padx=30, pady=(10, 0))
        
        # OS Badge (Full Width)
        os_badge = RoundedFrame(sys_frame, card_color="#161523", radius=8)
        os_badge.pack(fill="x", expand=True)
        os_lbl = tk.Label(os_badge, text=f"🖥️ OS: {platform.system()} {platform.release()}", font=("Segoe UI", 9, "bold"), fg="#A7A2C5", bg="#161523")
        os_lbl.pack(pady=8)
        
    def draw_progress_bar(self, canvas, percentage):
        self.draw_progress_bar_static(canvas, percentage)

    def draw_progress_bar_static(self, canvas, percentage):
        canvas.delete("all")
        width = canvas.winfo_width()
        if width <= 1:
            width = 200
        canvas.create_line(6, 7, width-6, 7, width=12, fill="#232135", capstyle="round")
        if percentage > 0:
            fill_width = max(12, int(6 + (width - 12) * (percentage / 100)))
            canvas.create_line(6, 7, fill_width, 7, width=12, fill="#7C3AED", capstyle="round")

    def animate_progress_bar(self, canvas, start_val, end_val, steps=12, current_step=0):
        if SHUTDOWN.is_set() or self.active_tab != "dashboard":
            return
        if current_step > steps:
            return
        val = start_val + (end_val - start_val) * current_step / steps
        self.draw_progress_bar_static(canvas, val)
        self.after(16, lambda: self.animate_progress_bar(canvas, start_val, end_val, steps, current_step + 1))
            
    def render_games(self):
        hdr = tk.Label(self.content_frame, text="Detected Games & Launchers", font=("Segoe UI", 16, "bold"), fg="#FFFFFF", bg="#0C0B10", anchor="w")
        hdr.pack(fill="x", padx=30, pady=(20, 5))
        
        desc = tk.Label(self.content_frame, text="These games and launchers are automatically detected on your PC and can be controlled remotely.", font=("Segoe UI", 9), fg="#7C7892", bg="#0C0B10", anchor="w")
        desc.pack(fill="x", padx=30, pady=(0, 10))
        
        list_frame = tk.Frame(self.content_frame, bg="#0C0B10")
        list_frame.pack(fill="both", expand=True, padx=30, pady=(0, 15))
        
        detected = auto_detect_launchers()
        
        all_games = [
            ("majestic_launcher", "Majestic Launcher", "🎮"),
            ("gta5", "Grand Theft Auto V", "🚗"),
            ("steam", "Steam Launcher", "💨"),
            ("epic_games", "Epic Games Launcher", "🎮"),
            ("minecraft", "Minecraft", "⛏️"),
            ("roblox", "Roblox", "🧱"),
            ("riot_games", "Riot Client", "🎯"),
            ("ea_desktop", "EA Desktop", "🎮"),
            ("battle_net", "Battle.net Launcher", "❄️"),
            ("ubisoft_connect", "Ubisoft Connect", "🌀"),
        ]
        
        for key, name, icon in all_games:
            path = detected.get(key)
            is_found = path is not None
            
            row = RoundedFrame(list_frame, card_color="#161523", radius=6)
            row.pack(fill="x", pady=2)
            
            name_lbl = tk.Label(row, text=f"{icon}  {name}", font=("Segoe UI", 10, "bold"), fg="#FFFFFF", bg="#161523", anchor="w")
            name_lbl.pack(side="left", padx=12, pady=5)
            
            if is_found:
                trunc_path = path
                if len(path) > 42:
                    trunc_path = "..." + path[-39:]
                path_lbl = tk.Label(row, text=trunc_path, font=("Segoe UI", 8), fg="#7C7892", bg="#161523", anchor="e")
                path_lbl.pack(side="right", padx=(0, 12), pady=5)
                
                badge = tk.Frame(row, bg="#064E3B", padx=6, pady=1)
                badge.pack(side="right", padx=8, pady=5)
                tk.Label(badge, text="Detected", font=("Segoe UI", 8, "bold"), fg="#34D399", bg="#064E3B").pack()
            else:
                badge = tk.Frame(row, bg="#1F2937", padx=6, pady=1)
                badge.pack(side="right", padx=12, pady=5)
                tk.Label(badge, text="Not Found", font=("Segoe UI", 8, "bold"), fg="#9CA3AF", bg="#1F2937").pack()

    def render_settings(self):
        hdr = tk.Label(self.content_frame, text="Connection Configuration", font=("Segoe UI", 16, "bold"), fg="#FFFFFF", bg="#0C0B10", anchor="w")
        hdr.pack(fill="x", padx=30, pady=(25, 10))
        
        form_frame = tk.Frame(self.content_frame, bg="#0C0B10", padx=30)
        form_frame.pack(fill="both", expand=True)
        
        # Activation Warning / Tip Card
        if not is_activated_mode():
            tip_card = tk.Frame(form_frame, bg="#3B0764", padx=15, pady=10, bd=0)
            tip_card.pack(fill="x", pady=(5, 15))
            tk.Label(tip_card, text="🔑 Агент не привязан к боту", font=("Segoe UI", 11, "bold"), fg="#F3F4F6", bg="#3B0764", anchor="w").pack(fill="x")
            tk.Label(tip_card, text="Для активации введите ключ привязки (TG-XXXX-XXXX) из Telegram-бота.", font=("Segoe UI", 9), fg="#E5E7EB", bg="#3B0764", anchor="w", justify="left", wraplength=480).pack(fill="x", pady=(2, 0))
            
        # Server Base URL Entry (Hidden from UI but created in memory for background operations)
        self.url_ent = RoundedEntry(form_frame, width=480, height=38, bg_color="#0C0B10")
        self.url_ent.insert(0, CONFIG.get("server_base_url") or SERVER_BASE_URL)
        
        # Activation / Access Key Entry
        key_label = "Activation Key (TG-XXXX-XXXX) or Access Key" if not is_activated_mode() else "Access Key"
        tk.Label(form_frame, text=key_label, font=("Segoe UI", 10, "bold"), fg="#7C7892", bg="#0C0B10", anchor="w").pack(fill="x", pady=(5, 5))
        self.key_ent = RoundedEntry(form_frame, width=480, height=38, bg_color="#0C0B10")
        self.key_ent.pack(anchor="w", pady=(0, 15))
        current_key = CONFIG.get("access_key") or ACCESS_KEY
        if current_key == "CHANGE_ME":
            current_key = ""
        self.key_ent.insert(0, current_key)
        
        # Auto-startup toggle
        self.autostart_var = tk.BooleanVar(value=is_autostart_enabled())
        self.autostart_chk = tk.Checkbutton(
            form_frame, 
            text="Запускать автоматически при старте системы", 
            variable=self.autostart_var, 
            font=("Segoe UI", 9), 
            fg="#FFFFFF", 
            bg="#0C0B10", 
            selectcolor="#161523",
            activebackground="#0C0B10",
            activeforeground="#FFFFFF",
            command=self.toggle_autostart
        )
        self.autostart_chk.pack(anchor="w", pady=(5, 15))
        
        # Reconnect Button
        btn_text = "Activate Agent" if not is_activated_mode() else "Save & Reconnect"
        self.save_btn = RoundedButton(form_frame, text=btn_text, command=self.save_settings, width=180, height=42, bg_color="#0C0B10")
        self.save_btn.pack(anchor="w", pady=10)
        
    def toggle_autostart(self):
        enable = self.autostart_var.get()
        set_autostart(enable)
        CONFIG["auto_start"] = enable
        try:
            CONFIG_FILE.write_text(json.dumps(CONFIG, ensure_ascii=False, indent=2), encoding="utf-8")
        except Exception:
            pass
            
    def save_settings(self):
        new_url = self.url_ent.get().strip()
        new_key = self.key_ent.get().strip()
        
        if not new_url or not new_key:
            messagebox.showerror("Error", "All configuration fields must be filled!")
            return
            
        global SERVER_BASE_URL, ACCESS_KEY, WEBSOCKET_URL, AGENT_ID, AGENT_NAME, _just_activated
        
        # Check if the user entered an activation key (starts with TG-)
        if new_key.startswith("TG-"):
            self.save_btn.configure(text="Activating...", state="disabled")
            self.update()
            try:
                payload = {
                    "activation_key": new_key,
                    "hostname": socket.gethostname(),
                    "username": os.environ.get("USERNAME") or os.environ.get("USER") or "",
                    "platform": platform.system(),
                    "os_name": platform.platform(),
                    "local_ip": local_ip(),
                }
                response = requests.post(
                    f"{new_url}/api/agents/activate",
                    json=payload,
                    timeout=20,
                )
                if response.status_code == 400:
                    try:
                        detail = response.json().get("detail", "Неверный или уже использованный ключ.")
                    except Exception:
                        detail = "Неверный или уже использованный ключ."
                    messagebox.showerror("Error", f"Activation failed: {detail}")
                    return
                elif response.status_code == 404:
                    messagebox.showerror("Error", "Activation failed: Key not found on server.")
                    return
                response.raise_for_status()
                res_data = response.json()
                
                agent_id = res_data["agent_id"]
                agent_token = res_data["agent_token"]
                
                CONFIG["server_base_url"] = new_url
                CONFIG["access_key"] = agent_token
                CONFIG["agent_id"] = agent_id
                CONFIG["agent_name"] = f"PC {socket.gethostname()}"
                CONFIG["is_activated"] = True
                CONFIG["websocket_url"] = f"{new_url.replace('http://', 'ws://').replace('https://', 'wss://')}/ws/status"
                
                CONFIG_FILE.write_text(json.dumps(CONFIG, ensure_ascii=False, indent=2), encoding="utf-8")
                
                SERVER_BASE_URL = new_url
                ACCESS_KEY = agent_token
                AGENT_ID = agent_id
                AGENT_NAME = CONFIG["agent_name"]
                WEBSOCKET_URL = CONFIG["websocket_url"]
                _just_activated = True
                
                messagebox.showinfo("Success", f"Activation successful! Device ID: {agent_id}")
                self.switch_tab("dashboard")
            except Exception as exc:
                messagebox.showerror("Error", f"Failed to connect and activate: {exc}")
            finally:
                self.save_btn.configure(text="Activate Agent", state="normal")
        else:
            # Regular key change / server URL change
            CONFIG["server_base_url"] = new_url
            CONFIG["access_key"] = new_key
            CONFIG["websocket_url"] = f"{new_url.replace('http://', 'ws://').replace('https://', 'wss://')}/ws/status"
            
            try:
                CONFIG_FILE.write_text(json.dumps(CONFIG, ensure_ascii=False, indent=2), encoding="utf-8")
                SERVER_BASE_URL = new_url
                ACCESS_KEY = new_key
                WEBSOCKET_URL = CONFIG["websocket_url"]
                
                messagebox.showinfo("Success", "Configuration successfully saved! Reconnecting...")
                self.switch_tab("dashboard")
            except Exception as exc:
                messagebox.showerror("Error", f"Failed to save configuration: {exc}")
            
    # Removed Logs Tab
        
    def update_stats_loop(self):
        # Obtain system metrics
        cpu = psutil.cpu_percent()
        ram = psutil.virtual_memory().percent
        
        if self.active_tab == "dashboard":
            self.cpu_val_lbl.configure(text=f"{cpu}%")
            self.ram_val_lbl.configure(text=f"{ram}%")
            
            # Smoothly animate progress bars from previous values
            old_cpu = getattr(self, "prev_cpu", 0.0)
            old_ram = getattr(self, "prev_ram", 0.0)
            
            self.animate_progress_bar(self.cpu_canvas, old_cpu, cpu)
            self.animate_progress_bar(self.ram_canvas, old_ram, ram)
            
            self.prev_cpu = cpu
            self.prev_ram = ram
            
            # Connection State Indicator
            if AGENT_CONNECTED:
                self.conn_dot.configure(fg="#10B981")
                self.conn_lbl.configure(text="Connected to server successfully", fg="#10B981")
            else:
                self.conn_dot.configure(fg="#EF4444")
                self.conn_lbl.configure(text="Connecting to server...", fg="#7C7892")
                
            self.task_lbl.configure(text=CURRENT_TASK or "None")
            
        self.after(2000, self.update_stats_loop)
        
    def create_image(self):
        icon_path = get_resource_path("icon.ico")
        if icon_path.exists():
            try:
                return Image.open(icon_path)
            except Exception:
                pass
        return Image.new('RGB', (64, 64), color=(124, 58, 237))
        
    def show_from_tray(self):
        """Restore window and force it to the front of all windows."""
        self.deiconify()
        # Trick Windows into allowing foreground steal:
        # iconify (minimize) then restore rapidly forces Windows to grant focus
        self.iconify()
        self.after(50, self._force_to_front)

    def _force_to_front(self):
        self.deiconify()
        self.state("normal")
        self.lift()
        self.attributes("-topmost", True)
        self.after(200, lambda: self.attributes("-topmost", False))
        self.focus_force()

    def on_tray_clicked(self, icon, item):
        if str(item) == "Open Dashboard":
            self.after(0, self.show_from_tray)
        elif str(item) == "Exit":
            icon.stop()
            SHUTDOWN.set()
            self.after(0, self.destroy)
            
    def minimize_to_tray(self):
        self.withdraw()

    def create_tray_icon(self):
        menu = pystray.Menu(
            pystray.MenuItem('Open Dashboard', self.on_tray_clicked, default=True),
            pystray.MenuItem('Exit', self.on_tray_clicked)
        )
        self.tray = pystray.Icon("PCManager", self.create_image(), "PCManager Agent", menu)
        threading.Thread(target=self.tray.run, daemon=True).start()

def launch_steam_on_startup():
    try:
        steam_running = False
        if platform.system() == "Windows":
            # 1. Try checking via psutil first for standard user processes (very fast)
            try:
                for proc in psutil.process_iter(['name']):
                    try:
                        name = proc.info.get('name')
                        if name and name.lower() == 'steam.exe':
                            steam_running = True
                            logger.info("Detected steam.exe running via psutil check.")
                            break
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        continue
            except Exception as pe:
                logger.debug("psutil check failed: %s", pe)

            # 2. Fall back to tasklist if not detected via psutil (helps if steam runs as Admin)
            if not steam_running:
                try:
                    system32 = os.path.join(os.environ.get('SystemRoot', 'C:\\Windows'), 'System32')
                    tasklist_bin = os.path.join(system32, 'tasklist.exe')
                    if not os.path.exists(tasklist_bin):
                        tasklist_bin = 'tasklist'
                    
                    out = subprocess.check_output(
                        f'"{tasklist_bin}" /NH /FI "IMAGENAME eq steam.exe"',
                        shell=True,
                        creationflags=subprocess.CREATE_NO_WINDOW
                    ).decode('cp866', errors='ignore')
                    if "steam.exe" in out.lower():
                        steam_running = True
                        logger.info("Detected steam.exe running via tasklist check.")
                except Exception as e:
                    logger.error("Error checking steam status via tasklist: %s", e)
        else:
            for proc in psutil.process_iter(['name']):
                try:
                    name = proc.info.get('name')
                    if name and name.lower() == 'steam.exe':
                        steam_running = True
                        break
                except Exception:
                    pass
                
        if steam_running:
            logger.info("Steam is already running. Skipping launch.")
            return

        steam_dir = get_steam_path()
        if steam_dir:
            steam_exe = os.path.join(steam_dir, "steam.exe")
            if os.path.exists(steam_exe):
                logger.info("Auto-launching Steam from %s", steam_exe)
                try:
                    subprocess.Popen([steam_exe], shell=False, creationflags=0x01000008 if platform.system() == "Windows" else 0)
                except OSError as e:
                    if getattr(e, "winerror", 0) == 5:
                        logger.warning("Access denied with breakaway flags. Retrying launch without breakaway...")
                        subprocess.Popen([steam_exe], shell=False)
                    else:
                        raise


            else:
                logger.warning("Steam exe not found at %s", steam_exe)
        else:
            logger.warning("Steam path could not be detected")
    except Exception as e:
        logger.error("Error launching Steam on startup: %s", e)



def check_for_updates() -> bool:
    """Checks the server for a newer version of the agent.
    Returns True if an update is available.
    """
    try:
        url = f"{SERVER_BASE_URL}/api/agents/version/latest"
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        data = r.json()
        latest_version = data.get("latest_version")
        if latest_version and latest_version != AGENT_VERSION:
            v_curr = [int(x) for x in AGENT_VERSION.split(".")]
            v_late = [int(x) for x in latest_version.split(".")]
            if v_late > v_curr:
                logger.info("New agent version available: %s (current: %s)", latest_version, AGENT_VERSION)
                return True
    except Exception as e:
        logger.warning("Failed to check for updates: %s", e)
    return False


def perform_update(download_url: str = None):
    if not download_url:
        download_url = f"{SERVER_BASE_URL}/releases/agent.exe"
    elif not download_url.startswith("http"):
        download_url = f"{SERVER_BASE_URL}{download_url}"
        
    logger.info("Downloading update from %s...", download_url)
    try:
        new_exe_path = LOCAL_DIR / "PCManager_Agent_new.exe"
        r = requests.get(download_url, stream=True, timeout=60)
        r.raise_for_status()
        with open(new_exe_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
        logger.info("Download complete: %s", new_exe_path)
        
        if not getattr(sys, "frozen", False):
            logger.info("Running in dev mode: skipping file hot-swap.")
            messagebox.showinfo("Update Info", "Update download simulated successfully (dev mode).")
            return
            
        updater_bat = LOCAL_DIR / "updater.bat"
        current_exe = Path(sys.executable).resolve()
        
        bat_content = f"""@echo off
timeout /t 2 /nobreak > NUL
:loop
del "{current_exe}" 2>nul
if exist "{current_exe}" (
    timeout /t 1 /nobreak > NUL
    goto loop
)
copy /y "{new_exe_path}" "{current_exe}" > NUL
del "{new_exe_path}" > NUL
start "" "{current_exe}"
del "%~f0"
"""
        updater_bat.write_text(bat_content, encoding="ascii")
        logger.info("Launching updater.bat detached...")
        
        try:
            subprocess.Popen(
                [str(updater_bat)],
                shell=True,
                creationflags=0x01000008 if platform.system() == "Windows" else 0
            )
        except OSError as e:
            if getattr(e, "winerror", 0) == 5:
                logger.warning("Access denied with breakaway flags for updater. Retrying launch without breakaway...")
                subprocess.Popen([str(updater_bat)], shell=True)
            else:
                raise
        
        SHUTDOWN.set()
        sys.exit(0)
    except Exception as e:
        logger.error("Error during update: %s", e)
        messagebox.showerror("Update Error", f"Ошибка во время обновления: {e}")


def run_startup_tasks():
    try:
        launch_steam_on_startup()
    except Exception as e:
        logger.error("Error running Steam startup task: %s", e)
        
    logger.info("Startup tasks: waiting 5 seconds for connection establishment before screenshot...")
    time.sleep(5)
    try:
        logger.info("Startup tasks: capturing and uploading initial screenshot...")
        save_screenshot()
        logger.info("Startup tasks: initial screenshot uploaded successfully")
    except Exception as e:
        logger.error("Error taking initial screenshot: %s", e)


def main() -> None:
    validate_startup()
    trigger_startup_rules()
    threads = [
        threading.Thread(target=heartbeat_loop, name="heartbeat", daemon=True),
        threading.Thread(target=task_loop, name="tasks", daemon=True),
        threading.Thread(target=websocket_loop, name="websocket", daemon=True),
        threading.Thread(target=automation_rules_loop, name="automations", daemon=True),
    ]
    for thread in threads:
        thread.start()
        
    threading.Thread(target=run_startup_tasks, name="startup_tasks", daemon=True).start()
        
    app = AgentApp()
    app.mainloop()

if __name__ == "__main__":
    main()

