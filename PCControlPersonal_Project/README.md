# PC Control Personal Server

Личный сервер для управления только своими Windows-агентами через FastAPI, WebSocket, Telegram-бота, Web UI и Android-приложение. Серверная часть подготовлена для Ubuntu Server 24.04 LTS и запускается как systemd-сервисы.

## Структура

```text
backend/                 FastAPI, REST API, WebSocket, Telegram bot
pc-agent/                Windows PC agent
android-app/             Android-приложение
systemd/                 pcmanager-server.service, pcmanager-bot.service
scripts/                 start/stop/restart/status/logs/update/backup
install_ubuntu.sh        установщик для Ubuntu/Debian
.env.example             пример /etc/pcmanager/pcmanager.env
config.example.json      пример /etc/pcmanager/config.json
requirements.txt         Python-зависимости
```

## Установка на Ubuntu Server 24.04 LTS

Скопируй папку проекта на сервер, например в `/tmp/PCControlPersonal_Project`, потом выполни:

```bash
cd /tmp/PCControlPersonal_Project
sudo bash install_ubuntu.sh
```

Установщик создаёт:

```text
/opt/pcmanager
/etc/pcmanager
/var/log/pcmanager
/var/lib/pcmanager
```

И ставит systemd-сервисы:

```text
pcmanager-server.service
pcmanager-bot.service
```

## Настройка .env

Открой конфиг:

```bash
sudo nano /etc/pcmanager/pcmanager.env
```

Минимум поменяй:

```env
BASE_PUBLIC_URL=http://SERVER_IP:8765
ADMIN_TOKEN=long-admin-login-token
SERVER_ACCESS_KEY=long-api-access-key
JWT_SECRET=long-random-jwt-secret
AGENT_BOOTSTRAP_TOKEN=long-agent-bootstrap-token
TELEGRAM_BOT_TOKEN=your-telegram-bot-token
TELEGRAM_ALLOWED_USER_IDS=YOUR_TELEGRAM_ID
TELEGRAM_OWNER_ID=YOUR_TELEGRAM_ID
LOCAL_ONLY=false
```

После изменения:

```bash
sudo systemctl restart pcmanager-server pcmanager-bot
```

## Запуск и автозапуск

```bash
sudo systemctl enable pcmanager-server pcmanager-bot
sudo systemctl start pcmanager-server pcmanager-bot
sudo systemctl status pcmanager-server pcmanager-bot
```

## Доступ не только дома

Самый безопасный вариант для школы/улицы — Tailscale. Сервер не надо открывать всему интернету и не надо пробрасывать порты на роутере.

На Ubuntu-сервере:

```bash
curl -fsSL https://tailscale.com/install.sh | sh
sudo tailscale up
tailscale ip -4
```

На телефоне установи Tailscale, войди в тот же аккаунт и открывай сайт:

```text
http://TAILSCALE_IP:8765/
```

Для приложения:

```text
Base URL: http://TAILSCALE_IP:8765/
WebSocket: ws://TAILSCALE_IP:8765/ws/status
```

`LOCAL_ONLY=true` разрешает домашние private IP и Tailscale-сеть `100.64.0.0/10`. Если используешь публичный домен/reverse proxy, оставь авторизацию и HTTPS, не открывай API без токена.

## Wake-on-LAN

Сервер может включать другой твой ноут/ПК в этой же сети, если устройство поддерживает Wake-on-LAN и питание не отключено полностью. Сервер не может включить сам себя, если он уже выключен.

В `/etc/pcmanager/pcmanager.env` добавь:

```env
WOL_DEVICES=notebook=AA:BB:CC:DD:EE:FF
WOL_BROADCAST_IP=255.255.255.255
WOL_PORT=9
```

Потом:

```bash
sudo systemctl restart pcmanager-server pcmanager-bot
```

Проверка:

