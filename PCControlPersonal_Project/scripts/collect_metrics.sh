#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="${PROJECT_DIR:-/opt/pcmanager}"
VENV="/opt/pcmanager/venv"

cd "$PROJECT_DIR"
if [ -x "$VENV/bin/python" ]; then
  "$VENV/bin/python" - <<'PY'
from backend.app.database import SessionLocal
from backend.app.api.monitor_routes import compute_health_score
from backend.app.services.metrics_service import collect_metric

db = SessionLocal()
try:
    health = compute_health_score(db)
    item = collect_metric(health["score"])
    print({"ok": True, "time": item.get("time"), "health_score": health.get("score")})
finally:
    db.close()
PY
else
  python3 - <<'PY'
from backend.app.database import SessionLocal
from backend.app.api.monitor_routes import compute_health_score
from backend.app.services.metrics_service import collect_metric

db = SessionLocal()
try:
    health = compute_health_score(db)
    item = collect_metric(health["score"])
    print({"ok": True, "time": item.get("time"), "health_score": health.get("score")})
finally:
    db.close()
PY
fi
