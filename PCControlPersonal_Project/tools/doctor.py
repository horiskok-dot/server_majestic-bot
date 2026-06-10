from __future__ import annotations

import json
import os
import re
import shutil
import socket
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from urllib.request import urlopen


PROJECT_ROOT = Path("/home/pc/PCControlPersonal_Project")
REPORT_DIR = Path(os.getenv("PCMANAGER_REPORT_DIR", "/var/lib/pcmanager/reports"))
ENV_PATH = Path("/etc/pcmanager/pcmanager.env")
REPORT_DIR.mkdir(parents=True, exist_ok=True)


def run(command: list[str], timeout: int = 20) -> tuple[int, str]:
    try:
        proc = subprocess.run(command, text=True, capture_output=True, timeout=timeout)
        return proc.returncode, (proc.stdout + proc.stderr).strip()
    except Exception as exc:
        return 1, str(exc)


def read_env_keys() -> set[str]:
    if not ENV_PATH.exists():
        return set()
    keys: set[str] = set()
    for line in ENV_PATH.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        if value.strip():
            keys.add(key.strip())
    return keys


def http_check(url: str) -> tuple[str, str]:
    try:
        with urlopen(url, timeout=5) as response:
            body = response.read(1200).decode("utf-8", "replace")
            return ("OK" if response.status == 200 else "ERROR", body)
    except Exception as exc:
        return "ERROR", str(exc)


def service_status(name: str) -> str:
    code, out = run(["systemctl", "is-active", name], timeout=6)
    return "OK" if code == 0 and out.strip() == "active" else f"ERROR: {out or 'inactive'}"


def port_status(port: int = 8765) -> str:
    code, out = run(["bash", "-lc", f"ss -tulpn | grep ':{port}' || true"])
    return "OK" if code == 0 and out else f"ERROR: port {port} is not listening"


def tcp_status(host: str, port: int, name: str) -> str:
    try:
        socket.create_connection((host, port), timeout=4).close()
        return "OK"
    except Exception as exc:
        return f"WARNING: {name} failed: {exc}"


def dns_status() -> str:
    try:
        socket.gethostbyname("api.telegram.org")
        return "OK"
    except Exception as exc:
        return f"WARNING: DNS failed: {exc}"


def ethernet_speed() -> str:
    code, out = run(["bash", "-lc", "command -v ethtool >/dev/null && ethtool enp4s0 2>/dev/null | grep 'Speed:' | awk '{print $2}' || true"])
    return out.strip() if code == 0 and out.strip() else "unknown"


def journal_matches(unit: str, lines: int = 120) -> list[str]:
    _, out = run(["journalctl", "-u", unit, "--since", "5 minutes ago", "-n", str(lines), "--no-pager"], timeout=25)
    needles = (
        r"\bERROR\b",
        r"\bWARNING\b",
        r"Traceback",
        r"Exception",
        r"\bfailed\b",
        r"\binactive\b",
        r"\bdead\b",
        r"\btimeout\b",
        r"permission denied",
        r"connection refused",
        r"not configured",
        r"\bdisabled\b",
        r"invalid token",
        r'" 401 ',
        r'" 403 ',
        r'" 404 ',
        r'" 500 ',
    )
    return [line for line in out.splitlines() if any(re.search(item, line, re.IGNORECASE) for item in needles)][-40:]


def compile_backend() -> str:
    if not PROJECT_ROOT.exists():
        return "WARNING: project path missing"
    code, out = run([sys.executable, "-m", "compileall", str(PROJECT_ROOT / "backend")], timeout=60)
    return "OK" if code == 0 else f"ERROR: compile failed: {out[-1000:]}"


def important_files_status() -> dict[str, str]:
    files = [
        "backend/app/main.py",
        "backend/app/config.py",
        "backend/app/bot/telegram_bot.py",
        "pc-agent/agent.py",
        "pc-agent/agent_config.example.json",
        "systemd/pcmanager-server.service",
        "systemd/pcmanager-bot.service",
        "scripts/backup.sh",
        "scripts/update.sh",
    ]
    return {item: ("OK" if (PROJECT_ROOT / item).exists() else "ERROR: missing") for item in files}


def script_permissions() -> dict[str, str]:
    scripts = sorted((PROJECT_ROOT / "scripts").glob("*.sh")) if (PROJECT_ROOT / "scripts").exists() else []
    result: dict[str, str] = {}
    for script in scripts:
        result[script.name] = "OK" if os.access(script, os.X_OK) else "WARNING: not executable"
    return result


