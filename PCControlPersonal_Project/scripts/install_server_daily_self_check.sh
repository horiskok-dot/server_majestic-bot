#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="${PROJECT_DIR:-/home/pc/PCControlPersonal_Project}"
SCRIPT_PATH="$PROJECT_DIR/scripts/server_daily_self_check.sh"
CRON_MARKER="# PCMANAGER_SERVER_DAILY_SELF_CHECK"
CRON_LINE="0 10 * * * $SCRIPT_PATH >/dev/null 2>&1 $CRON_MARKER"

if [[ ! -f "$SCRIPT_PATH" ]]; then
  echo "Script not found: $SCRIPT_PATH" >&2
  exit 1
fi

chmod +x "$SCRIPT_PATH"
mkdir -p "$PROJECT_DIR/reports"

tmp="$(mktemp)"
crontab -l 2>/dev/null | grep -v "$CRON_MARKER" > "$tmp" || true
echo "$CRON_LINE" >> "$tmp"
crontab "$tmp"
rm -f "$tmp"

echo "Installed daily server self-check:"
echo "$CRON_LINE"
echo "Reports: $PROJECT_DIR/reports"
