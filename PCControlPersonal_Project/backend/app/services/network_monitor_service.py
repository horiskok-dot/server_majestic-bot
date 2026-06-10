from __future__ import annotations

import ipaddress
import json
import socket
import time
from datetime import datetime
from pathlib import Path
from typing import Any

from ..config import get_settings
from .command_service import run_safe
from .event_service import add_event


ROUTER_FALLBACK = "192.168.0.1"


def _data_path(name: str) -> Path:
    path = Path(get_settings().data_dir) / name
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def _default_iface() -> str:
    code, out = run_safe(["bash", "-lc", "ip route | awk '/default/ {print $5; exit}'"], timeout=5)
    return out.strip() if code == 0 and out.strip() else "enp4s0"


def _router_ip() -> str:
    code, out = run_safe(["bash", "-lc", "ip route | awk '/default/ {print $3; exit}'"], timeout=5)
    return out.strip() if code == 0 and out.strip() else ROUTER_FALLBACK


def _ping_ms(host: str) -> dict[str, Any]:
    code, out = run_safe(["ping", "-c", "1", "-W", "2", host], timeout=5)
    if code != 0:
        return {"ok": False, "host": host, "ms": None}
    marker = "time="
    if marker not in out:
        return {"ok": True, "host": host, "ms": None}
    try:
        value = out.split(marker, 1)[1].split()[0]
        return {"ok": True, "host": host, "ms": round(float(value), 1)}
    except Exception:
        return {"ok": True, "host": host, "ms": None}


def _dns_ok() -> bool:
    try:
        socket.gethostbyname("api.telegram.org")
        return True
    except Exception:
        return False


def _internet_ok() -> bool:
    try:
        socket.create_connection(("1.1.1.1", 53), timeout=3).close()
        return True
    except Exception:
        return False


def _link_speed(iface: str) -> str:
    code, out = run_safe(["bash", "-lc", f"command -v ethtool >/dev/null && ethtool {iface} 2>/dev/null | awk -F': ' '/Speed:/ {{print $2; exit}}' || true"], timeout=5)
    return out.strip() if code == 0 and out.strip() else "unknown"


def traffic_stats(iface: str | None = None) -> dict[str, Any]:
    iface = iface or _default_iface()
    rows = Path("/proc/net/dev").read_text(encoding="utf-8", errors="ignore").splitlines()
    for row in rows:
        if ":" not in row:
            continue
        name, data = row.split(":", 1)
        if name.strip() != iface:
            continue
        parts = data.split()
        return {
            "iface": iface,
            "rx_bytes": int(parts[0]),
            "tx_bytes": int(parts[8]),
            "time": datetime.utcnow().isoformat(),
        }
    return {"iface": iface, "rx_bytes": 0, "tx_bytes": 0, "time": datetime.utcnow().isoformat()}


def network_status() -> dict[str, Any]:
    iface = _default_iface()
    router = _router_ip()
    google = _ping_ms("8.8.8.8")
    cloudflare = _ping_ms("1.1.1.1")
    router_ping = _ping_ms(router)
    return {
        "time": datetime.utcnow().isoformat(),
        "iface": iface,
        "local_ips": _local_ips(),
        "router_ip": router,
        "lan_speed": _link_speed(iface),
        "router_ping": router_ping,
        "google_ping": google,
        "cloudflare_ping": cloudflare,
        "internet_ok": _internet_ok(),
        "dns_ok": _dns_ok(),
        "traffic": traffic_stats(iface),
    }


def _local_ips() -> list[str]:
    code, out = run_safe(["hostname", "-I"], timeout=5)
    return [x.strip() for x in out.split() if x.strip()] if code == 0 else []


def _read_known_devices() -> dict[str, Any]:
    path = _data_path("devices.json")
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _write_known_devices(devices: dict[str, Any]) -> None:
    _data_path("devices.json").write_text(json.dumps(devices, ensure_ascii=False, indent=2), encoding="utf-8")


def _hostname_for(ip: str) -> str:
    try:
        return socket.gethostbyaddr(ip)[0]
    except Exception:
        return ""


def devices_from_neigh(update_store: bool = True) -> list[dict[str, Any]]:
    code, out = run_safe(["ip", "neigh"], timeout=8)
    now = datetime.utcnow().isoformat()
    known = _read_known_devices()
    devices: list[dict[str, Any]] = []
    if code == 0:
        for line in out.splitlines():
            parts = line.split()
            if len(parts) < 5 or "lladdr" not in parts:
                continue
            ip = parts[0]
            mac = parts[parts.index("lladdr") + 1].lower()
            state = parts[-1].lower()
            device_id = mac.replace(":", "")
            previous = known.get(device_id, {})
            is_new = not bool(previous)
            item = {
                "id": device_id,
                "ip": ip,
                "mac": mac,
                "hostname": previous.get("hostname") or _hostname_for(ip),
                "online": state not in {"failed", "incomplete"},
                "state": state,
                "first_seen": previous.get("first_seen") or now,
                "last_seen": now,
                "vendor": "",
                "known": bool(previous.get("known", False)),
                "name": previous.get("name", ""),
                "is_new": is_new,
            }
            known[device_id] = item
            devices.append(item)
            if update_store and is_new:
                add_event("network_device_new", "warning", "Новое устройство в сети", f"{ip} {mac}", "network", {"ip": ip, "mac": mac})
    if update_store:
        _write_known_devices(known)
    return sorted(known.values(), key=lambda x: (not x.get("online"), x.get("ip", "")))


def scan_lan() -> dict[str, Any]:
    subnet = get_settings().network_scan_subnet
    try:
        net = ipaddress.ip_network(subnet, strict=False)
    except Exception:
        net = ipaddress.ip_network("192.168.0.0/24")
    if net.prefixlen < 24:
        net = ipaddress.ip_network("192.168.0.0/24")
    # Gentle ping sweep only inside configured /24 to populate ARP cache.
    for ip in list(net.hosts())[:254]:
        run_safe(["bash", "-lc", f"ping -c 1 -W 1 {ip} >/dev/null 2>&1 || true"], timeout=2)
    devices = devices_from_neigh(update_store=True)
    return {"time": datetime.utcnow().isoformat(), "subnet": str(net), "devices": devices}


def rename_device(device_id: str, name: str) -> dict[str, Any]:
    known = _read_known_devices()
    if device_id not in known:
        raise KeyError(device_id)
    known[device_id]["name"] = name[:80]
    _write_known_devices(known)
    return known[device_id]


def mark_known(device_id: str) -> dict[str, Any]:
    known = _read_known_devices()
    if device_id not in known:
        raise KeyError(device_id)
    known[device_id]["known"] = True
    _write_known_devices(known)
    return known[device_id]