def main() -> int:
    env_keys = read_env_keys()
    root_usage = shutil.disk_usage("/")
    data_usage = shutil.disk_usage("/data") if Path("/data").exists() else root_usage
    load1, load5, load15 = os.getloadavg()
    ping_status, ping_body = http_check("http://127.0.0.1:8765/api/ping")
    health_status, health_body = http_check("http://127.0.0.1:8765/api/health")
    health_score_status, health_score_body = http_check("http://127.0.0.1:8765/api/health-score")
    network_status, network_body = http_check("http://127.0.0.1:8765/api/network/status")
    temperature_api_status, temperature_body = http_check("http://127.0.0.1:8765/api/system/temperature")
    required_env = ["ADMIN_TOKEN", "SERVER_ACCESS_KEY", "JWT_SECRET", "AGENT_BOOTSTRAP_TOKEN"]
    optional_env = ["TELEGRAM_BOT_TOKEN", "TELEGRAM_ALLOWED_USER_IDS"]
    missing_required = [key for key in required_env if key not in env_keys]
    missing_optional = [key for key in optional_env if key not in env_keys]
    server_logs = journal_matches("pcmanager-server")
    bot_logs = journal_matches("pcmanager-bot")

    checks = {
        "pcmanager_server": service_status("pcmanager-server"),
        "pcmanager_bot": service_status("pcmanager-bot"),
        "api_ping": ping_status,
        "api_health": health_status,
        "health_score": health_score_status,
        "network_monitor": network_status,
        "temperature_monitor": temperature_api_status,
        "port_8765": port_status(8765),
        "ssh": service_status("ssh"),
        "internet": tcp_status("1.1.1.1", 53, "internet"),
        "dns": dns_status(),
        "env_file": "OK" if ENV_PATH.exists() else "ERROR: env file missing",
        "required_env": "OK" if not missing_required else "ERROR: missing " + ", ".join(missing_required),
        "optional_env": "OK" if not missing_optional else "WARNING: missing " + ", ".join(missing_optional),
        "disk_root": "OK" if root_usage.free / root_usage.total > 0.10 else "WARNING: root disk free below 10%",
        "disk_data": "OK" if data_usage.free / data_usage.total > 0.10 else "WARNING: data disk free below 10%",
        "ram": "OK",
        "cpu_load": "OK" if load1 < (os.cpu_count() or 1) * 2 else "WARNING: high CPU load",
        "ethernet_speed": ethernet_speed(),
        "python_compile_backend": compile_backend(),
    }
    checks.update({f"file:{name}": value for name, value in important_files_status().items()})
    checks.update({f"script:{name}": value for name, value in script_permissions().items()})

    issues = []
    for key, value in checks.items():
        if str(value).startswith(("ERROR", "WARNING")):
            issues.append({"category": "system", "check": key, "message": str(value)})
    for line in server_logs:
        issues.append({"category": "server", "check": "journalctl", "message": line})
    for line in bot_logs:
        issues.append({"category": "bot", "check": "journalctl", "message": line})

    status = "OK"
    if any(str(value).startswith("ERROR") for value in checks.values()):
        status = "ERROR"
    elif issues:
        status = "WARNING"

    suggestions = []
    if ping_status != "OK":
        suggestions.append("API ping не отвечает: проверь pcmanager-server, порт 8765 и journalctl.")
    if missing_required:
        suggestions.append("Заполни обязательные переменные в /etc/pcmanager/pcmanager.env.")
    if root_usage.free / root_usage.total <= 0.10 or data_usage.free / data_usage.total <= 0.10:
        suggestions.append("Мало места на диске: удали старые backups/media/logs.")
    if server_logs or bot_logs:
        suggestions.append("Есть ошибки в journalctl: открой Logs или запусти tools/log_analyzer.py.")
    suggestions.append("Для внешнего доступа используй Tailscale, не открывай SSH/API в интернет.")

    report = {
        "time": datetime.utcnow().isoformat(),
        "status": status,
        "summary": f"{len(issues)} issue(s) found" if issues else "All core checks passed",
        "hostname": socket.gethostname(),
        "ip_addresses": socket.gethostbyname_ex(socket.gethostname())[-1],
        "uptime": run(["uptime", "-p"])[1],
        "checks": checks,
        "issues": issues,
        "suggestions": suggestions,
        "api_ping_body": ping_body,
        "api_health_body": health_body,
        "health_score_body": health_score_body,
        "network_body": network_body,
        "temperature_body": temperature_body,
        "disk": {
            "root": {"total": root_usage.total, "used": root_usage.used, "free": root_usage.free},
            "data": {"total": data_usage.total, "used": data_usage.used, "free": data_usage.free},
        },
        "load": {"load1": load1, "load5": load5, "load15": load15},
    }

    stamp = datetime.utcnow().strftime("%Y-%m-%d_%H-%M")
    for path in [REPORT_DIR / "latest.json", REPORT_DIR / f"{stamp}.json"]:
        path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    lines = [
        "PC Control Personal Local Doctor",
        f"Time: {report['time']}",
        f"Status: {status}",
        f"Summary: {report['summary']}",
        "",
        "Checks:",
        *[f"- {key}: {value}" for key, value in checks.items()],
        "",
        "Issues:",
        *[f"- [{item['category']}] {item['message']}" for item in issues[:80]],
        "",
        "Recommendations:",
        *[f"- {item}" for item in suggestions],
        "",
        "Useful commands:",
        "- curl http://127.0.0.1:8765/api/ping",
        "- sudo systemctl status pcmanager-server --no-pager",
        "- sudo systemctl status pcmanager-bot --no-pager",
        "- sudo journalctl -u pcmanager-server -n 100 --no-pager",
        "- sudo journalctl -u pcmanager-bot -n 100 --no-pager",
    ]
    for path in [REPORT_DIR / "latest.txt", REPORT_DIR / f"{stamp}.txt"]:
        path.write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines))
    return 0 if status in {"OK", "WARNING"} else 2


if __name__ == "__main__":
    raise SystemExit(main())
