from __future__ import annotations

import json
import os
import re
import subprocess
from collections import defaultdict
from datetime import datetime
from pathlib import Path


PROJECT_ROOT = Path("/home/pc/PCControlPersonal_Project")
REPORT_DIR = Path(os.getenv("PCMANAGER_REPORT_DIR", "/var/lib/pcmanager/reports"))
REPORT_DIR.mkdir(parents=True, exist_ok=True)

PATTERNS = [
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
    r"\bstatus_code=401\b",
    r"\bstatus_code=403\b",
    r"\bstatus_code=404\b",
    r"\bstatus_code=500\b",
]


def run(command: list[str], timeout: int = 25) -> str:
    try:
        proc = subprocess.run(command, text=True, capture_output=True, timeout=timeout)
        return (proc.stdout + proc.stderr).strip()
    except Exception as exc:
        return str(exc)


def categorize(line: str) -> str:
    low = line.lower()
    if "pcmanager-bot" in low or "telegram" in low or "bot" in low:
        return "bot"
    if "uvicorn" in low or "fastapi" in low or "pcmanager-server" in low:
        return "server"
    if "websocket" in low or "/ws/" in low:
        return "websocket"
    if "agent" in low:
        return "agent"
    if "401" in low or "403" in low or "invalid token" in low:
        return "config"
    if "connection refused" in low or "timeout" in low:
        return "api"
    return "system"


def recommendation(line: str) -> str:
    low = line.lower()
    if "disabled" in low or "not configured" in low:
        return "Проверь TELEGRAM_BOT_ENABLED, TELEGRAM_BOT_TOKEN, TELEGRAM_ALLOWED_USER_IDS и перезапусти bot service."
    if "connection refused" in low or "/api/ping" in low:
        return "Проверь pcmanager-server, порт 8765 и journalctl -u pcmanager-server."
    if "permission denied" in low:
        return "Проверь владельца/права файла или sudoers для строго разрешённой команды."
    if "address already in use" in low or "port already" in low:
        return "Найди занятый порт: ss -tulpn | grep 8765."
    if "no module named" in low:
        return "Активируй venv и установи зависимости: /opt/pcmanager/venv/bin/python -m pip install -r requirements.txt."
    if "403" in low or "invalid token" in low:
        return "Проверь access key/agent token, но не выводи секреты в лог."
    if "404" in low:
        return "Проверь URL endpoint и версию frontend/backend."
    if "500" in low or "traceback" in low:
        return "Открой полный traceback в journalctl и проверь последнюю изменённую функцию."
    return "Проверь соответствующий service status и последние логи journalctl."


def collect_logs() -> list[str]:
    chunks = [
        run(["journalctl", "-u", "pcmanager-server", "--since", "5 minutes ago", "-n", "250", "--no-pager"]),
        run(["journalctl", "-u", "pcmanager-bot", "--since", "5 minutes ago", "-n", "250", "--no-pager"]),
    ]
    return "\n".join(chunks).splitlines()


def main() -> int:
    findings = []
    grouped: dict[str, list[dict]] = defaultdict(list)
    for line in collect_logs():
        if any(re.search(pattern, line, re.IGNORECASE) for pattern in PATTERNS):
            item = {"line": line[-1000:], "recommendation": recommendation(line)}
            category = categorize(line)
            grouped[category].append(item)
            findings.append({"category": category, **item})

    status = "OK" if not findings else ("ERROR" if any("ERROR" in item["line"] or "Traceback" in item["line"] for item in findings) else "WARNING")
    report = {
        "time": datetime.utcnow().isoformat(),
        "status": status,
        "summary": f"{len(findings)} log issue(s) found" if findings else "No important log issues found",
        "groups": grouped,
        "findings": findings[-120:],
    }
    stamp = datetime.utcnow().strftime("%Y-%m-%d_%H-%M")
    for path in [REPORT_DIR / "log_latest.json", REPORT_DIR / f"log_{stamp}.json"]:
        path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    lines = [
        "PC Control Personal Log Analyzer",
        f"Time: {report['time']}",
        f"Status: {status}",
        f"Summary: {report['summary']}",
        "",
        "Groups:",
        *[f"- {key}: {len(value)}" for key, value in grouped.items()],
        "",
        "Findings:",
        *[f"- [{item['category']}] {item['line']}\n  Fix: {item['recommendation']}" for item in findings[-50:]],
    ]
    for path in [REPORT_DIR / "log_latest.txt", REPORT_DIR / f"log_{stamp}.txt"]:
        path.write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines))
    return 0 if status in {"OK", "WARNING"} else 2


if __name__ == "__main__":
    raise SystemExit(main())
