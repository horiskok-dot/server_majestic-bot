import json
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from ..config import get_settings


def setup_logging() -> None:
    settings = get_settings()
    log_dir = Path(settings.logs_dir)
    log_dir.mkdir(parents=True, exist_ok=True)
    root = logging.getLogger()
    root.setLevel(logging.INFO)
    if root.handlers:
        return
    formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s")
    server_handler = RotatingFileHandler(log_dir / "server.log", maxBytes=2_000_000, backupCount=5, encoding="utf-8")
    server_handler.setFormatter(formatter)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    root.addHandler(server_handler)
    root.addHandler(console_handler)


def append_json_log(filename: str, payload: dict) -> None:
    settings = get_settings()
    path = Path(settings.logs_dir) / filename
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=False) + "\n")
