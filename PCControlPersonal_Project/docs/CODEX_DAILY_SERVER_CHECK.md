# Codex Daily Server Check

Локальная проверка Ubuntu-сервера PC Manager с Windows-ПК через SSH.

Скрипты не хранят пароль, не выводят токены и не меняют firewall/SSH.

## Что проверяется

- IP сервера: `hostname -I`
- uptime
- диск: `df -h`
- RAM: `free -h`
- сервисы:
  - `pcmanager-server`
  - `pcmanager-bot`
- API:
  - `http://127.0.0.1:8765/api/ping`
- последние логи:
  - `journalctl -u pcmanager-server -n 80 --no-pager`
  - `journalctl -u pcmanager-bot -n 80 --no-pager`

Скрипт ищет в логах:

- `ERROR`
- `WARNING`
- `Traceback`
- `Exception`
- `failed`
- `disabled`
- `not configured`

## Ручной запуск

Из папки проекта на Windows:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\codex_daily_server_check.ps1 -Interactive
```

`-Interactive` разрешает обычному `ssh` спросить пароль в терминале.

Без `-Interactive` скрипт работает в безопасном non-interactive режиме и ожидает SSH-ключ:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\codex_daily_server_check.ps1
```

## Ежедневный запуск

Установить задачу Windows Task Scheduler на каждый день в 10:00:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\install_windows_daily_task.ps1
```

Важно: Task Scheduler не может безопасно вводить SSH-пароль. Для ежедневного запуска нужен SSH-ключ.

## Где смотреть отчёты

Отчёты сохраняются локально:

```text
reports/server_check_YYYY-MM-DD.txt
```

Посмотреть последний отчёт:

```powershell
Get-ChildItem .\reports\server_check_*.txt | Sort-Object LastWriteTime -Descending | Select-Object -First 1 | Get-Content
```

## Отключить ежедневную задачу

```powershell
Unregister-ScheduledTask -TaskName "PCManager Codex Daily Server Check" -Confirm:$false
```

## SSH-подключение

Ручная проверка SSH:

```powershell
ssh pc@192.168.0.194
```

## Почему пароль нельзя сохранять

Пароль в `.ps1`, `.bat`, логах или Task Scheduler легко случайно показать, отправить в архив или залить в репозиторий. Поэтому скрипт не хранит пароль вообще.

Для автоматического ежедневного запуска используй SSH-ключ:

```powershell
ssh-keygen -t ed25519
type $env:USERPROFILE\.ssh\id_ed25519.pub
```

Публичный ключ нужно добавить на сервер в:

```text
/home/pc/.ssh/authorized_keys
```

После этого команда ниже должна входить без пароля:

```powershell
ssh pc@192.168.0.194 "echo ok"
```

## Проверка прямо на Ubuntu-сервере

Если нужно, чтобы проверка работала сама на сервере без Windows, используются:

```text
scripts/server_daily_self_check.sh
scripts/install_server_daily_self_check.sh
```

Ручной запуск на сервере:

```bash
cd /home/pc/PCControlPersonal_Project
bash scripts/server_daily_self_check.sh
```

После проверки скрипт отправляет краткий summary в Telegram, если в `/etc/pcmanager/pcmanager.env` заданы:

```env
TELEGRAM_BOT_TOKEN=...
TELEGRAM_OWNER_ID=...
```

В сообщение попадает только статус `OK/WARNING/ERROR`, диск/RAM и количество найденных проблем в логах. Токены и access key не отправляются и маскируются.

Включить ежедневный запуск на сервере в 10:00 через `crontab` пользователя `pc`:

```bash
cd /home/pc/PCControlPersonal_Project
bash scripts/install_server_daily_self_check.sh
```

Посмотреть расписание:

```bash
crontab -l
```

Посмотреть последний отчёт:

```bash
ls -lt /home/pc/PCControlPersonal_Project/reports/server_self_check_*.txt | head
tail -n 80 /home/pc/PCControlPersonal_Project/reports/server_self_check_$(date +%F).txt
```

Отключить серверную ежедневную проверку:

```bash
crontab -l | grep -v PCMANAGER_SERVER_DAILY_SELF_CHECK | crontab -
```
