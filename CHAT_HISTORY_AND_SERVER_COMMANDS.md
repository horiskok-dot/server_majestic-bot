# История проекта и команды подключения

Документ для передачи контекста другому разработчику, ChatGPT или Codex.

Важно: реальные пароли, токены Telegram, `SERVER_ACCESS_KEY`, `OPENAI_API_KEY`, Telegram user IDs и другие секреты здесь не хранятся. Все секреты заменены на `[HIDDEN]`.

## 1. Основной сервер

Ubuntu-сервер:

- OS: Ubuntu Server 24.04 LTS
- Hostname: `home`
- Linux user для SSH: `pc`
- LAN IP раньше встречался как `192.168.0.194`, актуальный IP в последних проверках: `192.168.0.193`
- PC Manager backend: FastAPI/Uvicorn
- Основной порт PC Manager: `8765`
- Minecraft порт: `25565/tcp`, если Minecraft установлен/включён
- Tailscale IP раньше встречался: `100.91.196.119`, если Tailscale включён

Пути PC Manager:

- Исходный проект на сервере: `/home/pc/PCControlPersonal_Project`
- Runtime/install path: `/opt/pcmanager`
- Config: `/etc/pcmanager/pcmanager.env`
- Data/storage: `/data`, `/var/lib/pcmanager`, `/var/lib/pcmanager/storage`
- Logs: `journalctl`, `/var/log/pcmanager`

Systemd services PC Manager:

- `pcmanager-server.service`
- `pcmanager-bot.service`
- `pcmanager-local-check.timer`, если установлен daily diagnostics
- `pcmanager-metrics-collector.timer`, если установлен metrics collector

## 2. SSH подключение

Подключиться к серверу:

```bash
ssh pc@192.168.0.193
```

Если старый IP ещё используется:

```bash
ssh pc@192.168.0.194
```

Проверить IP сервера из Windows:

```powershell
ping 192.168.0.193
ssh pc@192.168.0.193
```

Проверить IP на самом сервере:

```bash
hostname -I
ip addr
ip route
```

Пароль SSH: `[HIDDEN]`. Не сохранять пароль в коде, скриптах, GitHub или логах.

## 3. Быстрые команды PC Manager

Перейти в проект:

```bash
cd /home/pc/PCControlPersonal_Project
```

Проверить API локально на сервере:

```bash
curl http://127.0.0.1:8765/api/ping
curl http://127.0.0.1:8765/api/health
```

Проверить API по LAN:

```bash
curl http://192.168.0.193:8765/api/ping
```

Открыть Web UI:

```text
http://192.168.0.193:8765/
```

Проверить порт:

```bash
ss -tulpn | grep 8765
```

Статус сервисов:

```bash
sudo systemctl status pcmanager-server --no-pager
sudo systemctl status pcmanager-bot --no-pager
```

Перезапуск:

```bash
sudo systemctl restart pcmanager-server
sudo systemctl restart pcmanager-bot
```

Логи:

```bash
sudo journalctl -u pcmanager-server -n 100 --no-pager
sudo journalctl -u pcmanager-bot -n 100 --no-pager
sudo journalctl -u pcmanager-server -f
sudo journalctl -u pcmanager-bot -f
```

Компиляция Python:

```bash
cd /home/pc/PCControlPersonal_Project
python3 -m compileall backend
```

## 4. Access key и токены

Получить `SERVER_ACCESS_KEY` на сервере, не показывая его в чате:

```bash
KEY=$(sudo grep '^SERVER_ACCESS_KEY=' /etc/pcmanager/pcmanager.env | cut -d= -f2-)
curl -H "X-Server-Access-Key: $KEY" http://127.0.0.1:8765/api/agents
```

Проверить, что env читается:

```bash
sudo grep -n 'SERVER_ACCESS_KEY\|TELEGRAM_BOT_ENABLED\|BASE_PUBLIC_URL' /etc/pcmanager/pcmanager.env
```

Не отправлять в чат реальные значения:

- `TELEGRAM_BOT_TOKEN`
- `SERVER_ACCESS_KEY`
- `OPENAI_API_KEY`
- Telegram user IDs
- SSH password

## 5. Что делалось по PC Manager

Основные этапы:

