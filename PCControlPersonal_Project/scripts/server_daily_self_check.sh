#!/usr/bin/env bash
set -u

PROJECT_DIR="${PROJECT_DIR:-/home/pc/PCControlPersonal_Project}"
ENV_FILE="${PCMANAGER_ENV_FILE:-/etc/pcmanager/pcmanager.env}"
REPORT_DIR="$PROJECT_DIR/reports"
DATE_STAMP="$(date +%F)"
TIME_STAMP="$(date '+%F %T %Z')"
REPORT_PATH="$REPORT_DIR/server_self_check_${DATE_STAMP}.txt"

mkdir -p "$REPORT_DIR"

if [[ -f "$PROJECT_DIR/tools/doctor.py" ]]; then
  python3 "$PROJECT_DIR/tools/doctor.py" >/dev/null 2>&1 || true
fi

read_env_value() {
  local key="$1"
  if [[ ! -r "$ENV_FILE" ]]; then
    return 0
  fi
  grep -E "^[[:space:]]*${key}[[:space:]]*=" "$ENV_FILE" 2>/dev/null \
    | tail -n 1 \
    | sed -E "s/^[[:space:]]*${key}[[:space:]]*=[[:space:]]*//; s/^['\\\"]//; s/['\\\"]$//"
}

mask_secrets() {
  sed -E \
    -e 's/[0-9]{8,12}:[A-Za-z0-9_-]{20,}/[MASKED_TELEGRAM_TOKEN]/g' \
    -e 's/(TELEGRAM_BOT_TOKEN|SERVER_ACCESS_KEY|ADMIN_TOKEN|JWT_SECRET|AGENT_BOOTSTRAP_TOKEN)=.*/\1=[MASKED]/g' \
    -e 's/(Bearer|X-Server-Access-Key:|X-PCManager-Key:) [A-Za-z0-9._~+\/=-]+/\1 [MASKED]/g'
}

collect() {
  local title="$1"
  shift
  echo
  echo "===== ${title} ====="
  "$@" 2>&1 | mask_secrets
}

contains_problem_lines() {
  grep -Eai 'ERROR|WARNING|Traceback|Exception|failed|disabled|not configured' || true
}

server_active="$(systemctl is-active pcmanager-server 2>/dev/null || true)"
bot_active="$(systemctl is-active pcmanager-bot 2>/dev/null || true)"
api_ping="$(curl -s --max-time 10 http://127.0.0.1:8765/api/ping 2>/dev/null || true)"
disk_percent="$(df -P / 2>/dev/null | awk 'NR==2 {gsub("%","",$5); print $5}')"
ram_percent="$(free 2>/dev/null | awk '/Mem:/ { if ($2 > 0) printf "%.0f", $3/$2*100; }')"

disk_percent="${disk_percent:-0}"
ram_percent="${ram_percent:-0}"

server_status="OK"
api_status="OK"
bot_status="OK"
disk_status="OK"
ram_status="OK"
suggestions=()

if [[ "$server_active" != "active" ]]; then
  server_status="ERROR"
  suggestions+=("Check pcmanager-server: systemctl status pcmanager-server")
fi

if [[ "$bot_active" != "active" ]]; then
  bot_status="ERROR"
  suggestions+=("Check pcmanager-bot: systemctl status pcmanager-bot")
fi

if ! grep -q '"ok"[[:space:]]*:[[:space:]]*true' <<<"$api_ping"; then
  api_status="ERROR"
  suggestions+=("API does not answer /api/ping. Check server logs and port 8765.")
fi

if [[ "$disk_percent" =~ ^[0-9]+$ ]]; then
  if (( disk_percent >= 90 )); then
    disk_status="ERROR"
    suggestions+=("Disk is almost full. Check storage and backups.")
  elif (( disk_percent >= 80 )); then
    disk_status="WARNING"
    suggestions+=("Disk usage is high. Clean old logs/backups soon.")
  fi
fi

if [[ "$ram_percent" =~ ^[0-9]+$ ]]; then
  if (( ram_percent >= 90 )); then
    ram_status="ERROR"
    suggestions+=("High RAM usage. Check processes: ps aux --sort=-%mem | head")
  elif (( ram_percent >= 80 )); then
    ram_status="WARNING"
    suggestions+=("RAM usage is high. Watch it.")
  fi
fi

