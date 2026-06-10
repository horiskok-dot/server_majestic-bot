# PC Control Personal — Project Handoff

Сгенерировано: `2026-04-26 22:20:20`  
Проект: `/home/pc/PCControlPersonal_Project`

> Секреты не выводятся. `TELEGRAM_BOT_TOKEN`, `SERVER_ACCESS_KEY`, пароли, access keys и Telegram user IDs показываются только как `[HIDDEN]`.

## 1. Краткое описание проекта

PC Control Personal — это личный домашний сервер для управления моими устройствами. Сервер работает на Ubuntu Server, backend написан на FastAPI. В проекте есть Telegram-бот, Windows-агент, Android-приложение, WebSocket и REST API.

Проект предназначен только для личных устройств владельца: мониторинг, логи, задачи, статусы, скриншоты, файлы, медиа и мобильный доступ. Функции скрытого доступа, взлома, брутфорса, дианона или доступа к чужим системам не входят в проект и не должны добавляться.

## 2. Текущая инфраструктура

Ubuntu server:
- OS: Ubuntu Server 24.04 LTS
- Hostname: `home`
- User: `pc`
- LAN IP: `192.168.0.194`
- Tailscale IP, если включён: `100.91.196.119`
- Project path: `/home/pc/PCControlPersonal_Project`
- Installed path: `/opt/pcmanager`
- Config path: `/etc/pcmanager/pcmanager.env`
- Logs: `journalctl` / systemd и `/var/log/pcmanager`

Network:
- Main router → Mercusys MS105G gigabit switch → Ubuntu server / Windows PC
- Ethernet interface: `enp4s0`
- Link check: `проверить командой sudo ethtool enp4s0`
- Server API port: `8765`
- Current hostname IP output: `192.168.0.194 100.91.196.119 fd7a:115c:a1e0::9537:c477`

Hardware:
- ASUS laptop as server
- CPU: Intel Pentium 2020M 2.40 GHz
- RAM: 8 GB DDR3
- SSD: Kingston 240 GB
- HDD: around 700 GB

## 3. Что уже сделано

- Ubuntu Server установлен.
- OpenSSH включён.
- SSH работает: `ssh pc@192.168.0.194`.
- Проект перенесён с Windows на Ubuntu через SCP.
- Исходный проект лежит в `/home/pc/PCControlPersonal_Project`.
- Installed/runtime копия лежит в `/opt/pcmanager`.
- `install_ubuntu.sh` был подготовлен/использован для Linux-структуры.
- Создан Python venv: `/opt/pcmanager/venv`.
- Установлены Python-зависимости из `requirements.txt`.
- Установлены systemd services.
- `pcmanager-server.service` сейчас: `active`.
- `pcmanager-bot.service` сейчас: `active`.
- FastAPI/Uvicorn слушает `0.0.0.0:8765`.
- `/api/ping` отвечает: `{"ok":true,"app":"PC Control Personal Server","version":"1.0.0","time":"2026-04-26T19:20:20.256223"}`.
- `/api/health` отвечает: `{"status":"ok","app":"PC Control Personal Server","version":"1.0.0","time":"2026-04-26T19:20:20.321622"}`.
- Сеть через Mercusys MS105G настроена под gigabit-схему.
- Создан технический отчёт: `TECHNICAL_FILES_REPORT.md`.
- Daily self-check: `CHECK: есть скрипты daily self-check, нужно проверить cron/report`.

## 4. Что сейчас работает

- LAN network: OK
- SSH: OK
- Ubuntu server: OK
- FastAPI backend: OK, если `pcmanager-server` active и `/api/ping` отвечает
- API ping: OK по текущей проверке, если ответ выше не пустой
- systemd server service: `active`
- Telegram bot service: `active/running`
- Windows agent: needs connection/configuration
- Android app: needs server URL configuration
- Web panel: needs manual check in browser
- Daily diagnostics: `CHECK: есть скрипты daily self-check, нужно проверить cron/report`

## 5. Что сейчас не настроено или требует внимания

### 1. Telegram bot

`pcmanager-bot.service` установлен. Если он `inactive/dead` или Telegram не отвечает, причина обычно одна из этих:
- Telegram bot disabled or not configured.
- Нет доступа/DNS к `api.telegram.org`.
- Неверный токен или owner id в env.

Нужно заполнить `/etc/pcmanager/pcmanager.env` без публикации секретов:

```env
TELEGRAM_BOT_ENABLED=true
TELEGRAM_BOT_TOKEN=[HIDDEN]
TELEGRAM_ALLOWED_USER_IDS=[HIDDEN]
SERVER_ACCESS_KEY=[HIDDEN]
```