- Перенос проекта PC Control Personal/PC Manager на Ubuntu Server.
- Настройка `/opt/pcmanager`, `/etc/pcmanager/pcmanager.env`, `/var/lib/pcmanager`, `/var/log/pcmanager`.
- Запуск FastAPI через `pcmanager-server.service`.
- Запуск Telegram bot через `pcmanager-bot.service`.
- Перевод Telegram bot на русский язык.
- Исправление inline-кнопок Telegram, которые раньше просто подсвечивались и ничего не делали.
- Добавление Web UI панели на `http://SERVER_IP:8765/`.
- Добавление страниц Dashboard, Server, Agents/PC Agent, Files, Media, Logs, Diagnostics, Wake, Settings.
- Добавление PWA-частей: `manifest.json`, `service-worker.js`.
- Добавление server screenshot/webcam/video, но они должны быть включены через env и не должны быть скрытыми.
- Добавление Wake-on-LAN настроек, хотя конкретная сетевуха могла не поддерживать WoL.
- Добавление Tailscale для доступа не только из дома.
- Добавление Local Doctor/Diagnostics вместо OpenAI AI Review, потому что OpenAI API платный.
- Удаление OpenAI/AI Review плана и переход к бесплатной локальной диагностике.
- Добавление Network Monitor, Maintenance Center, Health Score, Metrics, Events.
- Полировка Web UI: тёмная панель, карточки, мобильный режим, toast, placeholders.
- Исправление автообновления сайта, чтобы при refresh данных не выкидывало на главную страницу.
- Добавление мультизагрузки файлов на сайте.
- Добавление загрузки файлов через Telegram bot.
- Очистка старых update zip-архивов.
- HTTP stress test `/api/ping`.
- Начало добавления DDoS/rate-limit защиты.

## 6. Telegram bot

Telegram bot должен:

- Работать только для разрешённых пользователей.
- Не показывать секреты.
- Отвечать на русском.
- Давать красивые уведомления по задачам агента.
- Принимать файлы/фото/видео/аудио и сохранять на сервер.

Полезные команды Telegram:

```text
/start
/help
/status
/server
/agents
/agent <id>
/files
/upload
/download FILE_ID
/logs
/tasks
/screenshot <agent_id>
/agent_logs <agent_id>
/system_info <agent_id>
/diagnostics
/diagnostics_run
/diagnostics_latest
/health
/wol
/wake <device>
```

Файлы из Telegram:

- Можно просто отправить файл/фото/видео боту.
- Бот сохраняет файл и возвращает ID.
- Скачать обратно: `/download ID`.

## 7. Web UI

Открыть сайт:

```text
http://192.168.0.193:8765/
```

Основные страницы:

- Dashboard
- Network
- PC Agent / Agents
- Files
- Backups
- Media
- Logs
- Diagnostics
- Maintenance
- Wake
- Settings

Если сайт пишет `invalid token`:

- Ввести правильный admin/access token из `/etc/pcmanager/pcmanager.env`.
- Не путать `OPENAI_API_KEY` и `SERVER_ACCESS_KEY`.
- Для API использовать заголовок:

```bash
X-Server-Access-Key: <SERVER_ACCESS_KEY>
```

## 8. Files / uploads

На сайте:

- Страница `Files`.
- Можно выбрать один или много файлов.
- Можно drag & drop несколько файлов.
- Файлы сохраняются в `/data`.

Telegram:

- Отправить боту документ/фото/видео/аудио.
- Бот сохраняет файл как `FileAsset`.
- Команда `/download ID` отправляет файл обратно.

Проверка API мультизагрузки:

```bash
KEY=$(sudo grep '^SERVER_ACCESS_KEY=' /etc/pcmanager/pcmanager.env | cut -d= -f2-)
printf 'alpha' >/tmp/a.txt
printf 'beta' >/tmp/b.txt
curl -H "X-Server-Access-Key: $KEY" \
  -F "upload=@/tmp/a.txt" \
  -F "upload=@/tmp/b.txt" \
  "http://127.0.0.1:8765/api/files/upload?path=uploads/test_multi"
```

## 9. Windows Agent

Папка агента:

```text
pc-agent/
```

Конфиг агента:

```text
pc-agent/agent_config.json
```

Пример URL:

```json
{
  "server_base_url": "http://192.168.0.193:8765",
  "websocket_url": "ws://192.168.0.193:8765/ws/status",
  "access_key": "[HIDDEN]"
}
```

Запуск агента на Windows:

```bat
cd C:\Users\horis\Downloads\PCManagerBot_Setup_v2\PCControlPersonal_Project\pc-agent
run_agent.bat
```

Установка зависимостей агента:

```bat
install_agent_windows.bat
```

Проверить агента:

```bash
KEY=$(sudo grep '^SERVER_ACCESS_KEY=' /etc/pcmanager/pcmanager.env | cut -d= -f2-)
curl -H "X-Server-Access-Key: $KEY" http://127.0.0.1:8765/api/agents
```

Разрешённые задачи агента:

- `ping`
- `system_info`
- `screenshot`
- `process_list`
- `disk_info`
- `temperature`
- `agent_logs`
- `restart_allowed_app`
- некоторые кнопки игры/рабочих столов были добавлены позже, но gamepad/Sunshine/Moonlight затем просили удалить с сайта.