```bash
curl -H "Authorization: Bearer ADMIN_JWT" http://127.0.0.1:8765/api/wol/devices
```

В Telegram:

```text
/wol
/wake notebook
```

Логи:

```bash
sudo journalctl -u pcmanager-server -f
sudo journalctl -u pcmanager-bot -f
```

Готовые скрипты:

```bash
sudo /opt/pcmanager/scripts/start.sh
sudo /opt/pcmanager/scripts/stop.sh
sudo /opt/pcmanager/scripts/restart.sh
sudo /opt/pcmanager/scripts/status.sh
sudo /opt/pcmanager/scripts/logs.sh
sudo /opt/pcmanager/scripts/update.sh
sudo /opt/pcmanager/scripts/backup.sh
```

## Проверка API

```bash
curl http://127.0.0.1:8765/api/ping
curl -H "X-Server-Access-Key: YOUR_SERVER_ACCESS_KEY" http://127.0.0.1:8765/api/status
curl -H "X-Server-Access-Key: YOUR_SERVER_ACCESS_KEY" http://127.0.0.1:8765/api/agents
curl -H "X-Server-Access-Key: YOUR_SERVER_ACCESS_KEY" http://127.0.0.1:8765/api/tasks
curl -H "X-Server-Access-Key: YOUR_SERVER_ACCESS_KEY" http://127.0.0.1:8765/api/logs
curl -H "X-Server-Access-Key: YOUR_SERVER_ACCESS_KEY" http://127.0.0.1:8765/api/server/info
```

Swagger:

```text
http://SERVER_IP:8765/docs
```

Web UI:

```text
http://SERVER_IP:8765/panel
```

## Telegram-бот

Бот работает отдельным сервисом:

```bash
sudo systemctl status pcmanager-bot
sudo journalctl -u pcmanager-bot -f
```

Доступ разрешён только ID из:

```env
TELEGRAM_ALLOWED_USER_IDS=YOUR_TELEGRAM_ID
```

Команды:

```text
/start
/login
/status
/server
/agents
/files
/photos
/screenshots
/videos
/download FILE_ID
/server_screen
/server_webcam
/server_record_video SECONDS
/screenshot AGENT_ID
/processes AGENT_ID
/photo AGENT_ID
/recordvideo AGENT_ID SECONDS
/tasks
/logs
/help
/task AGENT_ID ACTION
/cancel TASK_ID
/retry TASK_ID
```

## Подключение Windows-агента

На Windows-ПК:

```bat
python -m pip install -r pc-agent\requirements.txt
```

```bat
set SERVER_URL=http://SERVER_IP:8765
set SERVER_WS_URL=ws://SERVER_IP:8765/ws/agent
set AGENT_BOOTSTRAP_TOKEN=token_from_/etc/pcmanager/pcmanager.env
set ENABLE_SCREENSHOT=false
set ENABLE_CAMERA=false
set ENABLE_VIDEO_RECORDING=false
python pc-agent\agent.py
```

Агент регистрируется через `AGENT_BOOTSTRAP_TOKEN`, получает отдельный agent token, отправляет `last_seen`, `latency`, `version`, `current_task`, подключается к `/ws/agent` и выполняет только allowlist-задачи.

Разрешённые задачи:

```text
ping
get_system_info
get_process_list
get_disk_info
get_network_info
restart_agent
update_agent
get_screenshot
run_safe_script
```

Произвольный shell по умолчанию выключен. Screenshot работает только если `ENABLE_SCREENSHOT=true` и на сервере, и на агенте.

## Файлы, скриншоты, процессы, камера

Сервер хранит файлы в:

```text
/var/lib/pcmanager/storage/uploads
/var/lib/pcmanager/storage/photos
/var/lib/pcmanager/storage/screenshots
/var/lib/pcmanager/storage/videos
/var/lib/pcmanager/storage/telegram_files
/var/lib/pcmanager/storage/temp
```

Основные API:

```text
GET  /api/server/info
GET  /api/server/network
GET  /api/agents/{agent_id}
GET  /api/agents/{agent_id}/network
POST /api/agents/{agent_id}/screenshot
GET  /api/agents/{agent_id}/processes
POST /api/agents/{agent_id}/processes/refresh
POST /api/agents/{agent_id}/camera/photo
POST /api/agents/{agent_id}/camera/record
POST /api/files/upload
GET  /api/files
GET  /api/files/{file_id}/download
DELETE /api/files/{file_id}
```

Загрузить файл с телефона/API:

```bash
curl -H "Authorization: Bearer JWT_TOKEN" \
  -F "upload=@report.txt" \
  "http://SERVER_IP:8765/api/mobile/files/upload?public_type=upload"
```

Скачать файл:

```bash
curl -H "Authorization: Bearer JWT_TOKEN" \
  -o file.bin \
  "http://SERVER_IP:8765/api/mobile/files/FILE_ID/download"
```

Сделать скриншот агента:

```bash
curl -X POST -H "Authorization: Bearer JWT_TOKEN" \
  "http://SERVER_IP:8765/api/mobile/agents/AGENT_ID/screenshot"
```

Обновить процессы:

```bash
curl -X POST -H "Authorization: Bearer JWT_TOKEN" \
  "http://SERVER_IP:8765/api/mobile/agents/AGENT_ID/processes/refresh"
```

Камера и видео выключены по умолчанию:

```env
ENABLE_CAMERA=false
ENABLE_VIDEO_RECORDING=false
```

Чтобы включить на своих устройствах, включи флаги и на сервере, и на агенте. При видеозаписи агент показывает локальный заметный индикатор `RECORDING`, а действие логируется.

## Скрин экрана и вебка сервера

Флаги в `/etc/pcmanager/pcmanager.env`:

```env
ENABLE_SERVER_SCREENSHOT=true
ENABLE_SERVER_WEBCAM=false
ENABLE_SERVER_WEBCAM_VIDEO=false
MAX_SERVER_WEBCAM_VIDEO_SECONDS=10
```

Скрин экрана сервера:

```bash
curl -X POST -H "Authorization: Bearer JWT_TOKEN" \
  "http://SERVER_IP:8765/api/mobile/server/screenshot"
```

Если Ubuntu Server без GUI, сервер не падает и вернёт понятную ошибку: `На сервере нет активного графического экрана`.

Фото с вебки сервера:

```bash
curl -X POST -H "Authorization: Bearer JWT_TOKEN" \
  "http://SERVER_IP:8765/api/mobile/server/webcam/photo?confirmed=true"
```

Видео с вебки сервера:

```bash
curl -X POST -H "Authorization: Bearer JWT_TOKEN" \
  "http://SERVER_IP:8765/api/mobile/server/webcam/record?duration_seconds=10&confirmed=true"
```

Через Telegram:

```text
/server_screen
/server_webcam
/server_record_video 10
```

Фото/видео с вебки сервера требуют подтверждения кнопкой и логируются. Файлы остаются в:

```text
/var/lib/pcmanager/storage/screenshots/server
/var/lib/pcmanager/storage/photos/server_webcam
/var/lib/pcmanager/storage/videos/server_webcam
```

Токены меняй только в:

```bash
sudo nano /etc/pcmanager/pcmanager.env
sudo systemctl restart pcmanager-server pcmanager-bot
```

## Подключение телефона

В Android-приложении укажи:

```text
Server Base URL: http://SERVER_IP:8765/
WebSocket URL: ws://SERVER_IP:8765/ws/status
Access Key/Admin Token: ADMIN_TOKEN
```

Для доступа не дома лучше использовать Tailscale или ZeroTier:

```text
Server Base URL: http://100.x.x.x:8765/
WebSocket URL: ws://100.x.x.x:8765/ws/status
```

