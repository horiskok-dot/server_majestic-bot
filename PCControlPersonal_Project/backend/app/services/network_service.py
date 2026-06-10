import socket
import time

from ..config import get_settings


STARTED_AT = time.time()


def get_local_ip() -> str:
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.connect(("8.8.8.8", 80))
        value = sock.getsockname()[0]
        sock.close()
        return value
    except Exception:
        return "127.0.0.1"


def server_info() -> dict:
    settings = get_settings()
    base = settings.base_public_url.rstrip("/")
    ws_base = base.replace("https://", "wss://").replace("http://", "ws://")
    return {
        "server_name": settings.app_name,
        "hostname": socket.gethostname(),
        "local_ip": get_local_ip(),
        "public_url": settings.base_public_url,
        "server_port": settings.server_port,
        "base_url": base,
        "websocket_url": f"{ws_base}/ws/status",
        "agent_websocket_url": f"{ws_base}/ws/agent",
        "uptime": int(time.time() - STARTED_AT),
        "version": settings.app_version,
    }