Запрещено:

- Произвольный shell.
- Произвольный PowerShell.
- Скрытая камера/микрофон.
- Удаление файлов без подтверждения.
- Запуск неизвестных программ вне allowlist.

## 10. Diagnostics / Local Doctor

Команды:

```bash
cd /home/pc/PCControlPersonal_Project
python3 tools/doctor.py
python3 tools/log_analyzer.py
bash scripts/local_check.sh
```

Отчёты:

```text
tools/reports/latest.txt
tools/reports/latest.json
tools/reports/YYYY-MM-DD_HH-MM.txt
tools/reports/YYYY-MM-DD_HH-MM.json
```

Timer:

```bash
sudo systemctl status pcmanager-local-check.timer --no-pager
systemctl list-timers | grep pcmanager
```

## 11. Backups

PC Manager backups встречались в:

```text
/home/pc/PCControlPersonal_Project/backup_*
/home/pc/backups
/data/backups
```

Backup командой, если есть скрипт:

```bash
cd /home/pc/PCControlPersonal_Project
bash scripts/backup.sh
```

Перед крупными изменениями:

```bash
STAMP=$(date +%F_%H-%M)
mkdir -p /home/pc/backups/manual_$STAMP
cp -a /home/pc/PCControlPersonal_Project /home/pc/backups/manual_$STAMP/
```

## 12. Tailscale

Tailscale ставился для доступа к серверу вне дома.

Проверка:

```bash
tailscale status
tailscale ip -4
```

Подключение через Tailscale, если IP актуален:

```bash
ssh pc@100.91.196.119
```

Web UI через Tailscale:

```text
http://100.91.196.119:8765/
```

## 13. Wake-on-LAN

Проверка сетевухи:

```bash
ip link
sudo ethtool enp4s0
```

Включение, если поддерживается:

```bash
sudo ethtool -s enp4s0 wol g
```

Если пишет `Operation not supported`, то конкретная сетевуха/BIOS/драйвер не поддерживает WoL в текущем режиме.

## 14. HTTP stress tests

Безопасный тест FastAPI:

```bash
curl http://192.168.0.193:8765/api/ping
```

Проводились HTTP-тесты:

- 1720 запросов: 1720 OK, ошибок 0.
- Усиленный `/api/ping`: 15000 запросов, 14000 OK, часть ошибок была на стороне Windows-клиента из-за лимита sockets.

Не использовать UDP flood/DoS скрипты. Они проверяют не FastAPI, а забивают сеть/роутер.

## 15. DDoS / rate limit

В проекте уже был middleware rate limit в `backend/app/main.py`.

Идея усиления:

- Лимитировать не только внешние IP, но и LAN/Tailscale.
- Отдельные лимиты для `/api/ping`, static/public paths и приватных API.
- Возвращать `429 Rate limit exceeded`.
- Не блокировать SSH.
- Настроить UFW аккуратно.
- Настроить fail2ban для SSH.

Проверить UFW:

```bash
sudo ufw status verbose
```

Разрешить SSH и нужные порты:

```bash
sudo ufw allow OpenSSH
sudo ufw allow 8765/tcp
sudo ufw allow 25565/tcp
```

Fail2ban:

```bash
sudo systemctl status fail2ban --no-pager
sudo fail2ban-client status
sudo fail2ban-client status sshd
```

## 16. Minecraft Java Server

Пользователь просил развернуть Vanilla Minecraft Java Server latest stable:

- Использовать официальный Mojang manifest/API.
- Папка: `/opt/minecraft/server`
- Пользователь: `minecraft`
- Порт: `25565/tcp`
- `online-mode=true`
- `enforce-whitelist=true`
- `white-list=true` или `whitelist=true` в зависимости от версии properties.
- `enable-command-block=false`
- `enable-rcon=false`
- `max-players=10`
- `pvp=false`
- systemd service: `minecraft.service`
- backup script: `/opt/minecraft/backup.sh`
- update script: `/opt/minecraft/update_minecraft.sh`

Команды Minecraft service:

```bash
sudo systemctl status minecraft --no-pager
sudo systemctl start minecraft
sudo systemctl stop minecraft
sudo systemctl restart minecraft
sudo journalctl -u minecraft -f
```

Проверить порт:

```bash
ss -tulpn | grep 25565
```

Whitelist/OP через консоль сервера:

```text
whitelist add Nick
op Nick
deop Nick
whitelist remove Nick
```

Если используется `rcon-cli` или screen/tmux, команды могут отличаться.

В рабочей папке Windows видны Minecraft-related файлы:

- `install_mc.py`
- `install_playit.py`
- `install_chunky.py`
- `install_we.py`
- `download_mc_mods.py`
- `mc_stats.py`
- `server.properties`
- `bukkit.yml`
- `spigot.yml`
- `paper-world-defaults.yml`
- `Chunky.jar`
- `tab_config.yml`
- `antiredstone_config.yml`
- `messages_en.yml`
- `messages_vi.yml`

Это похоже на дальнейшую работу с Paper/плагинами, но изначальная безопасная цель была Vanilla, а PaperMC только отдельным этапом после подтверждения.

## 17. AI на сайт сервера

Папка, которую пользователь дал:

```text
C:\Users\horis\Documents\sffsdfadfs
```

Что найдено:

- `assistant.py`
- `gui_app.py`
- `gravity.py`
- `requirements.txt`
- `Modelfile.dolphin.uncensored`
- `Modelfile.qwen.uncensored`

Это локальное AI-приложение на Python с Ollama, PyAutoGUI, Pillow/OpenCV и GUI через CustomTkinter. Это не сам серверный сайт PC Manager.

Зависимости:

```text
pyautogui
pillow
opencv-python
ollama
rich
```

Если добавлять AI на сайт сервера, безопасный вариант:

- Не использовать платный OpenAI API.
- Подключить локальный Ollama API, если установлен.
- Добавить страницу `AI` в Web UI.
- Добавить backend endpoint, который ходит на локальный Ollama, например `http://127.0.0.1:11434`.
- Не давать AI произвольный shell.
- Не давать AI скрыто управлять ПК.
- Любые действия через подтверждение и allowlist.

Проверить Ollama:

```bash
ollama list
curl http://127.0.0.1:11434/api/tags
```

## 18. Локальные пути Windows

Основная рабочая папка Codex/Windows:

```text
C:\Users\horis\Downloads\PCManagerBot_Setup_v2
```

Проект PC Manager локально:

```text
C:\Users\horis\Downloads\PCManagerBot_Setup_v2\PCControlPersonal_Project
```

Отчёты:

```text
C:\Users\horis\Downloads\PCManagerBot_Setup_v2\reports
```

Локальный AI:

```text
C:\Users\horis\Documents\sffsdfadfs
```

## 19. SCP / копирование на сервер

Копировать файл на сервер:

```powershell
scp C:\path\to\file.zip pc@192.168.0.193:/tmp/file.zip
```

Важно: в Windows PowerShell путь `C:\...` надо запускать с Windows, а не внутри SSH-сессии Linux. Если выполнить `scp "C:\..."` уже на Ubuntu, Linux воспримет `C:` как hostname.

Копировать папку:

```powershell
scp -r C:\Users\horis\Downloads\PCManagerBot_Setup_v2\PCControlPersonal_Project pc@192.168.0.193:/home/pc/
```

На сервере распаковать zip:

```bash
sudo apt install -y unzip rsync
rm -rf /tmp/update
mkdir -p /tmp/update
unzip -o /tmp/update.zip -d /tmp/update
```

## 20. Безопасные правила работы

Нельзя:

- Публиковать `.env`.
- Писать реальные токены в чат.
- Хранить SSH password в файлах.
- Открывать SSH в интернет без VPN/Tailscale/ключей.
- Добавлять произвольный shell в Web UI.
- Делать скрытую камеру/микрофон.
- Выключать `online-mode` Minecraft.
- Запускать UDP flood/DoS тесты.

Перед изменениями:

```bash
cd /home/pc/PCControlPersonal_Project
STAMP=$(date +%F_%H-%M)
mkdir -p backup_$STAMP
cp -a backend pc-agent README.md PROJECT_HANDOFF.md .env.example requirements.txt backup_$STAMP/ 2>/dev/null || true
```

После изменений:

```bash
cd /home/pc/PCControlPersonal_Project
python3 -m compileall backend
sudo systemctl restart pcmanager-server
sudo systemctl restart pcmanager-bot
curl http://127.0.0.1:8765/api/ping
sudo systemctl status pcmanager-server --no-pager
sudo systemctl status pcmanager-bot --no-pager
```

## 21. Что делать новому разработчику сначала

1. Подключиться:

```bash
ssh pc@192.168.0.193
```

2. Проверить сервер:

```bash
hostname -I
uptime
free -h
df -h
curl http://127.0.0.1:8765/api/ping
```

3. Проверить PC Manager:

```bash
sudo systemctl status pcmanager-server --no-pager
sudo systemctl status pcmanager-bot --no-pager
```

4. Проверить проект:

```bash
cd /home/pc/PCControlPersonal_Project
python3 -m compileall backend
```

5. Проверить сайт:

```text
http://192.168.0.193:8765/
```

6. Проверить Minecraft, если нужен:

```bash
sudo systemctl status minecraft --no-pager
ss -tulpn | grep 25565
```

7. Не трогать секреты и `.env` без backup.