Через домен и HTTPS:

```text
Server Base URL: https://pc.example.com/
WebSocket URL: wss://pc.example.com/ws/status
```

## Reverse proxy

Caddy:

```caddyfile
pc.example.com {
  reverse_proxy 127.0.0.1:8765
}
```

nginx:

```nginx
server {
    listen 443 ssl;
    server_name pc.example.com;

    location / {
        proxy_pass http://127.0.0.1:8765;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

Не открывай сервер в интернет без HTTPS и авторизации.

## Troubleshooting

Проверить сервисы:

```bash
sudo systemctl status pcmanager-server pcmanager-bot
```

Проверить порт:

```bash
ss -lntp | grep 8765
```

Посмотреть последние логи:

```bash
sudo journalctl -u pcmanager-server -n 100 --no-pager
sudo journalctl -u pcmanager-bot -n 100 --no-pager
```

Если Telegram не запускается, проверь `TELEGRAM_BOT_TOKEN` и `TELEGRAM_ALLOWED_USER_IDS`.

Если агент получает `403`, проверь `AGENT_BOOTSTRAP_TOKEN` при регистрации или сохранённый agent token в `agent_state.json`.
## PWA / Mobile Web

The Web UI is also a PWA. Open the panel from the phone:

```text
http://192.168.0.194:8765/
```

For remote access use Tailscale instead of opening SSH/API to the internet:

```text
http://100.91.196.119:8765/
```

Then choose “Add to Home Screen”. The PWA files are served by FastAPI:

- `/manifest.json`
- `/service-worker.js`

## AI Review

AI Review removed: OpenAI API usage was too expensive for this local personal server. There are no OpenAI API calls, no AI timers, and no `OPENAI_API_KEY` / `AI_REVIEW_*` settings in the runtime config.

## Home Server Dashboard

Web UI is the main interface now. Open:

```bash
http://192.168.0.194:8765/
```

Main sections:

- `Dashboard` - server status, CPU/RAM/disk, LAN speed, bot status, agent status, latest errors, latest backup and latest diagnostics report.
- `Files` - safe file manager inside `/data`.
- `Backups` - create, download and delete backups from `/data/backups`.
- `Media` - simple local media library from `/data/media/movies`, `/data/media/music`, `/data/media/photos`.
- `Diagnostics` - free local doctor/log analyzer without OpenAI or paid APIs.
- `Wake` - Wake-on-LAN devices from `.env`.

Dangerous Web UI actions require the admin token/access key and confirmation in the browser.

## Local Diagnostics

Run manually:

```bash
cd /home/pc/PCControlPersonal_Project
bash scripts/local_check.sh
cat tools/reports/latest.txt
```

Reports are saved to:

```text
tools/reports/latest.txt
tools/reports/latest.json
tools/reports/YYYY-MM-DD_HH-MM.txt
tools/reports/YYYY-MM-DD_HH-MM.json
```

Install daily checks at 10:00 and 18:00:

```bash
cd /home/pc/PCControlPersonal_Project
sudo bash scripts/install_local_check_timer.sh
systemctl list-timers | grep pcmanager-local-check
```

If Telegram is configured, warnings/errors are sent to the allowed owner. If Telegram is not configured, reports are only saved locally.

## File Manager And Media

The server keeps user files only under `/data`:

```text
/data/files
/data/backups
/data/screenshots
/data/uploads
/data/media/movies
/data/media/music
/data/media/photos
```

The API blocks path traversal and does not allow access outside `/data`.

## Backup Center

Backups are stored in `/data/backups`.

Manual backup:

```bash
cd /home/pc/PCControlPersonal_Project
bash scripts/backup.sh
```

Web UI can create:

- project backup
- config backup
- full backup

## Windows Agent

Agent config example is `pc-agent/agent_config.example.json`.

Recommended server values:

```json
{
  "SERVER_URL": "http://192.168.0.194:8765",
  "SERVER_WS_URL": "ws://192.168.0.194:8765/ws/agent"
}
```

Allowed restart apps are controlled by `allowed_apps`. Arbitrary shell and arbitrary PowerShell are disabled by design.

## Network Monitor, Maintenance, Health And Metrics

The Web UI also has server-care pages:

- `Network` shows LAN speed from `ethtool`, router ping, Google/Cloudflare ping, DNS/internet status, RX/TX traffic from `/proc/net/dev`, and LAN devices from `ip neigh`.
- `Maintenance` runs safe local maintenance: clean old logs, clean old backups, check Ubuntu updates, restart backend, restart bot, and run full local check. POST actions require the access key.
- `Health` calculates `Server Health` from services, API ping, network, disk, temperature, backups, log errors and agent status.
- `Metrics` stores history in `/var/lib/pcmanager/metrics.jsonl` and draws lightweight charts.
- `Events` stores timeline events in `/var/lib/pcmanager/events.jsonl`.
- `Reports` shows local doctor reports from `/var/lib/pcmanager/reports`.

Useful checks:

```bash
curl http://127.0.0.1:8765/api/network/status
curl http://127.0.0.1:8765/api/system/temperature
curl http://127.0.0.1:8765/api/health-score
curl http://127.0.0.1:8765/api/metrics/latest
curl http://127.0.0.1:8765/api/events/latest
```

Metrics timer:

```bash
sudo systemctl enable --now pcmanager-metrics-collector.timer
systemctl list-timers | grep pcmanager
```

Optional temperature tools:

```bash
sudo apt install lm-sensors smartmontools -y
```

Retention and notifications are configured in `/etc/pcmanager/pcmanager.env`:

```env
TEMP_WARNING_C=85
TEMP_CRITICAL_C=90
LOG_RETENTION_DAYS=14
BACKUP_RETENTION_DAYS=30
BACKUP_KEEP_LAST=5
METRICS_RETENTION_DAYS=30
METRICS_COLLECT_INTERVAL_MIN=5
NETWORK_SCAN_SUBNET=192.168.0.0/24
TELEGRAM_NOTIFY_EVENTS=true
TELEGRAM_NOTIFY_INFO=false
```
## Windows Agent Setup

Windows Agent lives in `pc-agent/` and connects only to your personal PC Control Personal server.

Server URLs for the current home server:

```text
server_base_url: http://192.168.0.193:8765
websocket_url: ws://192.168.0.193:8765/ws/status
```

Setup on Windows:

```bat
cd pc-agent
install_agent_windows.bat
notepad agent_config.json
run_agent.bat
```

In `pc-agent/agent_config.json`, replace:

```json
"access_key": "CHANGE_ME"
```

with your server access key from `/etc/pcmanager/pcmanager.env`. Do not paste this key into chat, logs, screenshots, or Git.

The agent supports only safe allowlisted tasks:

```text
ping
system_info
screenshot
process_list
disk_info
temperature
agent_logs
restart_allowed_app
```

`restart_allowed_app` can restart only apps listed in `allowed_apps`. The agent does not run arbitrary shell, PowerShell, cmd commands, or unknown programs.

How to check it:

```bat
pc-agent\run_agent.bat
type pc-agent\logs\agent.log
```

Then open the Web UI:

```text
http://192.168.0.193:8765/
```

Go to `PC Agent`. If the agent is offline, check:

```text
pc-agent/agent_config.json
server_base_url
websocket_url
access_key
pc-agent/logs/agent.log
```

Backend endpoints used by the agent:

```text
GET  /api/ping
POST /api/agents/{agent_id}/heartbeat
POST /api/agents/{agent_id}/status
GET  /api/agents/{agent_id}/tasks/next
POST /api/tasks/{task_id}/status
POST /api/tasks/{task_id}/result
POST /api/agents/{agent_id}/screenshot/upload
```
