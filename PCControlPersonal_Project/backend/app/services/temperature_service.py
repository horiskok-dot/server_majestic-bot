from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import psutil

from ..config import get_settings
from .command_service import run_safe


def _thermal_zone_values() -> list[dict[str, Any]]:
    values: list[dict[str, Any]] = []
    for zone in Path("/sys/class/thermal").glob("thermal_zone*"):
        try:
            raw = (zone / "temp").read_text(encoding="utf-8").strip()
            label = (zone / "type").read_text(encoding="utf-8").strip() if (zone / "type").exists() else zone.name
            current = float(raw) / 1000 if float(raw) > 1000 else float(raw)
            values.append({"name": label, "current_c": round(current, 1), "source": "thermal_zone"})
        except Exception:
            continue
    return values


def _psutil_values() -> list[dict[str, Any]]:
    values: list[dict[str, Any]] = []
    try:
        for group, entries in psutil.sensors_temperatures(fahrenheit=False).items():
            for entry in entries:
                if entry.current is not None:
                    values.append({"name": entry.label or group, "current_c": round(float(entry.current), 1), "source": "psutil"})
    except Exception:
        pass
    return values


def _sensors_values() -> list[dict[str, Any]]:
    code, out = run_safe(["bash", "-lc", "command -v sensors >/dev/null && sensors || true"], timeout=8)
    if code != 0 or not out:
        return []
    values: list[dict[str, Any]] = []
    for line in out.splitlines():
        match = re.search(r"([A-Za-z0-9 _.-]+):\s+\+?([0-9]+(?:\.[0-9]+)?)\s*°?C", line)
        if match:
            values.append({"name": match.group(1).strip(), "current_c": round(float(match.group(2)), 1), "source": "sensors"})
    return values


def temperature_status() -> dict[str, Any]:
    settings = get_settings()
    readings = _psutil_values() + _thermal_zone_values() + _sensors_values()
    seen: set[tuple[str, float]] = set()
    unique: list[dict[str, Any]] = []
    for item in readings:
        key = (str(item.get("name")), float(item.get("current_c") or 0))
        if key not in seen:
            unique.append(item)
            seen.add(key)
    max_c = max([float(x["current_c"]) for x in unique], default=None)
    tools_missing = not unique
    if max_c is None:
        status = "warning"
    elif max_c >= settings.temp_critical_c:
        status = "critical"
    elif max_c >= settings.temp_warning_c:
        status = "warning"
    else:
        status = "ok"
    return {
        "status": status,
        "max_c": round(max_c, 1) if max_c is not None else None,
        "warning_c": settings.temp_warning_c,
        "critical_c": settings.temp_critical_c,
        "readings": unique[:30],
        "tools_missing": tools_missing,
        "install_hint": "sudo apt install lm-sensors smartmontools -y" if tools_missing else "",
    }