После этого:

```bash
sudo systemctl restart pcmanager-bot
sudo systemctl status pcmanager-bot --no-pager -l
```

### 2. Windows agent

Нужно настроить agent config на Linux-сервер:

```yaml
base_url: http://192.168.0.194:8765
websocket_url: ws://192.168.0.194:8765/ws/status
access_key: [HIDDEN]
```

Затем запустить агент на Windows и проверить, появился ли он в `/api/agents` или веб-панели.

### 3. Android app

В приложении указать:

```text
Server Base URL: http://192.168.0.194:8765/
WebSocket URL: ws://192.168.0.194:8765/ws/status
Test URL: http://192.168.0.194:8765/api/ping
```

Если телефон не дома, использовать Tailscale:

```text
Server Base URL: http://100.91.196.119:8765/
WebSocket URL: ws://100.91.196.119:8765/ws/status
```

### 4. Security

- Не открывать SSH в интернет.
- Не хранить токены в коде.
- Не пушить `.env` / `pcmanager.env` в GitHub.
- Не давать root-доступ без необходимости.
- Не удалять `/etc/pcmanager/pcmanager.env`.

## 6. Архитектура проекта

| Компонент | Папка/файл | Роль |
|---|---|---|
| FastAPI backend | `backend/app/main.py` | Точка входа API, WebSocket и веб-панели |
| API routes | `backend/app/api/*.py` | HTTP endpoint-ы для сервера, агентов, телефона, файлов, медиа и задач |
| Services | `backend/app/services/*.py` | Бизнес-логика задач, файлов, агентов, медиа, сети и диагностики |
| Config | `backend/app/config.py`, `/etc/pcmanager/pcmanager.env` | Настройки, секреты, флаги функций, пути |
| Telegram bot | `backend/app/bot/runner.py`, `backend/app/bot/telegram_bot.py` | Запуск и логика Telegram-бота |
| WebSocket | `backend/app/websocket/manager.py` | Live-события для панели, телефона и агентов |
| Web panel | `backend/app/web/panel.html` | Веб-интерфейс управления сервером |
| Windows agent | `pc-agent/agent.py` | Агент на Windows-ПК, статус, задачи, скриншоты, процессы |
| Android app | `android-app/` | Мобильное приложение для мониторинга и управления |
| Systemd | `systemd/pcmanager-server.service`, `systemd/pcmanager-bot.service` | Автозапуск backend и Telegram bot |
| Install script | `install_ubuntu.sh` | Установка на Ubuntu |
| Maintenance scripts | `scripts/*.sh` | start/stop/restart/status/logs/backup/update/diagnostics |
| Docs | `README.md`, `MIGRATION_WINDOWS_TO_UBUNTU.md`, `PROJECT_HANDOFF.md` | Документация и передача контекста |

## 7. Важные файлы и за что отвечают

- `install_ubuntu.sh` — установка на Ubuntu, venv, папки, systemd.
- `requirements.txt` — Python-зависимости backend.
- `backend/app/main.py` — FastAPI entrypoint.
- `backend/app/config.py` — чтение настроек из env.
- `backend/app/api/mobile_routes.py` — API для мобильного приложения.
- `backend/app/api/agent_routes.py` или `backend/app/api/agents.py` — API для агентов, если файл есть в текущей версии.
- `backend/app/services/task_service.py` — задачи для агентов.
- `backend/app/services/agent_service.py` — состояние агентов.
- `backend/app/websocket/manager.py` — WebSocket-связь.
- `backend/app/bot/runner.py` — запуск Telegram-бота.
- `backend/app/bot/telegram_bot.py` — команды Telegram и inline-кнопки.
- `pc-agent/agent.py` — Windows-агент.
- `pc-agent/agent_config.example.json` — пример настройки агента, если файл есть.
- `android-app/.../ApiConfig.kt` — URL сервера в Android.
- `android-app/.../ApiService.kt` или `PcControlApi.kt` — Retrofit API.
- `android-app/.../RealtimeGateway.kt` — WebSocket в Android.
- `systemd/pcmanager-server.service` — автозапуск backend.
- `systemd/pcmanager-bot.service` — автозапуск Telegram bot.
- `scripts/start.sh`, `stop.sh`, `restart.sh`, `status.sh`, `logs.sh` — обслуживание.
- `scripts/backup.sh` — бэкап.
- `scripts/update.sh` — обновление.

