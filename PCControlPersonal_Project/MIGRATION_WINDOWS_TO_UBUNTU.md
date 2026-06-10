# Миграция сервера с Windows на Ubuntu Server 24.04 LTS

## Что было на Windows

- Сервер запускался вручную через `.bat`, `.exe` или Python.
- Конфиг, база и логи часто лежали рядом с кодом.
- Telegram-бот мог запускаться внутри одного процесса сервера.
- Windows-агент оставался отдельной программой на ПК.

## Что стало на Ubuntu

- Backend запускается как `pcmanager-server.service`.
- Telegram-бот запускается как `pcmanager-bot.service`.
- Код лежит в `/opt/pcmanager`.
- Конфиг лежит в `/etc/pcmanager/pcmanager.env` и `/etc/pcmanager/config.json`.
- SQLite-база лежит в `/var/lib/pcmanager/server.db`.
- Логи приложения лежат в `/var/log/pcmanager`.
- Логи сервисов смотрятся через `journalctl`.

## Главные изменённые файлы

- `backend/app/config.py` читает Linux-конфиги и Linux-пути.
- `backend/app/main.py` запускает FastAPI, REST API, WebSocket, rate limit и `/ws/agent`.
- `backend/app/bot/runner.py` нужен для отдельного bot-service.
- `backend/app/bot/telegram_bot.py` работает как личный бот только для разрешённых Telegram ID.
- `backend/app/api/system_routes.py` содержит `/api/status`, `/api/agents`, `/api/tasks`, `/api/logs`.
- `backend/app/services/task_service.py` содержит очередь задач, `request_id`, timeout и safe retry.
- `backend/app/database.py` добавляет лёгкую SQLite-миграцию старых баз.
- `pc-agent/agent.py` подключается к Linux-серверу по HTTP/WebSocket.
- `systemd/*.service` добавляет автозапуск.
- `scripts/*.sh` добавляет управление через systemctl/journalctl.
- `install_ubuntu.sh` устанавливает проект на Ubuntu.

## Как перенести config

1. На Ubuntu открой:

```bash
sudo nano /etc/pcmanager/pcmanager.env
```

2. Перенеси значения:

```env
TELEGRAM_BOT_TOKEN=...
TELEGRAM_ALLOWED_USER_IDS=8059251932
TELEGRAM_OWNER_ID=8059251932
ADMIN_TOKEN=...
SERVER_ACCESS_KEY=...
AGENT_BOOTSTRAP_TOKEN=...
BASE_PUBLIC_URL=http://SERVER_IP:8765
```

3. Перезапусти:

```bash
sudo systemctl restart pcmanager-server pcmanager-bot
```

## Как перенести базу и логи

Если старая SQLite-база совместима:

```bash
sudo systemctl stop pcmanager-server pcmanager-bot
sudo cp server.db /var/lib/pcmanager/server.db
sudo chown pcmanager:pcmanager /var/lib/pcmanager/server.db
sudo systemctl start pcmanager-server pcmanager-bot
```

Логи можно перенести так:

```bash
sudo cp *.log /var/log/pcmanager/
sudo chown pcmanager:pcmanager /var/log/pcmanager/*
```

При первом запуске сервер аккуратно добавит недостающие SQLite-колонки для задач.

## Как запустить

```bash
sudo bash install_ubuntu.sh
sudo systemctl status pcmanager-server pcmanager-bot
```

## Как проверить

```bash
curl http://127.0.0.1:8765/api/ping
curl -H "X-Server-Access-Key: SERVER_ACCESS_KEY" http://127.0.0.1:8765/api/status
sudo journalctl -u pcmanager-server -n 100 --no-pager
sudo journalctl -u pcmanager-bot -n 100 --no-pager
```

## Как подключить Windows-агента к Linux-серверу

На Windows:

```bat
set SERVER_URL=http://SERVER_IP:8765
set SERVER_WS_URL=ws://SERVER_IP:8765/ws/agent
set AGENT_BOOTSTRAP_TOKEN=AGENT_BOOTSTRAP_TOKEN_FROM_SERVER
python pc-agent\agent.py
```

После первого запуска агент сохранит свой token в `agent_state.json`. Если меняешь сервер или токены, удали старый `agent_state.json` и зарегистрируй агент заново.
## Дополнение: Web UI/PWA и diagnostics

После переноса серверная часть остаётся на Ubuntu, Windows-логика остаётся только в `pc-agent/`.

Новые Linux-компоненты:

- `tools/doctor.py` — локальная диагностика сервисов, API, env, диска и логов.
- `systemd/pcmanager-daily-check.service`
- `systemd/pcmanager-daily-check.timer`
- `backend/app/web/manifest.json`
- `backend/app/web/service-worker.js`

Android-приложение на этом этапе не является основным интерфейсом. Основной мобильный путь — Web UI как PWA:

## Home server additions

После миграции сервер дополнен домашними функциями:

- Web UI Dashboard: статус сервера, CPU/RAM/disk, LAN speed, Telegram bot, Windows Agent, errors, backup, diagnostics.
- File Manager: безопасная работа только внутри `/data`.
- Backup Center: архивы в `/data/backups`.
- Media Server: фильмы, музыка и фото в `/data/media`.
- Local Doctor: `tools/doctor.py`.
- Log Analyzer: `tools/log_analyzer.py`.
- Daily local check: `pcmanager-local-check.timer` в 10:00 и 18:00.

OpenAI API удалён из плана и не нужен. Проверки бесплатные и локальные.

Новые Linux-папки:

```text
/data/files
/data/backups
/data/screenshots
/data/uploads
/data/media/movies
/data/media/music
/data/media/photos
```

Проверка:

```bash
curl http://127.0.0.1:8765/api/home/status
curl http://127.0.0.1:8765/api/files/storage
bash /home/pc/PCControlPersonal_Project/scripts/local_check.sh
systemctl list-timers | grep pcmanager-local-check
```

```text
http://192.168.0.194:8765/
http://100.91.196.119:8765/  # через Tailscale
```

Секреты остаются только в `/etc/pcmanager/pcmanager.env`; `.env` и реальные токены не переносить в git и не вставлять в отчёты.