server_log="$(journalctl -u pcmanager-server -n 80 --no-pager 2>/dev/null | mask_secrets)"
bot_log="$(journalctl -u pcmanager-bot -n 80 --no-pager 2>/dev/null | mask_secrets)"
log_matches="$(printf '%s\n%s\n' "$server_log" "$bot_log" | contains_problem_lines | head -n 80)"
log_problem_count="$(printf '%s\n' "$log_matches" | sed '/^[[:space:]]*$/d' | wc -l | tr -d ' ')"

if [[ "$log_problem_count" != "0" ]]; then
  suggestions+=("Logs contain warnings/errors. See LOG MATCHES.")
fi

overall="OK"
if [[ "$server_status" == "ERROR" || "$api_status" == "ERROR" || "$bot_status" == "ERROR" || "$disk_status" == "ERROR" || "$ram_status" == "ERROR" ]]; then
  overall="ERROR"
elif [[ "$disk_status" == "WARNING" || "$ram_status" == "WARNING" || "$log_problem_count" != "0" ]]; then
  overall="WARNING"
fi

if [[ "${#suggestions[@]}" -eq 0 ]]; then
  suggestions+=("No urgent issues. Server looks normal.")
fi

send_telegram_summary() {
  local token owner text response
  token="$(read_env_value TELEGRAM_BOT_TOKEN)"
  owner="$(read_env_value TELEGRAM_OWNER_ID)"
  if [[ -z "$owner" ]]; then
    owner="$(read_env_value TELEGRAM_ALLOWED_USER_IDS | cut -d',' -f1 | tr -d ' ')"
  fi
  if [[ -z "$token" || -z "$owner" || "$owner" == "0" ]]; then
    return 0
  fi

  text="PC Manager daily check
OVERALL: $overall
SERVER: $server_status
API: $api_status
BOT: $bot_status
DISK: $disk_status (${disk_percent}%)
RAM: $ram_status (${ram_percent}%)
LOG ERRORS: $log_problem_count
Report: $REPORT_PATH"

  response="$(curl -s --max-time 15 -X POST "https://api.telegram.org/bot${token}/sendMessage" \
    --data-urlencode "chat_id=${owner}" \
    --data-urlencode "text=${text}" 2>&1 | mask_secrets || true)"
  if ! grep -q '"ok"[[:space:]]*:[[:space:]]*true' <<<"$response"; then
    echo "Telegram report send failed: $response" | mask_secrets >> "$REPORT_DIR/server_self_check_telegram_errors.log"
  fi
}

{
  echo "PC Manager Server Self Check"
  echo "Generated: $TIME_STAMP"
  echo "Project: $PROJECT_DIR"
  echo
  echo "SUMMARY"
  echo "OVERALL: $overall"
  echo "SERVER: $server_status"
  echo "API: $api_status"
  echo "BOT: $bot_status"
  echo "DISK: $disk_status (${disk_percent}%)"
  echo "RAM: $ram_status (${ram_percent}%)"
  echo "LOG ERRORS: $log_problem_count"
  echo
  echo "SUGGESTIONS"
  for item in "${suggestions[@]}"; do
    echo "- $item"
  done
  collect "HOSTNAME -I" hostname -I
  collect "UPTIME" uptime
  collect "DF -H" df -h
  collect "FREE -H" free -h
  echo
  echo "===== SYSTEMD ====="
  echo "pcmanager-server: $server_active"
  echo "pcmanager-bot: $bot_active"
  echo
  echo "===== API PING ====="
  printf '%s\n' "$api_ping" | mask_secrets
  echo
  echo "===== LOG MATCHES ====="
  printf '%s\n' "$log_matches"
  echo
  echo "===== PCMANAGER-SERVER LOG LAST 80 ====="
  printf '%s\n' "$server_log"
  echo
  echo "===== PCMANAGER-BOT LOG LAST 80 ====="
  printf '%s\n' "$bot_log"
} > "$REPORT_PATH"

echo "Report saved: $REPORT_PATH"
echo "OVERALL: $overall"
echo "SERVER: $server_status | API: $api_status | BOT: $bot_status | DISK: $disk_status | RAM: $ram_status | LOG ERRORS: $log_problem_count"

send_telegram_summary

if [[ "$overall" == "ERROR" ]]; then
  exit 2
fi
if [[ "$overall" == "WARNING" ]]; then
  exit 1
fi
exit 0