Не тратить время на подробный разбор `.jar`, `.zip`, `.apk.idsig`, `build/`, `.codex-tools/`, `backup_*/`, `__pycache__/`.

## 8. Команды для проверки

SSH:

```bash
ssh pc@192.168.0.194
```

Перейти в проект:

```bash
cd /home/pc/PCControlPersonal_Project
```

Проверить сервер:

```bash
sudo systemctl status pcmanager-server
```

Проверить бота:

```bash
sudo systemctl status pcmanager-bot
```

Перезапустить сервер:

```bash
sudo systemctl restart pcmanager-server
```

Перезапустить бота:

```bash
sudo systemctl restart pcmanager-bot
```

Логи сервера:

```bash
sudo journalctl -u pcmanager-server -n 100 --no-pager
sudo journalctl -u pcmanager-server -f
```

Логи бота:

```bash
sudo journalctl -u pcmanager-bot -n 100 --no-pager
sudo journalctl -u pcmanager-bot -f
```

Проверить API локально:

```bash
curl http://127.0.0.1:8765/api/ping
```

Проверить API по LAN:

```bash
curl http://192.168.0.194:8765/api/ping
```

Проверить порт:

```bash
ss -tulpn | grep 8765
```

Проверить IP:

```bash
hostname -I
```

Проверить Ethernet:

```bash
sudo ethtool enp4s0
```

Проверить Python:

```bash
cd /home/pc/PCControlPersonal_Project
python3 -m compileall backend
```

## 9. Как продолжать работу

Шаг 1: Почистить технический отчёт от Gradle/jar мусора и создать `TECHNICAL_FILES_REPORT_CLEAN.md`.

Шаг 2: Проверить `/etc/pcmanager/pcmanager.env` для Telegram bot, не выводя секреты.

Шаг 3: Перезапустить `pcmanager-bot` и проверить, что он `active (running)`.

Шаг 4: Подключить Windows agent к Linux backend.

Шаг 5: Проверить, появляется ли агент в `/api/agents` или веб-панели.

Шаг 6: Настроить Android app на адрес сервера `192.168.0.194` или Tailscale `100.91.196.119`.

Шаг 7: Проверить WebSocket `ws://192.168.0.194:8765/ws/status`.

Шаг 8: Добавить/проверить `diagnostics/doctor.py` или daily self-check.

Шаг 9: Сделать backup и нормальную структуру deploy/update.

## 10. Известные проблемы

- Telegram bot может быть disabled/not configured до заполнения env или при проблемах с `api.telegram.org`.
- `speedtest-cli` может показывать неверную скорость, но `ethtool` показывает реальную скорость линка.
- На клавиатуре сервера не все клавиши работают, поэтому лучше управлять через SSH.
- Сервер локальный, IP `192.168.0.194` не виден из интернета.
- Для доступа не из дома использовать Tailscale/ZeroTier/VPN, а не открывать SSH наружу.
- Codex cloud не сможет напрямую подключиться к локальному IP без локального VS Code/SSH/VPN.
- В отчётах нельзя показывать секреты.

## 11. Правила безопасности

- Не публиковать `.env` и `/etc/pcmanager/pcmanager.env`.
- Не писать токены в чат.
- Не хранить Telegram token в коде.
- Не открывать SSH наружу.
- Работать только с личными устройствами владельца.
- Опасные действия делать только с подтверждением.
- Перед крупными изменениями делать backup.
- Не добавлять скрытый доступ, обход защит, брутфорс или функции против чужих систем.

## 12. Быстрый старт для нового разработчика

1. Подключиться:

```bash
ssh pc@192.168.0.194
```

2. Открыть проект:

```bash
cd /home/pc/PCControlPersonal_Project
```

3. Проверить сервер:

```bash
curl http://127.0.0.1:8765/api/ping
sudo systemctl status pcmanager-server
```

4. Проверить бота:

```bash
sudo systemctl status pcmanager-bot
```

5. Читать `README.md`, `MIGRATION_WINDOWS_TO_UBUNTU.md`, `TECHNICAL_FILES_REPORT.md` и `PROJECT_HANDOFF.md`.

6. Не трогать и не выводить секреты.

## 13. Финальный краткий статус

Current status:
- Ubuntu Server: OK
- Network: OK
- SSH: OK
- Backend: OK
- API ping: OK
- Telegram bot: `active/running`
- Windows agent: TODO
- Android app: TODO
- Daily diagnostics: `CHECK: есть скрипты daily self-check, нужно проверить cron/report`
- Next best action: configure/check Telegram bot env and connect Windows agent
