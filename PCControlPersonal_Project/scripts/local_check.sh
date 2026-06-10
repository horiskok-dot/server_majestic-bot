#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="${PROJECT_DIR:-/home/pc/PCControlPersonal_Project}"
VENV_PY="${VENV_PY:-/opt/pcmanager/venv/bin/python}"
ENV_FILE="${PCMANAGER_ENV_FILE:-/etc/pcmanager/pcmanager.env}"
REPORT_DIR="${PCMANAGER_REPORT_DIR:-/var/lib/pcmanager/reports}"
mkdir -p "$REPORT_DIR"

export PCMANAGER_ENV_FILE="$ENV_FILE"

cd "$PROJECT_DIR"
"$VENV_PY" tools/doctor.py || true
"$VENV_PY" tools/log_analyzer.py || true

STATUS="UNKNOWN"
SUMMARY="No report"
if [ -f "$REPORT_DIR/latest.json" ]; then
  STATUS=$("$VENV_PY" - <<'PY'
import json
from pathlib import Path
import os
data=json.loads(Path(os.getenv("PCMANAGER_REPORT_DIR", "/var/lib/pcmanager/reports"), "latest.json").read_text(encoding="utf-8"))
print(data.get("status","UNKNOWN"))
PY
)
  SUMMARY=$("$VENV_PY" - <<'PY'
import json
from pathlib import Path
import os
data=json.loads(Path(os.getenv("PCMANAGER_REPORT_DIR", "/var/lib/pcmanager/reports"), "latest.json").read_text(encoding="utf-8"))
print(data.get("summary","No summary"))
PY
)
fi

NOTIFY_OK="$(grep -E '^LOCAL_CHECK_NOTIFY_OK=' "$ENV_FILE" 2>/dev/null | tail -n1 | cut -d= -f2- | tr '[:upper:]' '[:lower:]' || true)"
if [ "$STATUS" != "OK" ] || [ "$NOTIFY_OK" = "true" ]; then
  "$VENV_PY" - <<'PY' || true
import os
import json
from pathlib import Path
import sys

sys.path.insert(0, "/home/pc/PCControlPersonal_Project")
from backend.app.services.notify_service import telegram_notify

path = Path(os.getenv("PCMANAGER_REPORT_DIR", "/var/lib/pcmanager/reports"), "latest.json")
data = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
checks = data.get("checks", {})
text = "\n".join([
    "PC Manager Local Check",
    f"Status: {data.get('status', 'UNKNOWN')}",
    f"Server: {checks.get('pcmanager_server', '-')}",
    f"Bot: {checks.get('pcmanager_bot', '-')}",
    f"API: {checks.get('api_ping', '-')}",
    f"Disk: {checks.get('disk_root', '-')}",
    f"Issues: {len(data.get('issues', []))}",
    f"Report: {os.getenv('PCMANAGER_REPORT_DIR', '/var/lib/pcmanager/reports')}/latest.txt",
])
telegram_notify(text)
PY
fi

echo "Local check finished: $STATUS - $SUMMARY"
