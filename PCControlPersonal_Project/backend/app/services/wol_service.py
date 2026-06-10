import re
import socket
from dataclasses import dataclass

from ..config import get_settings


MAC_RE = re.compile(r"^(?:[0-9a-fA-F]{2}[:-]){5}[0-9a-fA-F]{2}$|^[0-9a-fA-F]{12}$")


@dataclass(frozen=True)
class WolDevice:
    name: str
    mac: str


def normalize_mac(mac: str) -> str:
    value = mac.strip().replace("-", ":").lower()
    if len(value) == 12 and ":" not in value:
        value = ":".join(value[i : i + 2] for i in range(0, 12, 2))
    if not MAC_RE.match(value):
        raise ValueError("Неверный MAC-адрес")
    return value


def list_wol_devices() -> list[WolDevice]:
    settings = get_settings()
    devices: list[WolDevice] = []
    for name, mac in settings.wol_device_map.items():
        try:
            devices.append(WolDevice(name=name, mac=normalize_mac(mac)))
        except ValueError:
            continue
    return devices


def build_magic_packet(mac: str) -> bytes:
    clean = normalize_mac(mac).replace(":", "")
    mac_bytes = bytes.fromhex(clean)
    return b"\xff" * 6 + mac_bytes * 16


def wake_device(name: str) -> dict:
    settings = get_settings()
    devices = {device.name: device for device in list_wol_devices()}
    device = devices.get(name)
    if not device:
        raise KeyError("Устройство не найдено в WOL_DEVICES")

    packet = build_magic_packet(device.mac)
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.settimeout(3)
        sock.sendto(packet, (settings.wol_broadcast, int(settings.wol_port)))

    return {
        "ok": True,
        "device": device.name,
        "mac": device.mac,
        "broadcast": settings.wol_broadcast,
        "port": settings.wol_port,
    }
