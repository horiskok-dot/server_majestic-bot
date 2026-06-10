import re
import uuid
from pathlib import Path

from ..config import get_settings


SAFE_NAME_RE = re.compile(r"[^A-Za-z0-9._-]+")
PUBLIC_TYPES = {
    "upload",
    "telegram_file",
    "photo",
    "screenshot",
    "video",
    "server_screenshot",
    "agent_screenshot",
    "server_webcam_photo",
    "agent_camera_photo",
    "server_webcam_video",
    "agent_camera_video",
}


def storage_root() -> Path:
    root = Path(get_settings().storage_dir).resolve()
    root.mkdir(parents=True, exist_ok=True)
    for name in [
        "uploads",
        "telegram_files",
        "temp",
        "photos/server_webcam",
        "photos/agents_camera",
        "screenshots/server",
        "screenshots/agents",
        "videos/server_webcam",
        "videos/agents_camera",
    ]:
        (root / name).mkdir(parents=True, exist_ok=True)
    return root


def public_type_dir(public_type: str) -> Path:
    mapping = {
        "upload": "uploads",
        "telegram_file": "telegram_files",
        "photo": "photos/agents_camera",
        "screenshot": "screenshots/agents",
        "video": "videos/agents_camera",
        "server_screenshot": "screenshots/server",
        "agent_screenshot": "screenshots/agents",
        "server_webcam_photo": "photos/server_webcam",
        "agent_camera_photo": "photos/agents_camera",
        "server_webcam_video": "videos/server_webcam",
        "agent_camera_video": "videos/agents_camera",
    }
    if public_type not in mapping:
        raise ValueError("Invalid file category")
    target = (storage_root() / mapping[public_type]).resolve()
    if not str(target).startswith(str(storage_root())):
        raise ValueError("Invalid storage path")
    return target


def safe_filename(original: str) -> str:
    original = Path(original or "file.bin").name
    cleaned = SAFE_NAME_RE.sub("_", original).strip("._") or "file.bin"
    return f"{uuid.uuid4().hex}_{cleaned}"
