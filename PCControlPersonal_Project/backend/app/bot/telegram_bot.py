import json
import logging
import subprocess
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Any
import io
import zipfile


import telebot
from requests.exceptions import ConnectionError as RequestsConnectionError
from requests.exceptions import ReadTimeout
from telebot import types

from ..config import get_settings
from ..database import db_session
from ..models import Agent, FileAsset, LogEntry, Task, User, ActivationKey
from ..services.agent_service import agent_to_mobile, compute_agent_status, list_agents
from ..services.file_service import asset_path, create_asset_from_bytes
from ..services.log_service import add_log
from ..services.network_service import server_info
from ..services.server_media_service import create_server_screenshot, create_server_webcam_photo, create_server_webcam_video
from ..services.task_service import cancel_task, create_task, expire_running_tasks, retry_task
from ..services.wol_service import list_wol_devices, wake_device
from ..utils.logging import append_json_log
from .lang_ru import BTN, RU_TEXTS


settings = get_settings()
logger = logging.getLogger("telegram-bot")
BOT: telebot.TeleBot | None = None
STATE = {"last_log_id": 0}
NOTIFY_EVENTS = {"agent_online", "agent_offline", "task_done", "task_failed", "threshold_alert"}
SUPPRESSED_ERROR_EVENTS = {"server_screenshot_failed"}
NOTIFIED_TASK_IDS: set[str] = set()
USER_STATES: dict[int, dict[str, Any]] = {}

ACTION_LABELS = {
    "desktop_left": "\u0420\u0430\u0431\u043e\u0447\u0438\u0439 \u0441\u0442\u043e\u043b \u0432\u043b\u0435\u0432\u043e",
    "desktop_right": "\u0420\u0430\u0431\u043e\u0447\u0438\u0439 \u0441\u0442\u043e\u043b \u0432\u043f\u0440\u0430\u0432\u043e",
    "desktop_new": "\u0421\u043e\u0437\u0434\u0430\u0442\u044c \u0440\u0430\u0431\u043e\u0447\u0438\u0439 \u0441\u0442\u043e\u043b",
    "desktop_close": "\u0417\u0430\u043a\u0440\u044b\u0442\u044c \u0440\u0430\u0431\u043e\u0447\u0438\u0439 \u0441\u0442\u043e\u043b",
    "release_keys": "\u041e\u0442\u043fу\u0441\u0442\u0438\u0442\u044c \u043aл\u0430\u0432\u0438\u0448\u0438",
    "press_key": "\u041d\u0430\u0436\u0430\u0442\u044c \u043a\u043b\u0430\u0432\u0438\u0448\u0443",
    "click_preset": "\u041aл\u0438\u043a \u043f\u043e \u043f\u0440\u0435\u0441\u0435\u0442\u0443",
    "volume_up": "\u0413\u0440\u043e\u043c\u043a\u043e\u0441\u0442\u044c +",
    "volume_down": "\u0413\u0440\u043e\u043c\u043a\u043e\u0441\u0442\u044c -",
    "cleanup_screenshots": "\u041e\u0447\u0438с\u0442\u0438\u0442\u044c \u0441\u0442\u0430\u0440\u044b\u0435 \u0441\u043a\u0440\u0438\u043d\u0448\u043e\u0442\u044b",
    "automation_status": "\u0421т\u0430\u0442\u0443с \u0430\u0432\u0442\u043e\u043c\u0430\u0442\u0438\u0437\u0430\u0446\u0438\u0438",
    "game_status": "\u0421\u0442\u0430\u0442\u0443\u0441 \u0438\u0433\u0440\u044b",
    "screenshot": "\u0421\u043a\u0440\u0438\u043d\u0448от",
    "take_screenshot": "\u0421\u043a\u0440\u0438\u043d\u0448от",
    "system_info": "Информация о системе",
    "get_system_info": "Информация о системе",
    "process_list": "Список процессов",
    "get_process_list": "Список процессов",
    "disk_info": "Диски",
    "get_disk_info": "Диски",
    "agent_logs": "Логи агента",
    "anti_afk_start": "Anti-AFK включён",
    "anti_afk_stop": "Anti-AFK выключен",
    "auto_screen_start": "Автоскрин включён",
    "auto_screen_stop": "Автоскрин выключен",
    "launch_allowed_app": "Запуск приложения",
    "restart_allowed_app": "Перезапуск приложения",
}


def is_newer_version(current: str | None, latest: str | None) -> bool:
    if not current or not latest:
        return False
    try:
        v_curr = [int(x) for x in str(current).split(".")]
        v_late = [int(x) for x in str(latest).split(".")]
        return v_late > v_curr
    except Exception:
        return False


def is_owner(user_id: int | None) -> bool:
    return int(user_id or 0) in settings.allowed_telegram_ids


def main_menu_keyboard() -> types.InlineKeyboardMarkup:
    markup = types.InlineKeyboardMarkup()
    markup.row(
        types.InlineKeyboardButton(BTN["refresh_status"], callback_data="refresh_status"),
        types.InlineKeyboardButton(BTN["agents"], callback_data="show_agents"),
    )
    markup.row(
        types.InlineKeyboardButton(BTN["files"], callback_data="show_files"),
        types.InlineKeyboardButton(BTN["logs"], callback_data="show_logs"),
    )
    markup.row(
        types.InlineKeyboardButton(BTN["server_ip"], callback_data="show_server_ip"),
        types.InlineKeyboardButton(BTN["recent_tasks"], callback_data="show_recent_tasks"),
    )
    markup.row(
        types.InlineKeyboardButton(BTN["diagnostics"], callback_data="show_diagnostics"),
        types.InlineKeyboardButton(BTN["wake"], callback_data="show_wol"),
    )
    markup.row(
        types.InlineKeyboardButton("📊 Статус дисков (HDD/SSD)", callback_data="show_storage")
    )
    return markup


def back_keyboard() -> types.InlineKeyboardMarkup:
    markup = types.InlineKeyboardMarkup()
    markup.row(types.InlineKeyboardButton(BTN["main_menu"], callback_data="main_menu"))
    return markup


def files_keyboard() -> types.InlineKeyboardMarkup:
    markup = types.InlineKeyboardMarkup()
    markup.row(
        types.InlineKeyboardButton(BTN["photos"], callback_data="show_photos"),
        types.InlineKeyboardButton(BTN["screenshots"], callback_data="show_screenshots"),
    )
    markup.row(
        types.InlineKeyboardButton(BTN["videos"], callback_data="show_videos"),
        types.InlineKeyboardButton(BTN["main_menu"], callback_data="main_menu"),
    )
    return markup


def confirm_keyboard(action: str) -> types.InlineKeyboardMarkup:
    markup = types.InlineKeyboardMarkup()
    markup.row(
        types.InlineKeyboardButton(BTN["confirm"], callback_data=f"confirm:{action}"),
        types.InlineKeyboardButton(BTN["cancel"], callback_data="main_menu"),
    )
    return markup


def send_safe(bot: telebot.TeleBot, chat_id: int, text: str, **kwargs) -> None:
    try:
        bot.send_message(chat_id, (text or "-")[:3900], **kwargs)
    except Exception as exc:
        logger.exception("Ошибка отправки сообщения Telegram: %s", exc)
        safe_bot_log({"event": "telegram_send_failed", "error": str(exc)})


def safe_bot_log(payload: dict) -> None:
    try:
        append_json_log("bot.log", payload)
    except Exception as exc:
        logger.warning("Не удалось записать bot.log: %s", exc)


def answer_callback(bot: telebot.TeleBot, call, text: str | None = None) -> None:
    try:
        bot.answer_callback_query(call.id, text or "")
    except Exception as exc:
        logger.exception("Ошибка ответа на callback Telegram: %s", exc)

def owner_only(bot: telebot.TeleBot, message) -> bool:
    if is_owner(getattr(message.from_user, "id", 0)):
        return True
    send_safe(bot, message.chat.id, RU_TEXTS["access_denied"])
    return False


def callback_owner_only(bot: telebot.TeleBot, call) -> bool:
    if is_owner(getattr(call.from_user, "id", 0)):
        return True
    answer_callback(bot, call, RU_TEXTS["access_denied"])
    return False


def start_text() -> str:
    return f"{RU_TEXTS['start_ready']}\n\n{RU_TEXTS['choose_action']}"


def status_text() -> str:
    with db_session() as db:
        expire_running_tasks(db)
        agents = list_agents(db)
        online = sum(1 for agent in agents if compute_agent_status(agent) == "online")
        active = db.query(Task).filter(Task.status.in_(["queued", "pending", "running"])).count()
        errors = [agent.last_error for agent in agents if agent.last_error][-3:]
    lines = [
        RU_TEXTS["server_online"],
        f"Агенты: {len(agents)}",
        f"Онлайн: {online}",
        f"Активные задачи: {active}",
    ]
    if errors:
        lines.append("Последние ошибки:")
        lines.extend(f"- {error}" for error in errors)
    return "\n".join(lines)


def server_ip_text() -> str:
    data = server_info()
    return (
        "Информация о сервере\n"
        f"Hostname: {data.get('hostname') or '-'}\n"
        f"Local IP: {data.get('local_ip') or '-'}\n"
        f"Public URL: {data.get('public_url') or '-'}\n"
        f"Port: {data.get('server_port') or '-'}\n"
        f"Base URL для телефона: {data.get('base_url') or '-'}\n"
        f"WebSocket URL: {data.get('websocket_url') or '-'}\n"
        f"Версия: {data.get('version') or '-'}"
    )


def diagnostics_text() -> str:
    with db_session() as db:
        agents = list_agents(db)
        online = sum(1 for agent in agents if compute_agent_status(agent) == "online")
        active = db.query(Task).filter(Task.status.in_(["queued", "pending", "running"])).count()
        last_errors = (
            db.query(LogEntry)
            .filter(LogEntry.level.in_(["ERROR", "WARNING"]))
            .order_by(LogEntry.created_at.desc())
            .limit(3)
            .all()
        )
    return "\n".join(
        [
            "Диагностика сервера",
            f"Telegram bot: {'включён' if settings.telegram_bot_enabled else 'выключен'}",
            f"Telegram token: {'задан' if settings.telegram_bot_token else 'не задан'}",
            f"Admin IDs: {'заданы' if settings.allowed_telegram_ids else 'не заданы'}",
            f"LOCAL_ONLY: {settings.local_only}",
            f"Base URL: {settings.base_public_url}",
            f"Агенты: {online}/{len(agents)} онлайн",
            f"Активные задачи: {active}",
            f"WOL устройств: {len(list_wol_devices())}",
            "Последние предупреждения/ошибки:",
            *[f"- {item.event}: {item.message}" for item in last_errors],
        ]
    )


def wol_text() -> str:
    devices = list_wol_devices()
    if not devices:
        return (
            "Wake-on-LAN устройства не настроены.\n\n"
            "Добавь в /etc/pcmanager/pcmanager.env строку:\n"
            "WOL_DEVICES=notebook=AA:BB:CC:DD:EE:FF\n\n"
            "Потом перезапусти сервер и бота."
        )
    lines = ["Wake-on-LAN устройства:"]
    for device in devices:
        lines.append(f"- {device.name}: {device.mac}")
    lines.append("")
    lines.append("Команда: /wake NAME")
    return "\n".join(lines)


def wol_keyboard() -> types.InlineKeyboardMarkup:
    markup = types.InlineKeyboardMarkup()
    for device in list_wol_devices():
        markup.row(types.InlineKeyboardButton(f"Включить {device.name}", callback_data=f"wake:{device.name}"))
    markup.row(types.InlineKeyboardButton(BTN["main_menu"], callback_data="main_menu"))
    return markup


def agents_text() -> str:
    with db_session() as db:
        agents = [agent_to_mobile(agent) for agent in list_agents(db)]
    if not agents:
        return RU_TEXTS["no_agents"]
    
    lines = ["🖥️ **Список агентов:**\n"]
    for item in agents[:10]:
        status_raw = str(item.get("status") or "offline").lower()
        status_val = "В сети 🟢" if status_raw == "online" else "Не в сети 🔴"
        name = item.get('name') or 'Без имени'
        version = item.get('version') or '-'
        ip = item.get('local_ip') or '-'
        last_seen = item.get('last_seen') or '-'
        
        lines.append(
            f"💻 **{name}**\n"
            f"└ Статус: **{status_val}**\n"
            f"└ Версия: `{version}`\n"
            f"└ IP: `{ip}`\n"
            f"└ Последний раз в сети: {last_seen}"
        )
    return "\n\n".join(lines)


def file_type_title(public_type: str | None) -> str:
    titles = {
        None: "Последние файлы",
        "server_webcam_photo": "Фото вебки сервера",
        "agent_camera_photo": "Фото агентов",
        "server_screenshot": "Скриншоты сервера",
        "agent_screenshot": "Скриншоты агентов",
        "server_webcam_video": "Видео вебки сервера",
        "agent_camera_video": "Видео агентов",
        "telegram_file": "Telegram-файлы",
    }
    return titles.get(public_type, public_type or "Файлы")


def file_list_text(public_type: str | None = None) -> str:
    with db_session() as db:
        query = db.query(FileAsset).filter(FileAsset.is_active == True).order_by(FileAsset.created_at.desc())  # noqa: E712
        if public_type:
            query = query.filter(FileAsset.public_type == public_type)
        files = query.limit(15).all()
    if not files:
        return f"{file_type_title(public_type)}\n{RU_TEXTS['no_files']}"
    lines = [file_type_title(public_type)]
    for item in files:
        created = item.created_at.strftime("%Y-%m-%d %H:%M") if item.created_at else "-"
        lines.append(f"#{item.id} | {item.original_filename or item.filename} | {item.public_type} | {item.size_bytes} байт | {created}")
    lines.append("\nСкачать: /download FILE_ID")
    return "\n".join(lines)


def tasks_text() -> str:
    with db_session() as db:
        expire_running_tasks(db)
        tasks = db.query(Task).order_by(Task.created_at.desc()).limit(15).all()
    if not tasks:
        return RU_TEXTS["no_tasks"]
    lines = ["Последние задачи"]
    for task in tasks:
        created = task.created_at.strftime("%Y-%m-%d %H:%M") if task.created_at else "-"
        lines.append(
            f"{task.task_id}\n"
            f"Агент: {task.agent_id}\n"
            f"Команда: {task.action}\n"
            f"Статус: {task.status}\n"
            f"Создана: {created}\n"
            f"Ошибка: {task.error or '-'}"
        )
    return "\n\n".join(lines)


def logs_text() -> str:
    with db_session() as db:
        entries = db.query(LogEntry).order_by(LogEntry.created_at.desc()).limit(30).all()
    if not entries:
        return RU_TEXTS["no_logs"]
    lines = ["Последние 30 строк логов"]
    for entry in entries:
        created = entry.created_at.strftime("%H:%M:%S") if entry.created_at else "-"
        lines.append(f"{created} [{entry.level}] {entry.source}/{entry.event}: {entry.message}")
    return "\n".join(lines)


def send_asset(bot: telebot.TeleBot, chat_id: int, asset: FileAsset) -> None:
    path = asset_path(asset)
    if asset.public_type in {"screenshot", "server_screenshot", "agent_screenshot"}:
        caption = "🖥️ Скриншот экрана"
    elif asset.public_type in {"photo", "server_webcam_photo", "agent_camera_photo"}:
        caption = "📷 Снимок с веб-камеры"
    elif asset.public_type in {"video", "server_webcam_video", "agent_camera_video"}:
        caption = "📹 Видео с веб-камеры"
    else:
        caption = f"Файл: {asset.original_filename or asset.filename}"
        
    with path.open("rb") as handle:
        if asset.public_type in {"photo", "screenshot", "server_screenshot", "server_webcam_photo", "agent_screenshot", "agent_camera_photo"}:
            bot.send_photo(chat_id, handle, caption=caption)
        elif asset.public_type in {"video", "server_webcam_video", "agent_camera_video"}:
            bot.send_video(chat_id, handle, caption=caption)
        else:
            bot.send_document(chat_id, handle, visible_file_name=asset.original_filename or asset.filename, caption=caption)


def telegram_attachment_info(message) -> tuple[str, str, str | None]:
    now = datetime.now().strftime("%Y%m%d_%H%M%S")
    if getattr(message, "document", None):
        item = message.document
        return item.file_id, item.file_name or f"telegram_document_{now}.bin", item.mime_type
    if getattr(message, "photo", None):
        item = message.photo[-1]
        return item.file_id, f"telegram_photo_{now}.jpg", "image/jpeg"
    if getattr(message, "video", None):
        item = message.video
        return item.file_id, item.file_name or f"telegram_video_{now}.mp4", item.mime_type or "video/mp4"
    if getattr(message, "audio", None):
        item = message.audio
        return item.file_id, item.file_name or f"telegram_audio_{now}.mp3", item.mime_type
    if getattr(message, "voice", None):
        item = message.voice
        return item.file_id, f"telegram_voice_{now}.ogg", item.mime_type or "audio/ogg"
    if getattr(message, "video_note", None):
        item = message.video_note
        return item.file_id, f"telegram_video_note_{now}.mp4", "video/mp4"
    raise ValueError("Файл не найден в сообщении")


def save_telegram_upload(bot: telebot.TeleBot, message) -> None:
    if not owner_only(bot, message):
        return
    try:
        file_id, filename, mime_type = telegram_attachment_info(message)
        file_info = bot.get_file(file_id)
        data = bot.download_file(file_info.file_path)
        with db_session() as db:
            asset = create_asset_from_bytes(
                db,
                data,
                filename,
                "telegram_file",
                "telegram",
                description=f"Telegram upload from chat {message.chat.id}",
                mime_type=mime_type,
            )
        try:
            uploads_dir = Path("/data/uploads")
            uploads_dir.mkdir(parents=True, exist_ok=True)
            target_path = uploads_dir / filename
            target_path.write_bytes(data)
            logger.info("Telegram uploaded file physically written to %s", target_path)
        except Exception as e:
            logger.exception("Failed to write telegram upload to /data/uploads: %s", e)
        send_safe(
            bot,
            message.chat.id,
            (
                "Файл сохранён на сервере.\n"
                f"ID: {asset.id}\n"
                f"Имя: {asset.original_filename or asset.filename}\n"
                f"Размер: {asset.size_bytes} байт\n\n"
                f"Скачать обратно: /download {asset.id}"
            ),
            reply_markup=files_keyboard(),
        )
    except Exception as exc:
        logger.exception("Не удалось сохранить файл из Telegram: %s", exc)
        send_safe(bot, message.chat.id, f"Не удалось сохранить файл: {exc}", reply_markup=files_keyboard())


def create_agent_task(message, bot: telebot.TeleBot, action: str, payload: dict, usage: str, confirmed: bool = False) -> None:
    parts = (message.text or "").split()
    if len(parts) < 2:
        send_safe(bot, message.chat.id, f"Формат: {usage}")
        return
    with db_session() as db:
        agent = db.query(Agent).filter(Agent.agent_id == parts[1]).first()
        if not agent:
            send_safe(bot, message.chat.id, RU_TEXTS["agent_not_found"])
            return
        try:
            task = create_task(db, agent, action, payload, "telegram", confirmed=confirmed)
            send_safe(bot, message.chat.id, f"Задача создана: {task.task_id}", reply_markup=back_keyboard())
        except ValueError as exc:
            send_safe(bot, message.chat.id, f"Ошибка: {exc}")


def ensure_telegram_user(db, telegram_id: int, username: str | None) -> User:
    tg_str = str(telegram_id)
    user = db.query(User).filter(User.telegram_id == tg_str).first()
    if not user:
        user = User(telegram_id=tg_str, username=username or f"tg_{telegram_id}")
        db.add(user)
        db.commit()
        db.refresh(user)
    return user


def generate_activation_key_for_user(db, user_id: int) -> str:
    import random
    chars = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
    part1 = "".join(random.choices(chars, k=4))
    part2 = "".join(random.choices(chars, k=4))
    key = f"TG-{part1}-{part2}"
    
    while db.query(ActivationKey).filter(ActivationKey.key == key).first() is not None:
        part1 = "".join(random.choices(chars, k=4))
        part2 = "".join(random.choices(chars, k=4))
        key = f"TG-{part1}-{part2}"
        
    key_entry = ActivationKey(key=key, user_id=user_id)
    db.add(key_entry)
    db.commit()
    return key


# send_customized_agent_zip removed for security

def send_agent_file(bot: telebot.TeleBot, chat_id: int) -> None:
    # telegram_bot.py is at: backend/app/bot/  → .parent×3 = backend/
    # pc-agent/ and releases/ are next to backend/, so need one more .parent = project root
    project_root = Path(__file__).resolve().parent.parent.parent.parent
    exe_path = project_root / "releases" / "agent.exe"
    if exe_path.exists():
        base_url = settings.base_public_url
        if "YOUR_SERVER_IP" in base_url or not base_url:
            import socket
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.connect(("8.8.8.8", 80))
                local_ip = s.getsockname()[0]
                s.close()
            except Exception:
                local_ip = "192.168.0.193"
            base_url = f"http://{local_ip}:8765"
            
        url = f"{base_url.rstrip('/')}/releases/PCManager_Agent.exe"
        text = (
            "🖥️ *Установщик PCManager для Windows (.exe)*\n\n"
            "Файл установщика весит более 50 МБ и не может быть отправлен напрямую через Telegram.\n"
            "Вы можете скачать его по прямой ссылке с вашего личного сервера:\n\n"
            f"🔗 [Скачать PCManager_Agent.exe]({url})\n\n"
            "_После скачивания запустите программу на ПК и введите ваш ключ активации для автоматического подключения!_"
        )
        markup = types.InlineKeyboardMarkup()
        markup.row(
            types.InlineKeyboardButton("📥 Скачать PCManager_Agent.exe", url=url)
        )
        send_safe(bot, chat_id, text, reply_markup=markup, parse_mode="Markdown")
    else:
        py_path = project_root / "pc-agent" / "agent.py"
        if py_path.exists():
            with py_path.open("rb") as handle:
                bot.send_document(chat_id, handle, visible_file_name="PCManager_Agent.py", caption="🖥️ Скрипт Агента PCManager (.py) (EXE-файл еще не скомпилирован)")
        else:
            logger.error("Agent file not found! Looked in: %s/releases/agent.exe and %s/pc-agent/agent.py", project_root, project_root)
            send_safe(bot, chat_id, "❌ Файл установщика не найден на сервере. Пожалуйста, обратитесь к администратору.")


def build_bot(token: str, is_admin: bool) -> telebot.TeleBot:
    bot = telebot.TeleBot(token, parse_mode=None)

    if not is_admin:
        @bot.message_handler(commands=["start", "login"])
        def start(message):
            tg_id = getattr(message.from_user, "id", 0)
            username = getattr(message.from_user, "username", None)
            with db_session() as db:
                user = ensure_telegram_user(db, tg_id, username)
                unused_key = db.query(ActivationKey).filter(ActivationKey.user_id == user.id, ActivationKey.is_used == False).order_by(ActivationKey.created_at.desc()).first()
                if unused_key:
                    key = unused_key.key
                else:
                    key = generate_activation_key_for_user(db, user.id)
            
            text = (
                "👋 *Привет! Я — PCManager Bot.*\n"
                "Я помогу тебе настроить удаленное управление твоим ПК и автоматизацию Majestic RP.\n\n"
                f"🔑 *Твой ключ активации:* `{key}`\n"
                "_(Нажми на ключ выше, чтобы мгновенно скопировать его)_\n\n"
                "🖥️ *Инструкция по установке:*\n"
                "1. Скачай программу `PCManager_Agent.exe` по кнопке ниже.\n"
                "2. Запусти её на своем компьютере.\n"
                "3. Введи полученный ключ активации в консоли.\n\n"
                "Программа подключится автоматически!"
            )
            markup = types.InlineKeyboardMarkup()
            markup.row(
                types.InlineKeyboardButton("📥 Скачать Agent.exe", callback_data="saas_download"),
                types.InlineKeyboardButton("🔑 Новый ключ", callback_data="saas_new_key")
            )
            markup.row(
                types.InlineKeyboardButton("🖥️ Мои устройства", callback_data="saas_my_devices")
            )
            send_safe(bot, message.chat.id, text, reply_markup=markup, parse_mode="Markdown")

        def get_saas_agent_for_msg(message, db):
            tg_id = getattr(message.from_user, "id", 0)
            username = getattr(message.from_user, "username", None)
            user = ensure_telegram_user(db, tg_id, username)
            
            parts = (message.text or "").split()
            if len(parts) >= 2:
                if not parts[1].isdigit():
                    agent_id = parts[1]
                    agent = db.query(Agent).filter(Agent.agent_id == agent_id, Agent.user_id == user.id).first()
                    if not agent:
                        return None, f"❌ Устройство с ID '{agent_id}' не найдено или не принадлежит вам."
                    return agent, None

            agents = db.query(Agent).filter(Agent.user_id == user.id).all()
            if not agents:
                return None, "🖥️ *У вас пока нет привязанных устройств.*\n\nЗапустите `PCManager_Agent.exe` и введите ваш ключ активации."
            
            if len(agents) == 1:
                return agents[0], None
            
            lines = ["🖥️ *У вас привязано несколько устройств. Укажите ID устройства после команды:*"]
            for a in agents:
                status_emoji = "🟢" if compute_agent_status(a) == "online" else "🔴"
                lines.append(f"- {status_emoji} `{a.agent_id}` ({a.name})")
            
            cmd = parts[0]
            lines.append(f"\n*Пример:* `{cmd} {agents[0].agent_id}`")
            return None, "\n".join(lines)

        @bot.message_handler(commands=["help"])
        def saas_help_cmd(message):
            text = (
                "👋 *Команды управления PCManager:*\n\n"
                "📸 `/screenshot` — Сделать скриншот экрана\n"
                "📷 `/photo` — Сделать фото с веб-камеры\n"
                "📹 `/video` — Записать видео с вебки (5 сек)\n"
                "📋 `/processes` — Список активных процессов\n"
                "💻 `/sysinfo` — Информация о системе\n"
                "🟢 `/anti_afk_start` — Включить Anti-AFK\n"
                "🔴 `/anti_afk_stop` — Выключить Anti-AFK\n"
                "🟢 `/autoscreen_start` — Включить Автоэкран\n"
                "🔴 `/autoscreen_stop` — Выключить Автоэкран\n"
                "🤖 `/status` — Статус автоматизации\n"
                "🎮 `/launch` — Запустить Majestic / GTA V\n"
                "📊 `/game_status` — Статус запуска игры\n"
                "⌨️ `/key <клавиша>` — Нажатие клавиши (W, A, S, D, Space, Enter, E, Z, Esc, Shift)\n\n"
                "💡 _Если у вас несколько устройств, укажите ID устройства в команде, например:_ `/screenshot client-pc`"
            )
            send_safe(bot, message.chat.id, text, parse_mode="Markdown")

        @bot.message_handler(commands=["screenshot", "screen"])
        def saas_screenshot_cmd(message):
            with db_session() as db:
                agent, err = get_saas_agent_for_msg(message, db)
                if err:
                    send_safe(bot, message.chat.id, err, parse_mode="Markdown")
                    return
                if compute_agent_status(agent) != "online":
                    send_safe(bot, message.chat.id, f"❌ Устройство '{agent.name}' ({agent.agent_id}) не в сети.")
                    return
                try:
                    task = create_task(db, agent, "take_screenshot", {"save_to_server": True, "quality": 80}, "telegram")
                    send_safe(bot, message.chat.id, f"✅ Запрос скриншота отправлен на {agent.name}! Выполняется... (Задача: {task.task_id})")
                except Exception as exc:
                    send_safe(bot, message.chat.id, f"❌ Ошибка отправки команды: {exc}")

        @bot.message_handler(commands=["photo", "camera"])
        def saas_photo_cmd(message):
            with db_session() as db:
                agent, err = get_saas_agent_for_msg(message, db)
                if err:
                    send_safe(bot, message.chat.id, err, parse_mode="Markdown")
                    return
                if compute_agent_status(agent) != "online":
                    send_safe(bot, message.chat.id, f"❌ Устройство '{agent.name}' ({agent.agent_id}) не в сети.")
                    return
                try:
                    task = create_task(db, agent, "camera_snapshot", {"save_to_server": True}, "telegram", confirmed=True)
                    send_safe(bot, message.chat.id, f"✅ Запрос фото с веб-камеры отправлен на {agent.name}! Выполняется... (Задача: {task.task_id})")
                except Exception as exc:
                    send_safe(bot, message.chat.id, f"❌ Ошибка отправки команды: {exc}")

        @bot.message_handler(commands=["video", "recordvideo"])
        def saas_video_cmd(message):
            parts = (message.text or "").split()
            duration = 5
            if len(parts) == 2 and parts[1].isdigit():
                duration = int(parts[1])
            elif len(parts) >= 3 and parts[2].isdigit():
                duration = int(parts[2])
                
            with db_session() as db:
                agent, err = get_saas_agent_for_msg(message, db)
                if err:
                    send_safe(bot, message.chat.id, err, parse_mode="Markdown")
                    return
                if compute_agent_status(agent) != "online":
                    send_safe(bot, message.chat.id, f"❌ Устройство '{agent.name}' ({agent.agent_id}) не в сети.")
                    return
                try:
                    task = create_task(db, agent, "record_video", {"duration_seconds": duration, "save_to_server": True}, "telegram", confirmed=True)
                    send_safe(bot, message.chat.id, f"✅ Запрос на запись видео ({duration} сек) отправлен на {agent.name}! Выполняется... (Задача: {task.task_id})")
                except Exception as exc:
                    send_safe(bot, message.chat.id, f"❌ Ошибка отправки команды: {exc}")

        @bot.message_handler(commands=["processes"])
        def saas_processes_cmd(message):
            with db_session() as db:
                agent, err = get_saas_agent_for_msg(message, db)
                if err:
                    send_safe(bot, message.chat.id, err, parse_mode="Markdown")
                    return
                if compute_agent_status(agent) != "online":
                    send_safe(bot, message.chat.id, f"❌ Устройство '{agent.name}' ({agent.agent_id}) не в сети.")
                    return
                try:
                    task = create_task(db, agent, "get_process_list", {}, "telegram")
                    send_safe(bot, message.chat.id, f"✅ Запрос списка процессов отправлен на {agent.name}! Выполняется... (Задача: {task.task_id})")
                except Exception as exc:
                    send_safe(bot, message.chat.id, f"❌ Ошибка отправки команды: {exc}")

        @bot.message_handler(commands=["sysinfo", "system_info"])
        def saas_sysinfo_cmd(message):
            with db_session() as db:
                agent, err = get_saas_agent_for_msg(message, db)
                if err:
                    send_safe(bot, message.chat.id, err, parse_mode="Markdown")
                    return
                if compute_agent_status(agent) != "online":
                    send_safe(bot, message.chat.id, f"❌ Устройство '{agent.name}' ({agent.agent_id}) не в сети.")
                    return
                try:
                    task = create_task(db, agent, "get_system_info", {}, "telegram")
                    send_safe(bot, message.chat.id, f"✅ Запрос системной информации отправлен на {agent.name}! Выполняется... (Задача: {task.task_id})")
                except Exception as exc:
                    send_safe(bot, message.chat.id, f"❌ Ошибка отправки команды: {exc}")

        @bot.message_handler(commands=["launch", "launch_game"])
        def saas_launch_cmd(message):
            with db_session() as db:
                agent, err = get_saas_agent_for_msg(message, db)
                if err:
                    send_safe(bot, message.chat.id, err, parse_mode="Markdown")
                    return
                if compute_agent_status(agent) != "online":
                    send_safe(bot, message.chat.id, f"❌ Устройство '{agent.name}' ({agent.agent_id}) не в сети.")
                    return
                try:
                    task = create_task(db, agent, "launch_allowed_app", {"app_key": "majestic_launcher"}, "telegram")
                    send_safe(bot, message.chat.id, f"✅ Запрос на запуск Majestic Launcher отправлен на {agent.name}! Выполняется... (Задача: {task.task_id})")
                except Exception as exc:
                    send_safe(bot, message.chat.id, f"❌ Ошибка отправки команды: {exc}")

        @bot.message_handler(commands=["game_status"])
        def saas_game_status_cmd(message):
            with db_session() as db:
                agent, err = get_saas_agent_for_msg(message, db)
                if err:
                    send_safe(bot, message.chat.id, err, parse_mode="Markdown")
                    return
                if compute_agent_status(agent) != "online":
                    send_safe(bot, message.chat.id, f"❌ Устройство '{agent.name}' ({agent.agent_id}) не в сети.")
                    return
                try:
                    task = create_task(db, agent, "game_status", {}, "telegram")
                    send_safe(bot, message.chat.id, f"✅ Запрос статуса игры отправлен на {agent.name}! Выполняется... (Задача: {task.task_id})")
                except Exception as exc:
                    send_safe(bot, message.chat.id, f"❌ Ошибка отправки команды: {exc}")

        @bot.message_handler(commands=["key", "press"])
        def saas_key_cmd(message):
            parts = (message.text or "").split()
            if len(parts) < 2:
                send_safe(bot, message.chat.id, "Формат: `/key KEY` или `/key AGENT_ID KEY` (W, A, S, D, Space, Enter, E, Z, Esc, Shift)", parse_mode="Markdown")
                return
            
            with db_session() as db:
                tg_id = getattr(message.from_user, "id", 0)
                username = getattr(message.from_user, "username", None)
                user = ensure_telegram_user(db, tg_id, username)
                
                agent = None
                key = None
                if len(parts) >= 3:
                    agent_id = parts[1]
                    key = parts[2].lower().strip()
                    agent = db.query(Agent).filter(Agent.agent_id == agent_id, Agent.user_id == user.id).first()
                    if not agent:
                        send_safe(bot, message.chat.id, f"❌ Устройство с ID '{agent_id}' не найдено или не принадлежит вам.")
                        return
                else:
                    key = parts[1].lower().strip()
                    agents = db.query(Agent).filter(Agent.user_id == user.id).all()
                    if not agents:
                        send_safe(bot, message.chat.id, "🖥️ *У вас пока нет привязанных устройств.*")
                        return
                    if len(agents) == 1:
                        agent = agents[0]
                    else:
                        lines = ["🖥️ *У вас привязано несколько устройств. Укажите ID устройства:*"]
                        for a in agents:
                            lines.append(f"- `{a.agent_id}` ({a.name})")
                        lines.append(f"\n*Пример:* `/key {agents[0].agent_id} {key}`")
                        send_safe(bot, message.chat.id, "\n".join(lines), parse_mode="Markdown")
                        return
                
                if key not in {"w", "a", "s", "d", "z", "e", "esc", "space", "enter", "tab", "shift"}:
                    send_safe(bot, message.chat.id, "❌ Недопустимая клавиша. Разрешены: W, A, S, D, Z, E, Esc, Space, Enter, Tab, Shift")
                    return
                
                if compute_agent_status(agent) != "online":
                    send_safe(bot, message.chat.id, f"❌ Устройство '{agent.name}' ({agent.agent_id}) не в сети.")
                    return
                
                try:
                    task = create_task(db, agent, "press_key", {"key": key}, "telegram")
                    send_safe(bot, message.chat.id, f"✅ Клавиша '{key.upper()}' успешно отправлена на {agent.name}! (Задача: {task.task_id})")
                except Exception as exc:
                    send_safe(bot, message.chat.id, f"❌ Ошибка отправки клавиши: {exc}")

        @bot.message_handler(commands=["release_keys"])
        def saas_release_keys_cmd(message):
            with db_session() as db:
                agent, err = get_saas_agent_for_msg(message, db)
                if err:
                    send_safe(bot, message.chat.id, err, parse_mode="Markdown")
                    return
                if compute_agent_status(agent) != "online":
                    send_safe(bot, message.chat.id, f"❌ Устройство '{agent.name}' ({agent.agent_id}) не в сети.")
                    return
                try:
                    task = create_task(db, agent, "release_keys", {}, "telegram")
                    send_safe(bot, message.chat.id, f"✅ Запрос отпускания клавиш отправлен на {agent.name}! (Задача: {task.task_id})")
                except Exception as exc:
                    send_safe(bot, message.chat.id, f"❌ Ошибка отправки команды: {exc}")

        @bot.message_handler(commands=["volume_up", "volume_down"])
        def saas_volume_cmd(message):
            cmd = (message.text or "").split()[0].lstrip("/")
            with db_session() as db:
                agent, err = get_saas_agent_for_msg(message, db)
                if err:
                    send_safe(bot, message.chat.id, err, parse_mode="Markdown")
                    return
                if compute_agent_status(agent) != "online":
                    send_safe(bot, message.chat.id, f"❌ Устройство '{agent.name}' ({agent.agent_id}) не в сети.")
                    return
                try:
                    task = create_task(db, agent, cmd, {}, "telegram")
                    send_safe(bot, message.chat.id, f"✅ Запрос изменения громкости ({cmd}) отправлен на {agent.name}! (Задача: {task.task_id})")
                except Exception as exc:
                    send_safe(bot, message.chat.id, f"❌ Ошибка отправки команды: {exc}")

        @bot.message_handler(commands=["desktop_left", "desktop_right"])
        def saas_desktop_cmd(message):
            cmd = (message.text or "").split()[0].lstrip("/")
            with db_session() as db:
                agent, err = get_saas_agent_for_msg(message, db)
                if err:
                    send_safe(bot, message.chat.id, err, parse_mode="Markdown")
                    return
                if compute_agent_status(agent) != "online":
                    send_safe(bot, message.chat.id, f"❌ Устройство '{agent.name}' ({agent.agent_id}) не в сети.")
                    return
                try:
                    task = create_task(db, agent, cmd, {}, "telegram")
                    send_safe(bot, message.chat.id, f"✅ Запрос переключения рабочего стола ({cmd}) отправлен на {agent.name}! (Задача: {task.task_id})")
                except Exception as exc:
                    send_safe(bot, message.chat.id, f"❌ Ошибка отправки команды: {exc}")

        @bot.message_handler(commands=["anti_afk_start"])
        def saas_anti_afk_start_cmd(message):
            parts = (message.text or "").split()
            min_minutes = 10
            max_minutes = 20
            if len(parts) >= 2:
                if parts[1].isdigit():
                    min_minutes = int(parts[1])
                    if len(parts) >= 3 and parts[2].isdigit():
                        max_minutes = int(parts[2])
                elif len(parts) >= 3 and parts[2].isdigit():
                    min_minutes = int(parts[2])
                    if len(parts) >= 4 and parts[3].isdigit():
                        max_minutes = int(parts[3])
                        
            with db_session() as db:
                agent, err = get_saas_agent_for_msg(message, db)
                if err:
                    send_safe(bot, message.chat.id, err, parse_mode="Markdown")
                    return
                if compute_agent_status(agent) != "online":
                    send_safe(bot, message.chat.id, f"❌ Устройство '{agent.name}' ({agent.agent_id}) не в сети.")
                    return
                try:
                    task = create_task(db, agent, "anti_afk_start", {"min_minutes": min_minutes, "max_minutes": max(max_minutes, min_minutes)}, "telegram")
                    send_safe(bot, message.chat.id, f"✅ Запрос запуска Anti-AFK ({min_minutes}-{max_minutes} мин) отправлен на {agent.name}! (Задача: {task.task_id})")
                except Exception as exc:
                    send_safe(bot, message.chat.id, f"❌ Ошибка запуска Anti-AFK: {exc}")

        @bot.message_handler(commands=["anti_afk_stop"])
        def saas_anti_afk_stop_cmd(message):
            with db_session() as db:
                agent, err = get_saas_agent_for_msg(message, db)
                if err:
                    send_safe(bot, message.chat.id, err, parse_mode="Markdown")
                    return
                if compute_agent_status(agent) != "online":
                    send_safe(bot, message.chat.id, f"❌ Устройство '{agent.name}' ({agent.agent_id}) не в сети.")
                    return
                try:
                    task = create_task(db, agent, "anti_afk_stop", {}, "telegram")
                    send_safe(bot, message.chat.id, f"✅ Запрос остановки Anti-AFK отправлен на {agent.name}! (Задача: {task.task_id})")
                except Exception as exc:
                    send_safe(bot, message.chat.id, f"❌ Ошибка остановки Anti-AFK: {exc}")

        @bot.message_handler(commands=["autoscreen_start"])
        def saas_autoscreen_start_cmd(message):
            parts = (message.text or "").split()
            interval = 300
            if len(parts) == 2 and parts[1].isdigit():
                interval = int(parts[1])
            elif len(parts) >= 3 and parts[2].isdigit():
                interval = int(parts[2])
                
            with db_session() as db:
                agent, err = get_saas_agent_for_msg(message, db)
                if err:
                    send_safe(bot, message.chat.id, err, parse_mode="Markdown")
                    return
                if compute_agent_status(agent) != "online":
                    send_safe(bot, message.chat.id, f"❌ Устройство '{agent.name}' ({agent.agent_id}) не в сети.")
                    return
                try:
                    task = create_task(db, agent, "auto_screen_start", {"interval_seconds": max(60, interval)}, "telegram")
                    send_safe(bot, message.chat.id, f"✅ Запрос запуска Автоэкрана (каждые {interval} сек) отправлен на {agent.name}! (Задача: {task.task_id})")
                except Exception as exc:
                    send_safe(bot, message.chat.id, f"❌ Ошибка запуска Автоэкрана: {exc}")

        @bot.message_handler(commands=["autoscreen_stop"])
        def saas_autoscreen_stop_cmd(message):
            with db_session() as db:
                agent, err = get_saas_agent_for_msg(message, db)
                if err:
                    send_safe(bot, message.chat.id, err, parse_mode="Markdown")
                    return
                if compute_agent_status(agent) != "online":
                    send_safe(bot, message.chat.id, f"❌ Устройство '{agent.name}' ({agent.agent_id}) не в сети.")
                    return
                try:
                    task = create_task(db, agent, "auto_screen_stop", {}, "telegram")
                    send_safe(bot, message.chat.id, f"✅ Запрос остановки Автоэкрана отправлен на {agent.name}! (Задача: {task.task_id})")
                except Exception as exc:
                    send_safe(bot, message.chat.id, f"❌ Ошибка остановки Автоэкрана: {exc}")

        @bot.message_handler(commands=["status", "devices"])
        def saas_status_cmd(message):
            with db_session() as db:
                tg_id = getattr(message.from_user, "id", 0)
                username = getattr(message.from_user, "username", None)
                user = ensure_telegram_user(db, tg_id, username)
                
                agents = db.query(Agent).filter(Agent.user_id == user.id).all()
                if not agents:
                    text = "🖥️ *У вас пока нет привязанных устройств.*\n\nЗапустите `PCManager_Agent.exe` и введите ваш ключ активации."
                    send_safe(bot, message.chat.id, text, parse_mode="Markdown")
                    return
                
                lines = ["🖥️ *Ваши устройства:*"]
                for agent in agents:
                    status = compute_agent_status(agent)
                    status_emoji = "🟢" if status == "online" else "🔴"
                    lines.append(
                        f"\n• *{agent.name}* (`{agent.agent_id}`)"
                        f"\n  └ Статус: {status_emoji} {status}"
                        f"\n  └ ОС: {agent.platform} | Версия: {agent.version}"
                        f"\n  └ Активность: {agent.last_seen_at.strftime('%Y-%m-%d %H:%M:%S') if agent.last_seen_at else '-'}"
                    )
                send_safe(bot, message.chat.id, "\n".join(lines), parse_mode="Markdown")

        @bot.callback_query_handler(func=lambda call: True)
        def callback_handler(call):
            data = call.data or ""
            if data.startswith("saas_"):
                answer_callback(bot, call)
                tg_id = getattr(call.from_user, "id", 0)
                username = getattr(call.from_user, "username", None)
                with db_session() as db:
                    user = ensure_telegram_user(db, tg_id, username)
                    if data == "saas_new_key":
                        key = generate_activation_key_for_user(db, user.id)
                        text = (
                            "🔑 *Твой новый ключ активации:* `{}`\n"
                            "_(Нажми на ключ выше, чтобы скопировать)_\n\n"
                            "Введи его в запущенном `PCManager_Agent.exe` для автоматической привязки."
                        ).format(key)
                        markup = types.InlineKeyboardMarkup()
                        markup.row(
                            types.InlineKeyboardButton("📥 Скачать Agent.exe", callback_data="saas_download"),
                            types.InlineKeyboardButton("🖥️ Мои устройства", callback_data="saas_my_devices")
                        )
                        send_safe(bot, call.message.chat.id, text, reply_markup=markup, parse_mode="Markdown")
                    elif data == "saas_download":
                        send_agent_file(bot, call.message.chat.id)
                    elif data == "saas_my_devices":
                        agents = db.query(Agent).filter(Agent.user_id == user.id).all()
                        markup = types.InlineKeyboardMarkup()
                        if not agents:
                            text = "🖥️ *У тебя пока нет привязанных устройств.*\n\nЗапусти `PCManager_Agent.exe` и введи свой ключ активации."
                        else:
                            text = "🖥️ *Выбери устройство для управления:*"
                            for a in agents:
                                status_emoji = "🟢" if compute_agent_status(a) == "online" else "🔴"
                                markup.row(types.InlineKeyboardButton(f"{status_emoji} {a.name} ({a.agent_id})", callback_data=f"saas_panel:{a.agent_id}"))
                        
                        markup.row(
                            types.InlineKeyboardButton("🔑 Получить новый ключ", callback_data="saas_new_key"),
                            types.InlineKeyboardButton("📥 Скачать Agent.exe", callback_data="saas_download")
                        )
                        send_safe(bot, call.message.chat.id, text, reply_markup=markup, parse_mode="Markdown")
                    elif data.startswith("saas_panel:"):
                        agent_id = data.split(":", 1)[1]
                        agent = db.query(Agent).filter(Agent.agent_id == agent_id, Agent.user_id == user.id).first()
                        if not agent:
                            send_safe(bot, call.message.chat.id, "❌ Устройство не найдено.")
                            return
                        status = compute_agent_status(agent)
                        status_emoji = "🟢" if status == "online" else "🔴"
                        text = (
                            f"🖥️ *Управление устройством: {agent.name}*\n"
                            f"└ ID: `{agent.agent_id}`\n"
                            f"└ Статус: {status_emoji} {status}\n"
                            f"└ ОС: {agent.platform} | Версия: {agent.version}\n"
                            f"└ IP: {agent.local_ip or '-'}\n"
                            f"└ Текущая задача: {agent.current_task or 'нет'}\n"
                            f"└ Активность: {agent.last_seen_at.strftime('%Y-%m-%d %H:%M:%S') if agent.last_seen_at else '-'}"
                        )
                        markup = types.InlineKeyboardMarkup()
                        if status == "online":
                            markup.row(
                                types.InlineKeyboardButton("📸 Скриншот", callback_data=f"saas_action:{agent_id}:take_screenshot"),
                                types.InlineKeyboardButton("💻 Система", callback_data=f"saas_action:{agent_id}:get_system_info")
                            )
                            markup.row(
                                types.InlineKeyboardButton("📋 Процессы", callback_data=f"saas_action:{agent_id}:get_process_list"),
                                types.InlineKeyboardButton("📹 Вебка / Камера", callback_data=f"saas_cam:{agent_id}")
                            )
                            markup.row(
                                types.InlineKeyboardButton("🎥 Запись экрана", callback_data=f"saas_screen_rec:{agent_id}"),
                                types.InlineKeyboardButton("⌨️ Клавиатура", callback_data=f"saas_keys:{agent_id}")
                            )
                            markup.row(
                                types.InlineKeyboardButton("🤖 Автоматизация", callback_data=f"saas_auto:{agent_id}"),
                                types.InlineKeyboardButton("🔌 Питание", callback_data=f"saas_power:{agent_id}")
                            )
                            markup.row(
                                types.InlineKeyboardButton("🎮 Игры / Лаунчеры", callback_data=f"saas_games:{agent_id}")
                            )
                            markup.row(
                                types.InlineKeyboardButton("🛋️ Пульт", callback_data=f"saas_remote:{agent_id}"),
                                types.InlineKeyboardButton("⏰ Таймер", callback_data=f"saas_timer:{agent_id}")
                            )
                        else:
                            markup.row(types.InlineKeyboardButton("💤 Устройство не в сети", callback_data="saas_noop"))
                        markup.row(
                            types.InlineKeyboardButton("🔄 Обновить", callback_data=f"saas_panel:{agent_id}"),
                            types.InlineKeyboardButton("◀️ Назад к списку", callback_data="saas_my_devices")
                        )
                        send_safe(bot, call.message.chat.id, text, reply_markup=markup, parse_mode="Markdown")
                    elif data.startswith("saas_keys:"):
                        agent_id = data.split(":", 1)[1]
                        agent = db.query(Agent).filter(Agent.agent_id == agent_id, Agent.user_id == user.id).first()
                        if not agent:
                            send_safe(bot, call.message.chat.id, "❌ Устройство не найдено.")
                            return
                        text = f"⌨️ *Эмуляция клавиш для {agent.name}:*\nВыбери клавишу для нажатия:"
                        markup = types.InlineKeyboardMarkup()
                        markup.row(
                            types.InlineKeyboardButton("W", callback_data=f"saas_press:{agent_id}:w"),
                            types.InlineKeyboardButton("A", callback_data=f"saas_press:{agent_id}:a"),
                            types.InlineKeyboardButton("S", callback_data=f"saas_press:{agent_id}:s"),
                            types.InlineKeyboardButton("D", callback_data=f"saas_press:{agent_id}:d")
                        )
                        markup.row(
                            types.InlineKeyboardButton("Space (Пробел)", callback_data=f"saas_press:{agent_id}:space"),
                            types.InlineKeyboardButton("Enter (Ввод)", callback_data=f"saas_press:{agent_id}:enter")
                        )
                        markup.row(
                            types.InlineKeyboardButton("E", callback_data=f"saas_press:{agent_id}:e"),
                            types.InlineKeyboardButton("Z", callback_data=f"saas_press:{agent_id}:z"),
                            types.InlineKeyboardButton("Esc", callback_data=f"saas_press:{agent_id}:esc"),
                            types.InlineKeyboardButton("Shift", callback_data=f"saas_press:{agent_id}:shift")
                        )
                        markup.row(types.InlineKeyboardButton("◀️ Назад в меню устройства", callback_data=f"saas_panel:{agent_id}"))
                        send_safe(bot, call.message.chat.id, text, reply_markup=markup, parse_mode="Markdown")
                    elif data.startswith("saas_cam:"):
                        agent_id = data.split(":", 1)[1]
                        agent = db.query(Agent).filter(Agent.agent_id == agent_id, Agent.user_id == user.id).first()
                        if not agent:
                            send_safe(bot, call.message.chat.id, "❌ Устройство не найдено.")
                            return
                        text = f"📹 *Управление камерой для {agent.name}:*"
                        markup = types.InlineKeyboardMarkup()
                        markup.row(
                            types.InlineKeyboardButton("📸 Сделать фото", callback_data=f"saas_action:{agent_id}:take_photo"),
                            types.InlineKeyboardButton("📹 Видео (5с)", callback_data=f"saas_action:{agent_id}:record_video_5")
                        )
                        markup.row(
                            types.InlineKeyboardButton("📹 Видео (10с)", callback_data=f"saas_action:{agent_id}:record_video_10"),
                            types.InlineKeyboardButton("📹 Видео (30с)", callback_data=f"saas_action:{agent_id}:record_video_30")
                        )
                        markup.row(types.InlineKeyboardButton("◀️ Назад в меню устройства", callback_data=f"saas_panel:{agent_id}"))
                        send_safe(bot, call.message.chat.id, text, reply_markup=markup, parse_mode="Markdown")
                    elif data.startswith("saas_screen_rec:"):
                        agent_id = data.split(":", 1)[1]
                        agent = db.query(Agent).filter(Agent.agent_id == agent_id, Agent.user_id == user.id).first()
                        if not agent:
                            send_safe(bot, call.message.chat.id, "❌ Устройство не найдено.")
                            return
                        text = f"🎥 *Запись экрана для {agent.name}:*\nВыбери длительность записи:"
                        markup = types.InlineKeyboardMarkup()
                        markup.row(
                            types.InlineKeyboardButton("🎥 Экран (5с)", callback_data=f"saas_action:{agent_id}:record_screen_5"),
                            types.InlineKeyboardButton("🎥 Экран (10с)", callback_data=f"saas_action:{agent_id}:record_screen_10")
                        )
                        markup.row(
                            types.InlineKeyboardButton("🎥 Экран (30с)", callback_data=f"saas_action:{agent_id}:record_screen_30")
                        )
                        markup.row(types.InlineKeyboardButton("◀️ Назад в меню устройства", callback_data=f"saas_panel:{agent_id}"))
                        send_safe(bot, call.message.chat.id, text, reply_markup=markup, parse_mode="Markdown")
                    elif data.startswith("saas_auto:"):
                        agent_id = data.split(":", 1)[1]
                        agent = db.query(Agent).filter(Agent.agent_id == agent_id, Agent.user_id == user.id).first()
                        if not agent:
                            send_safe(bot, call.message.chat.id, "❌ Устройство не найдено.")
                            return
                        sys_info = agent.system_info or {}
                        rules = sys_info.get("automation_rules", [])
                        
                        text = f"🤖 *Управление автоматизацией для {agent.name}:*\n\n"
                        text += "*Базовые службы:*\n"
                        text += "• Anti-AFK (имитация присутствия)\n"
                        text += "• Автоэкран (периодические скриншоты)\n\n"
                        
                        markup = types.InlineKeyboardMarkup()
                        markup.row(
                            types.InlineKeyboardButton("🟢 Старт Anti-AFK", callback_data=f"saas_action:{agent_id}:anti_afk_start"),
                            types.InlineKeyboardButton("🔴 Стоп Anti-AFK", callback_data=f"saas_action:{agent_id}:anti_afk_stop")
                        )
                        markup.row(
                            types.InlineKeyboardButton("📸 Старт Автоэкран", callback_data=f"saas_action:{agent_id}:autoscreen_start"),
                            types.InlineKeyboardButton("🔴 Стоп Автоэкран", callback_data=f"saas_action:{agent_id}:autoscreen_stop")
                        )
                        
                        text += "*Активные правила:* \n"
                        if rules:
                            for idx, rule in enumerate(rules):
                                r_id = rule.get("id")
                                name = rule.get("name", "Правило")
                                trigger = rule.get("trigger", "time")
                                r_time = rule.get("time", "22:00")
                                action = rule.get("action", "sleep_pc")
                                action_label = {"sleep_pc": "💤 Сон", "lock_pc": "🔒 Блок", "monitor_off": "🖥️ Погаснуть", "screenshot": "📸 Скриншот"}.get(action, action)
                                
                                if trigger == "startup":
                                    desc = f"{idx+1}. {name}: [При старте] ➡️ {action_label}"
                                else:
                                    desc = f"{idx+1}. {name}: [В {r_time}] ➡️ {action_label}"
                                text += f"• {desc}\n"
                                markup.row(
                                    types.InlineKeyboardButton(f"🗑️ Удалить #{idx+1}", callback_data=f"saas_del_rule:{agent_id}:{r_id}")
                                )
                        else:
                            text += "_Правила автоматизации по расписанию не добавлены._\n"
                            
                        text += "\n*Добавить готовые правила:* \n"
                        markup.row(
                            types.InlineKeyboardButton("💤 Сон в 22:00", callback_data=f"saas_add_rule:{agent_id}:sleep_2200"),
                            types.InlineKeyboardButton("🖥️ Погаснуть в 23:00", callback_data=f"saas_add_rule:{agent_id}:mon_2300")
                        )
                        markup.row(
                            types.InlineKeyboardButton("🔒 Блок в 18:00", callback_data=f"saas_add_rule:{agent_id}:lock_1800"),
                            types.InlineKeyboardButton("📸 Скрин при старте", callback_data=f"saas_add_rule:{agent_id}:scr_boot")
                        )
                        markup.row(types.InlineKeyboardButton("◀️ Назад в меню устройства", callback_data=f"saas_panel:{agent_id}"))
                        send_safe(bot, call.message.chat.id, text, reply_markup=markup, parse_mode="Markdown")
                        
                    elif data.startswith("saas_add_rule:"):
                        _, agent_id, preset = data.split(":", 2)
                        agent = db.query(Agent).filter(Agent.agent_id == agent_id, Agent.user_id == user.id).first()
                        if not agent:
                            send_safe(bot, call.message.chat.id, "❌ Устройство не найдено.")
                            return
                        payload = {}
                        if preset == "sleep_2200":
                            payload = {"name": "Сон в 22:00", "trigger": "time", "time": "22:00", "action": "sleep_pc"}
                        elif preset == "mon_2300":
                            payload = {"name": "Экран в 23:00", "trigger": "time", "time": "23:00", "action": "monitor_off"}
                        elif preset == "lock_1800":
                            payload = {"name": "Блок в 18:00", "trigger": "time", "time": "18:00", "action": "lock_pc"}
                        elif preset == "scr_boot":
                            payload = {"name": "Скриншот при старте", "trigger": "startup", "action": "screenshot"}
                        try:
                            task = create_task(db, agent, "add_automation_rule", payload, "telegram", confirmed=True)
                            bot.answer_callback_query(call.id, "✅ Задача отправлена на ПК!")
                            time.sleep(0.5)
                            create_task(db, agent, "system_info", {}, "telegram", confirmed=True)
                            time.sleep(0.2)
                            send_safe(bot, call.message.chat.id, f"✅ Правило автоматизации отправлено на ПК! (Задача: {task.task_id})\nПожалуйста, нажмите «Обновить» через несколько секунд для обновления списка.", reply_markup=types.InlineKeyboardMarkup().row(
                                types.InlineKeyboardButton("🔄 Обновить правила", callback_data=f"saas_auto:{agent_id}"),
                                types.InlineKeyboardButton("◀️ Вернуться к панели", callback_data=f"saas_panel:{agent_id}")
                            ))
                        except Exception as exc:
                            send_safe(bot, call.message.chat.id, f"❌ Ошибка добавления правила: {exc}")
                            
                    elif data.startswith("saas_del_rule:"):
                        _, agent_id, rule_id = data.split(":", 2)
                        agent = db.query(Agent).filter(Agent.agent_id == agent_id, Agent.user_id == user.id).first()
                        if not agent:
                            send_safe(bot, call.message.chat.id, "❌ Устройство не найдено.")
                            return
                        try:
                            task = create_task(db, agent, "delete_automation_rule", {"id": rule_id}, "telegram", confirmed=True)
                            bot.answer_callback_query(call.id, "✅ Задача удаления отправлена на ПК!")
                            time.sleep(0.5)
                            create_task(db, agent, "system_info", {}, "telegram", confirmed=True)
                            send_safe(bot, call.message.chat.id, f"✅ Задача на удаление правила отправлена на ПК! (Задача: {task.task_id})\nПожалуйста, нажмите «Обновить» через несколько секунд для обновления списка.", reply_markup=types.InlineKeyboardMarkup().row(
                                types.InlineKeyboardButton("🔄 Обновить правила", callback_data=f"saas_auto:{agent_id}"),
                                types.InlineKeyboardButton("◀️ Вернуться к панели", callback_data=f"saas_panel:{agent_id}")
                            ))
                        except Exception as exc:
                            send_safe(bot, call.message.chat.id, f"❌ Ошибка удаления правила: {exc}")
                    elif data.startswith("saas_power:"):
                        agent_id = data.split(":", 1)[1]
                        agent = db.query(Agent).filter(Agent.agent_id == agent_id, Agent.user_id == user.id).first()
                        if not agent:
                            send_safe(bot, call.message.chat.id, "❌ Устройство не найдено.")
                            return
                        text = f"🔌 *Управление питанием для {agent.name}:*\nВыбери действие:"
                        markup = types.InlineKeyboardMarkup()
                        markup.row(
                            types.InlineKeyboardButton("🔒 Заблокировать", callback_data=f"saas_action:{agent_id}:lock_pc"),
                            types.InlineKeyboardButton("💤 Спящий режим", callback_data=f"saas_action:{agent_id}:sleep_pc")
                        )
                        markup.row(
                            types.InlineKeyboardButton("🖥️ Погасить монитор", callback_data=f"saas_action:{agent_id}:monitor_off")
                        )
                        markup.row(
                            types.InlineKeyboardButton("🔴 Выключить ПК", callback_data=f"saas_action:{agent_id}:shutdown_now")
                        )
                        markup.row(types.InlineKeyboardButton("◀️ Назад в меню устройства", callback_data=f"saas_panel:{agent_id}"))
                        send_safe(bot, call.message.chat.id, text, reply_markup=markup, parse_mode="Markdown")
                    elif data.startswith("saas_games:"):
                        agent_id = data.split(":", 1)[1]
                        agent = db.query(Agent).filter(Agent.agent_id == agent_id, Agent.user_id == user.id).first()
                        if not agent:
                            send_safe(bot, call.message.chat.id, "❌ Устройство не найдено.")
                            return
                        sys_info = agent.system_info or {}
                        games_list = sys_info.get("games_list", [])
                        text = f"🎮 *Игротека для {agent.name}:*\n"
                        markup = types.InlineKeyboardMarkup()
                        if games_list:
                            text += "Доступные игры (Steam, Epic & RP):\n"
                            for game in games_list:
                                title = game.get("title", "Неизвестная игра")
                                store = str(game.get("store", "steam")).upper()
                                playtime = game.get("playtime_hours", 0.0)
                                game_key = title.lower().strip().replace(" ", "_").replace("-", "_")
                                if store == "STEAM" and playtime > 0:
                                    playtime_str = f" ⏳ В игре: {playtime} ч."
                                else:
                                    playtime_str = ""
                                text += f"\n• *{title}* [{store}]{playtime_str}"
                                markup.row(
                                    types.InlineKeyboardButton(f"🕹️ Старт {title[:12]}", callback_data=f"saas_launch_app:{agent_id}:{game_key}"),
                                    types.InlineKeyboardButton("⏹️ Закрыть", callback_data=f"saas_close_app:{agent_id}:{game_key}")
                                )
                        else:
                            launchers = sys_info.get("launchers", [])
                            if launchers:
                                for launcher_key in launchers:
                                    label = launcher_key.replace("_", " ").title()
                                    markup.row(
                                        types.InlineKeyboardButton(f"🕹️ {label}", callback_data=f"saas_launch_app:{agent_id}:{launcher_key}"),
                                        types.InlineKeyboardButton("⏹️ Закрыть", callback_data=f"saas_close_app:{agent_id}:{launcher_key}")
                                    )
                            else:
                                text += "\n\n_Игры не обнаружены. Убедитесь, что лаунчеры установлены, и обновите статус._"
                                markup.row(types.InlineKeyboardButton("🔄 Обновить статус", callback_data=f"saas_action:{agent_id}:get_system_info"))
                        markup.row(types.InlineKeyboardButton("◀️ Назад в меню устройства", callback_data=f"saas_panel:{agent_id}"))
                        send_safe(bot, call.message.chat.id, text, reply_markup=markup, parse_mode="Markdown")
                    elif data.startswith("saas_launch_app:"):
                        _, agent_id, launcher_key = data.split(":", 2)
                        agent = db.query(Agent).filter(Agent.agent_id == agent_id, Agent.user_id == user.id).first()
                        if not agent:
                            send_safe(bot, call.message.chat.id, "❌ Устройство не найдено.")
                            return
                        try:
                            task = create_task(db, agent, "launch_allowed_app", {"app_key": launcher_key}, "telegram", confirmed=True)
                            send_safe(
                                bot,
                                call.message.chat.id,
                                f"✅ Команда запуска '{launcher_key.replace('_', ' ').title()}' отправлена! (Задача: {task.task_id})",
                                reply_markup=types.InlineKeyboardMarkup().row(types.InlineKeyboardButton("◀️ Назад к играм", callback_data=f"saas_games:{agent_id}"))
                            )
                        except Exception as exc:
                            send_safe(bot, call.message.chat.id, f"❌ Ошибка запуска: {exc}")
                    elif data.startswith("saas_close_app:"):
                        _, agent_id, launcher_key = data.split(":", 2)
                        agent = db.query(Agent).filter(Agent.agent_id == agent_id, Agent.user_id == user.id).first()
                        if not agent:
                            send_safe(bot, call.message.chat.id, "❌ Устройство не найдено.")
                            return
                        try:
                            task = create_task(db, agent, "close_allowed_app", {"app_key": launcher_key}, "telegram", confirmed=True)
                            send_safe(
                                bot,
                                call.message.chat.id,
                                f"✅ Команда закрытия '{launcher_key.replace('_', ' ').title()}' отправлена! (Задача: {task.task_id})",
                                reply_markup=types.InlineKeyboardMarkup().row(types.InlineKeyboardButton("◀️ Назад к играм", callback_data=f"saas_games:{agent_id}"))
                            )
                        except Exception as exc:
                            send_safe(bot, call.message.chat.id, f"❌ Ошибка закрытия: {exc}")
                    elif data == "saas_noop":
                        pass
                    elif data.startswith("saas_press:"):
                        _, agent_id, key = data.split(":", 2)
                        agent = db.query(Agent).filter(Agent.agent_id == agent_id, Agent.user_id == user.id).first()
                        if not agent:
                            send_safe(bot, call.message.chat.id, "❌ Устройство не найдено.")
                            return
                        try:
                            task = create_task(db, agent, "press_key", {"key": key}, "telegram")
                            send_safe(
                                bot,
                                call.message.chat.id,
                                f"✅ Клавиша '{key.upper()}' успешно отправлена на {agent.name}! (Задача: {task.task_id})",
                                reply_markup=types.InlineKeyboardMarkup().row(types.InlineKeyboardButton("◀️ Назад к клавиатуре", callback_data=f"saas_keys:{agent_id}"))
                            )
                        except Exception as exc:
                            send_safe(bot, call.message.chat.id, f"❌ Ошибка отправки клавиши: {exc}")
                    elif data.startswith("saas_action:"):
                        _, agent_id, action = data.split(":", 2)
                        agent = db.query(Agent).filter(Agent.agent_id == agent_id, Agent.user_id == user.id).first()
                        if not agent:
                            send_safe(bot, call.message.chat.id, "❌ Устройство не найдено.")
                            return
                        action_payloads = {
                            "take_screenshot": ("take_screenshot", {"save_to_server": True, "quality": 80}),
                            "get_system_info": ("get_system_info", {}),
                            "get_process_list": ("get_process_list", {}),
                            "anti_afk_start": ("anti_afk_start", {}),
                            "anti_afk_stop": ("anti_afk_stop", {}),
                            "autoscreen_start": ("autoscreen_start", {}),
                            "autoscreen_stop": ("autoscreen_stop", {}),
                            "take_photo": ("camera_snapshot", {"save_to_server": True}),
                            "record_video_5": ("record_video", {"duration_seconds": 5, "save_to_server": True}),
                            "record_video_10": ("record_video", {"duration_seconds": 10, "save_to_server": True}),
                            "record_video_30": ("record_video", {"duration_seconds": 30, "save_to_server": True}),
                            "record_screen_5": ("record_screen", {"duration_seconds": 5, "save_to_server": True}),
                            "record_screen_10": ("record_screen", {"duration_seconds": 10, "save_to_server": True}),
                            "record_screen_30": ("record_screen", {"duration_seconds": 30, "save_to_server": True}),
                            "lock_pc": ("lock_pc", {}),
                            "sleep_pc": ("sleep_pc", {}),
                            "monitor_off": ("monitor_off", {}),
                            "shutdown_now": ("shutdown_now", {}),
                        }
                        if action not in action_payloads:
                            send_safe(bot, call.message.chat.id, "❌ Неизвестное действие.")
                            return
                        act_type, payload = action_payloads[action]
                        try:
                            task = create_task(db, agent, act_type, payload, "telegram", confirmed=True)
                            send_safe(
                                bot,
                                call.message.chat.id,
                                f"✅ Команда отправлена на {agent.name}! Выполняется... (Задача: {task.task_id})",
                                reply_markup=types.InlineKeyboardMarkup().row(types.InlineKeyboardButton("◀️ Вернуться в панель", callback_data=f"saas_panel:{agent_id}"))
                            )
                        except Exception as exc:
                            send_safe(bot, call.message.chat.id, f"❌ Ошибка отправки команды: {exc}")
                    elif data.startswith("saas_remote:"):
                        agent_id = data.split(":", 1)[1]
                        agent = db.query(Agent).filter(Agent.agent_id == agent_id, Agent.user_id == user.id).first()
                        if not agent:
                            send_safe(bot, call.message.chat.id, "❌ Устройство не найдено.")
                            return
                        text = f"🛋️ *Виртуальный пульт управления для {agent.name}:*\nВы можете управлять курсором мыши, кликами и медиаплеером."
                        markup = types.InlineKeyboardMarkup()
                        
                        markup.row(
                            types.InlineKeyboardButton("📜 Вверх", callback_data=f"saas_remote_action:{agent_id}:scroll_up"),
                            types.InlineKeyboardButton("⬆️ Вверх", callback_data=f"saas_remote_action:{agent_id}:move_up"),
                            types.InlineKeyboardButton("🖱️ 2x ЛКМ", callback_data=f"saas_remote_action:{agent_id}:click_double")
                        )
                        markup.row(
                            types.InlineKeyboardButton("◀️ Влево", callback_data=f"saas_remote_action:{agent_id}:move_left"),
                            types.InlineKeyboardButton("🖱️ ЛКМ", callback_data=f"saas_remote_action:{agent_id}:click_left"),
                            types.InlineKeyboardButton("🖱️ ПКМ", callback_data=f"saas_remote_action:{agent_id}:click_right"),
                            types.InlineKeyboardButton("▶️ Вправо", callback_data=f"saas_remote_action:{agent_id}:move_right")
                        )
                        markup.row(
                            types.InlineKeyboardButton("📜 Вниз", callback_data=f"saas_remote_action:{agent_id}:scroll_down"),
                            types.InlineKeyboardButton("⬇️ Вниз", callback_data=f"saas_remote_action:{agent_id}:move_down"),
                            types.InlineKeyboardButton("⌨️ Текст", callback_data=f"saas_remote_type:{agent_id}")
                        )
                        markup.row(
                            types.InlineKeyboardButton("⏯️ Пауза", callback_data=f"saas_remote_action:{agent_id}:play_pause"),
                            types.InlineKeyboardButton("🔇 Звук", callback_data=f"saas_remote_action:{agent_id}:mute"),
                            types.InlineKeyboardButton("🔉 Тише", callback_data=f"saas_remote_action:{agent_id}:volume_down"),
                            types.InlineKeyboardButton("🔊 Громче", callback_data=f"saas_remote_action:{agent_id}:volume_up"),
                            types.InlineKeyboardButton("🖥️ Свернуть", callback_data=f"saas_remote_action:{agent_id}:show_desktop")
                        )
                        markup.row(
                            types.InlineKeyboardButton("◀️ Назад в меню устройства", callback_data=f"saas_panel:{agent_id}")
                        )
                        send_safe(bot, call.message.chat.id, text, reply_markup=markup, parse_mode="Markdown")
                        
                    elif data.startswith("saas_remote_action:"):
                        parts = data.split(":")
                        agent_id = parts[1]
                        remote_act = parts[2]
                        
                        agent = db.query(Agent).filter(Agent.agent_id == agent_id, Agent.user_id == user.id).first()
                        if not agent:
                            send_safe(bot, call.message.chat.id, "❌ Устройство не найдено.")
                            return
                            
                        payload = {}
                        if remote_act == "move_up":
                            payload = {"action": "move", "dx": 0, "dy": -50}
                        elif remote_act == "move_down":
                            payload = {"action": "move", "dx": 0, "dy": 50}
                        elif remote_act == "move_left":
                            payload = {"action": "move", "dx": -50, "dy": 0}
                        elif remote_act == "move_right":
                            payload = {"action": "move", "dx": 50, "dy": 0}
                        elif remote_act == "click_left":
                            payload = {"action": "click_left"}
                        elif remote_act == "click_double":
                            payload = {"action": "click_double"}
                        elif remote_act == "click_right":
                            payload = {"action": "click_right"}
                        elif remote_act == "scroll_up":
                            payload = {"action": "scroll_up"}
                        elif remote_act == "scroll_down":
                            payload = {"action": "scroll_down"}
                        elif remote_act == "play_pause":
                            payload = {"action": "media", "key": "play_pause"}
                        elif remote_act == "mute":
                            payload = {"action": "media", "key": "mute"}
                        elif remote_act == "volume_up":
                            payload = {"action": "media", "key": "volume_up"}
                        elif remote_act == "volume_down":
                            payload = {"action": "media", "key": "volume_down"}
                        elif remote_act == "show_desktop":
                            payload = {"action": "media", "key": "show_desktop"}
                            
                        try:
                            create_task(db, agent, "remote_input", payload, "telegram", confirmed=True)
                            bot.answer_callback_query(call.id, text=f"Отправлено: {remote_act}")
                        except Exception as exc:
                            bot.answer_callback_query(call.id, text=f"Ошибка: {exc}", show_alert=True)
                            
                    elif data.startswith("saas_remote_type:"):
                        agent_id = data.split(":", 1)[1]
                        agent = db.query(Agent).filter(Agent.agent_id == agent_id, Agent.user_id == user.id).first()
                        if not agent:
                            send_safe(bot, call.message.chat.id, "❌ Устройство не найдено.")
                            return
                        USER_STATES[call.message.chat.id] = {"action": "type_text", "agent_id": agent_id}
                        send_safe(bot, call.message.chat.id, "⌨️ *Введите текст для отправки на компьютер:*\n\n_(Текст будет набран на ПК в текущем активном окне)_", parse_mode="Markdown")
                        
                    elif data.startswith("saas_timer:"):
                        agent_id = data.split(":", 1)[1]
                        agent = db.query(Agent).filter(Agent.agent_id == agent_id, Agent.user_id == user.id).first()
                        if not agent:
                            send_safe(bot, call.message.chat.id, "❌ Устройство не найдено.")
                            return
                        sys_info = agent.system_info or {}
                        timer_info = sys_info.get("timer") or {}
                        timer_active = timer_info.get("active", False)
                        timer_remaining = timer_info.get("remaining_minutes", 0)
                        
                        markup = types.InlineKeyboardMarkup()
                        if timer_active:
                            text = (
                                f"⏰ *Таймер выключения активен!*\n\n"
                                f"└ Осталось: `{timer_remaining} мин.`\n"
                                f"└ Действие: `Выключение ПК`"
                            )
                            markup.row(
                                types.InlineKeyboardButton("❌ Отменить таймер", callback_data=f"saas_cancel_timer:{agent_id}"),
                                types.InlineKeyboardButton("🔄 Обновить", callback_data=f"saas_timer:{agent_id}")
                            )
                        else:
                            text = (
                                f"⏰ *Таймер выключения для {agent.name}:*\n\n"
                                f"В данный момент таймер не запущен.\n\n"
                                f"Введите в чат количество минут для выключения (например, `45`):"
                            )
                            USER_STATES[call.message.chat.id] = {"action": "set_timer", "agent_id": agent_id}
                            markup.row(
                                types.InlineKeyboardButton("🔄 Обновить статус", callback_data=f"saas_timer:{agent_id}")
                            )
                        markup.row(
                            types.InlineKeyboardButton("◀️ Назад в меню устройства", callback_data=f"saas_panel:{agent_id}")
                        )
                        send_safe(bot, call.message.chat.id, text, reply_markup=markup, parse_mode="Markdown")
                        
                    elif data.startswith("saas_cancel_timer:"):
                        agent_id = data.split(":", 1)[1]
                        agent = db.query(Agent).filter(Agent.agent_id == agent_id, Agent.user_id == user.id).first()
                        if not agent:
                            send_safe(bot, call.message.chat.id, "❌ Устройство не найдено.")
                            return
                        try:
                            create_task(db, agent, "cancel_timer", {}, "telegram", confirmed=True)
                            send_safe(
                                bot,
                                call.message.chat.id,
                                f"✅ Запрос на отмену таймера отправлен на {agent.name}!",
                                reply_markup=types.InlineKeyboardMarkup().row(
                                    types.InlineKeyboardButton("◀️ Вернуться в таймер", callback_data=f"saas_timer:{agent_id}")
                                )
                            )
                        except Exception as exc:
                            send_safe(bot, call.message.chat.id, f"❌ Ошибка отмены таймера: {exc}")
                return
        return bot

    @bot.message_handler(commands=["start", "login"])
    def start(message):
        if owner_only(bot, message):
            send_safe(bot, message.chat.id, start_text(), reply_markup=main_menu_keyboard())

    @bot.message_handler(commands=["help"])
    def help_cmd(message):
        if owner_only(bot, message):
            send_safe(bot, message.chat.id, RU_TEXTS["help"], reply_markup=main_menu_keyboard())

    @bot.message_handler(commands=["status"])
    def status_cmd(message):
        if owner_only(bot, message):
            send_safe(bot, message.chat.id, status_text(), reply_markup=main_menu_keyboard())

    @bot.message_handler(commands=["server"])
    def server_cmd(message):
        if owner_only(bot, message):
            send_safe(bot, message.chat.id, server_ip_text(), reply_markup=main_menu_keyboard())

    @bot.message_handler(commands=["agents", "agent"])
    def agents_cmd(message):
        if owner_only(bot, message):
            send_safe(bot, message.chat.id, agents_text(), reply_markup=back_keyboard())

    @bot.message_handler(commands=["files"])
    def files_cmd(message):
        if owner_only(bot, message):
            send_safe(bot, message.chat.id, file_list_text(), reply_markup=files_keyboard())

    @bot.message_handler(commands=["upload"])
    def upload_cmd(message):
        if owner_only(bot, message):
            send_safe(
                bot,
                message.chat.id,
                "Отправь сюда один или несколько файлов, фото или видео. Я сохраню их на сервере и дам ID для /download.",
                reply_markup=files_keyboard(),
            )

    @bot.message_handler(content_types=["document", "photo", "video", "audio", "voice", "video_note"])
    def telegram_file_upload_cmd(message):
        save_telegram_upload(bot, message)

    @bot.message_handler(commands=["photos"])
    def photos_cmd(message):
        if owner_only(bot, message):
            text = file_list_text("server_webcam_photo") + "\n\n" + file_list_text("agent_camera_photo")
            send_safe(bot, message.chat.id, text, reply_markup=files_keyboard())

    @bot.message_handler(commands=["screenshots"])
    def screenshots_cmd(message):
        if owner_only(bot, message):
            text = file_list_text("server_screenshot") + "\n\n" + file_list_text("agent_screenshot")
            send_safe(bot, message.chat.id, text, reply_markup=files_keyboard())

    @bot.message_handler(commands=["videos"])
    def videos_cmd(message):
        if owner_only(bot, message):
            text = file_list_text("server_webcam_video") + "\n\n" + file_list_text("agent_camera_video")
            send_safe(bot, message.chat.id, text, reply_markup=files_keyboard())

    @bot.message_handler(commands=["tasks"])
    def tasks_cmd(message):
        if owner_only(bot, message):
            send_safe(bot, message.chat.id, tasks_text(), reply_markup=back_keyboard())

    @bot.message_handler(commands=["logs"])
    def logs_cmd(message):
        if owner_only(bot, message):
            send_safe(bot, message.chat.id, logs_text(), reply_markup=back_keyboard())

    @bot.message_handler(commands=["diag", "diagnostics"])
    def diagnostics_cmd(message):
        if owner_only(bot, message):
            send_safe(bot, message.chat.id, diagnostics_text(), reply_markup=main_menu_keyboard())

    @bot.message_handler(commands=["health"])
    def health_cmd(message):
        if owner_only(bot, message):
            send_safe(bot, message.chat.id, status_text(), reply_markup=main_menu_keyboard())

    @bot.message_handler(commands=["diagnostics_latest"])
    def diagnostics_latest_cmd(message):
        if not owner_only(bot, message):
            return
        path = Path("/home/pc/PCControlPersonal_Project/tools/reports/latest.json")
        if not path.exists():
            send_safe(bot, message.chat.id, "Локального отчёта пока нет. Запусти /diagnostics_run.")
            return
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            checks = data.get("checks", {})
            text = "\n".join([
                "PC Manager Local Check",
                f"Status: {data.get('status', '-')}",
                f"Summary: {data.get('summary', '-')}",
                f"Server: {checks.get('pcmanager_server', '-')}",
                f"Bot: {checks.get('pcmanager_bot', '-')}",
                f"API: {checks.get('api_ping', '-')}",
                f"Issues: {len(data.get('issues', []))}",
                "Report: /home/pc/PCControlPersonal_Project/tools/reports/latest.txt",
            ])
            send_safe(bot, message.chat.id, text, reply_markup=main_menu_keyboard())
        except Exception as exc:
            send_safe(bot, message.chat.id, f"Не удалось прочитать отчёт: {exc}")

    @bot.message_handler(commands=["diagnostics_run"])
    def diagnostics_run_cmd(message):
        if not owner_only(bot, message):
            return
        proc = subprocess.run(
            ["bash", "/home/pc/PCControlPersonal_Project/scripts/local_check.sh"],
            text=True,
            capture_output=True,
            timeout=120,
        )
        send_safe(bot, message.chat.id, (proc.stdout + proc.stderr)[-3500:] or "Диагностика выполнена.", reply_markup=main_menu_keyboard())

    @bot.message_handler(commands=["wol"])
    def wol_cmd(message):
        if owner_only(bot, message):
            send_safe(bot, message.chat.id, wol_text(), reply_markup=wol_keyboard())

    @bot.message_handler(commands=["wake"])
    def wake_cmd(message):
        if not owner_only(bot, message):
            return
        parts = (message.text or "").split()
        if len(parts) != 2:
            send_safe(bot, message.chat.id, "Формат: /wake NAME", reply_markup=wol_keyboard())
            return
        try:
            result = wake_device(parts[1])
            with db_session() as db:
                add_log(db, "info", "telegram", "wol_wake", f"Wake-on-LAN отправлен для {parts[1]}", result)
            send_safe(bot, message.chat.id, f"Пакет Wake-on-LAN отправлен: {parts[1]}", reply_markup=wol_keyboard())
        except Exception as exc:
            send_safe(bot, message.chat.id, f"Не удалось включить устройство: {exc}", reply_markup=wol_keyboard())

    @bot.message_handler(commands=["download"])
    def download_cmd(message):
        if not owner_only(bot, message):
            return
        parts = (message.text or "").split()
        if len(parts) != 2 or not parts[1].isdigit():
            send_safe(bot, message.chat.id, "Формат: /download FILE_ID")
            return
        with db_session() as db:
            asset = db.query(FileAsset).filter(FileAsset.id == int(parts[1]), FileAsset.is_active == True).first()  # noqa: E712
            if not asset:
                send_safe(bot, message.chat.id, RU_TEXTS["file_not_found"])
                return
            add_log(db, "info", "telegram", "file_downloaded", f"Файл {asset.id} отправлен в Telegram", {"file_id": asset.id})
        try:
            send_asset(bot, message.chat.id, asset)
        except Exception as exc:
            send_safe(bot, message.chat.id, f"Не удалось отправить файл: {exc}")

    # Uploads are handled above by telegram_file_upload_cmd for all supported attachment types.
    @bot.message_handler(content_types=["_disabled_duplicate_upload_handler"])
    def upload_from_telegram(message):
        if not owner_only(bot, message):
            return
        try:
            if message.document:
                file_info = bot.get_file(message.document.file_id)
                original = message.document.file_name or "telegram_file.bin"
                mime = message.document.mime_type or "application/octet-stream"
            elif message.video:
                file_info = bot.get_file(message.video.file_id)
                original = "telegram_video.mp4"
                mime = "video/mp4"
            else:
                file_info = bot.get_file(message.photo[-1].file_id)
                original = "telegram_photo.jpg"
                mime = "image/jpeg"
            data = bot.download_file(file_info.file_path)
            with db_session() as db:
                asset = create_asset_from_bytes(db, data, original, "telegram_file", "telegram", description="Загружено из Telegram", mime_type=mime)
            send_safe(bot, message.chat.id, f"Файл сохранён: #{asset.id} | {asset.original_filename}")
        except Exception as exc:
            logger.exception("Ошибка загрузки файла из Telegram")
            send_safe(bot, message.chat.id, f"Не удалось сохранить файл: {exc}")

    @bot.message_handler(commands=["server_screen"])
    def server_screen_cmd(message):
        if not owner_only(bot, message):
            return
        with db_session() as db:
            try:
                asset = create_server_screenshot(db, "telegram")
            except Exception as exc:
                send_safe(bot, message.chat.id, f"Не удалось сделать скрин экрана сервера: {exc}")
                return
        send_asset(bot, message.chat.id, asset)

    @bot.message_handler(commands=["server_webcam", "webcam"])
    def server_webcam_cmd(message):
        if owner_only(bot, message):
            send_safe(bot, message.chat.id, "Подтвердить фото с веб-камеры сервера?", reply_markup=confirm_keyboard("server_webcam_photo"))

    @bot.message_handler(commands=["server_record_video"])
    def server_record_video_cmd(message):
        if not owner_only(bot, message):
            return
        parts = (message.text or "").split()
        duration = int(parts[1]) if len(parts) >= 2 and parts[1].isdigit() else 10
        send_safe(bot, message.chat.id, f"Подтвердить запись видео с веб-камеры сервера на {duration} сек.?", reply_markup=confirm_keyboard(f"server_webcam_video:{duration}"))

    @bot.message_handler(commands=["screenshot"])
    def screenshot_cmd(message):
        if owner_only(bot, message):
            create_agent_task(message, bot, "take_screenshot", {"save_to_server": True, "quality": 80}, "/screenshot AGENT_ID")

    @bot.message_handler(commands=["processes"])
    def processes_cmd(message):
        if owner_only(bot, message):
            create_agent_task(message, bot, "get_process_list", {}, "/processes AGENT_ID")

    @bot.message_handler(commands=["agent_logs"])
    def agent_logs_cmd(message):
        if owner_only(bot, message):
            create_agent_task(message, bot, "agent_logs", {"limit_lines": 120}, "/agent_logs AGENT_ID")

    @bot.message_handler(commands=["system_info"])
    def system_info_cmd(message):
        if owner_only(bot, message):
            create_agent_task(message, bot, "get_system_info", {}, "/system_info AGENT_ID")

    @bot.message_handler(commands=["key"])
    def key_cmd(message):
        if not owner_only(bot, message):
            return
        parts = (message.text or "").split()
        if len(parts) != 3:
            send_safe(bot, message.chat.id, "Формат: /key AGENT_ID KEY")
            return
        key = parts[2].lower().strip()
        if key not in {"w", "a", "s", "d", "z", "e", "esc", "space", "enter", "tab", "shift"}:
            send_safe(bot, message.chat.id, "Клавиша не в allowlist.")
            return
        create_agent_task(message, bot, "press_key", {"key": key}, "/key AGENT_ID KEY")

    @bot.message_handler(commands=["click"])
    def click_cmd(message):
        if not owner_only(bot, message):
            return
        parts = (message.text or "").split()
        if len(parts) != 3:
            send_safe(bot, message.chat.id, "Формат: /click AGENT_ID PRESET")
            return
        preset = parts[2].lower().strip()
        if preset not in {"play", "char1", "char2", "house", "spawn", "spawn2"}:
            send_safe(bot, message.chat.id, "Пресет не в allowlist: play, char1, char2, house, spawn, spawn2.")
            return
        create_agent_task(message, bot, "click_preset", {"preset": preset}, "/click AGENT_ID PRESET")

    @bot.message_handler(commands=["launch_game"])
    def launch_game_cmd(message):
        if owner_only(bot, message):
            create_agent_task(message, bot, "launch_allowed_app", {"app_key": "majestic_launcher"}, "/launch_game AGENT_ID")

    @bot.message_handler(commands=["game_status"])
    def game_status_cmd(message):
        if owner_only(bot, message):
            create_agent_task(message, bot, "game_status", {}, "/game_status AGENT_ID")

    @bot.message_handler(commands=["release_keys"])
    def release_keys_cmd(message):
        if owner_only(bot, message):
            create_agent_task(message, bot, "release_keys", {}, "/release_keys AGENT_ID")

    @bot.message_handler(commands=["desktop_left", "desktop_right"])
    def desktop_cmd(message):
        if owner_only(bot, message):
            command = (message.text or "").split()[0].lstrip("/")
            create_agent_task(message, bot, command, {}, f"/{command} AGENT_ID")

    @bot.message_handler(commands=["volume_up", "volume_down"])
    def volume_cmd(message):
        if owner_only(bot, message):
            command = (message.text or "").split()[0].lstrip("/")
            create_agent_task(message, bot, command, {}, f"/{command} AGENT_ID")

    @bot.message_handler(commands=["anti_afk_start"])
    def anti_afk_start_cmd(message):
        if not owner_only(bot, message):
            return
        parts = (message.text or "").split()
        min_minutes = int(parts[2]) if len(parts) >= 3 and parts[2].isdigit() else 10
        max_minutes = int(parts[3]) if len(parts) >= 4 and parts[3].isdigit() else 20
        create_agent_task(message, bot, "anti_afk_start", {"min_minutes": min_minutes, "max_minutes": max(max_minutes, min_minutes)}, "/anti_afk_start AGENT_ID [MIN] [MAX]")

    @bot.message_handler(commands=["anti_afk_stop"])
    def anti_afk_stop_cmd(message):
        if owner_only(bot, message):
            create_agent_task(message, bot, "anti_afk_stop", {}, "/anti_afk_stop AGENT_ID")

    @bot.message_handler(commands=["autoscreen_start"])
    def autoscreen_start_cmd(message):
        if not owner_only(bot, message):
            return
        parts = (message.text or "").split()
        interval = int(parts[2]) if len(parts) >= 3 and parts[2].isdigit() else 300
        create_agent_task(message, bot, "auto_screen_start", {"interval_seconds": max(60, interval)}, "/autoscreen_start AGENT_ID [SECONDS]")

    @bot.message_handler(commands=["autoscreen_stop"])
    def autoscreen_stop_cmd(message):
        if owner_only(bot, message):
            create_agent_task(message, bot, "auto_screen_stop", {}, "/autoscreen_stop AGENT_ID")

    @bot.message_handler(commands=["automation_status"])
    def automation_status_cmd(message):
        if owner_only(bot, message):
            create_agent_task(message, bot, "automation_status", {}, "/automation_status AGENT_ID")

    @bot.message_handler(commands=["photo", "camera"])
    def photo_cmd(message):
        if owner_only(bot, message):
            create_agent_task(message, bot, "camera_snapshot", {"save_to_server": True}, "/photo AGENT_ID", confirmed=True)

    @bot.message_handler(commands=["recordvideo"])
    def recordvideo_cmd(message):
        if not owner_only(bot, message):
            return
        parts = (message.text or "").split()
        if len(parts) < 2:
            send_safe(bot, message.chat.id, "Формат: /recordvideo AGENT_ID SECONDS")
            return
        duration = int(parts[2]) if len(parts) >= 3 and parts[2].isdigit() else 5
        create_agent_task(message, bot, "record_video", {"duration_seconds": duration, "save_to_server": True}, "/recordvideo AGENT_ID SECONDS", confirmed=True)

    @bot.message_handler(commands=["task"])
    def task_cmd(message):
        if not owner_only(bot, message):
            return
        parts = (message.text or "").split()
        if len(parts) < 3:
            send_safe(bot, message.chat.id, "Формат: /task AGENT_ID ACTION")
            return
        with db_session() as db:
            agent = db.query(Agent).filter(Agent.agent_id == parts[1]).first()
            if not agent:
                send_safe(bot, message.chat.id, RU_TEXTS["agent_not_found"])
                return
            try:
                task = create_task(db, agent, parts[2], {}, "telegram", confirmed=False)
                add_log(db, "info", "telegram", "task_created", f"Задача {task.task_id} создана", {"task_id": task.task_id})
                markup = types.InlineKeyboardMarkup()
                markup.row(
                    types.InlineKeyboardButton("Отменить задачу", callback_data=f"cancel_task:{task.task_id}"),
                    types.InlineKeyboardButton("Повторить задачу", callback_data=f"retry_task:{task.task_id}"),
                )
                send_safe(bot, message.chat.id, f"Задача создана: {task.task_id}", reply_markup=markup)
            except ValueError as exc:
                send_safe(bot, message.chat.id, f"Ошибка: {exc}")

    @bot.message_handler(commands=["cancel"])
    def cancel_cmd(message):
        if not owner_only(bot, message):
            return
        parts = (message.text or "").split()
        if len(parts) != 2:
            send_safe(bot, message.chat.id, "Формат: /cancel TASK_ID")
            return
        cancel_task_by_id(bot, message.chat.id, parts[1])

    @bot.message_handler(commands=["retry"])
    def retry_cmd(message):
        if not owner_only(bot, message):
            return
        parts = (message.text or "").split()
        if len(parts) != 2:
            send_safe(bot, message.chat.id, "Формат: /retry TASK_ID")
            return
        retry_task_by_id(bot, message.chat.id, parts[1])



    @bot.message_handler(commands=["storage", "disk"])
    def storage_cmd(message):
        if owner_only(bot, message):
            send_safe(bot, message.chat.id, get_storage_report(), parse_mode="Markdown")

    @bot.message_handler(func=lambda message: True)
    def saas_text_handler(message):
        chat_id = message.chat.id
        state = USER_STATES.get(chat_id)
        if not state:
            return
        
        action = state.get("action")
        agent_id = state.get("agent_id")
        USER_STATES.pop(chat_id, None)
        
        with db_session() as db:
            tg_id = getattr(message.from_user, "id", 0)
            username = getattr(message.from_user, "username", None)
            user = ensure_telegram_user(db, tg_id, username)
            
            agent = db.query(Agent).filter(Agent.agent_id == agent_id, Agent.user_id == user.id).first()
            if not agent:
                send_safe(bot, chat_id, "❌ Устройство не найдено.")
                return
            
            if action == "type_text":
                text_to_type = message.text or ""
                try:
                    task = create_task(db, agent, "remote_input", {"action": "type_text", "text": text_to_type}, "telegram", confirmed=True)
                    send_safe(
                        bot,
                        chat_id,
                        f"✅ Текст отправлен на набор на {agent.name}! (Задача: {task.task_id})",
                        reply_markup=types.InlineKeyboardMarkup().row(
                            types.InlineKeyboardButton("🛋️ Вернуться к пульту", callback_data=f"saas_remote:{agent_id}")
                        )
                    )
                except Exception as exc:
                    send_safe(bot, chat_id, f"❌ Ошибка отправки текста: {exc}")
                    
            elif action == "set_timer":
                try:
                    duration_min = int(str(message.text or "").strip())
                    if duration_min <= 0:
                        raise ValueError()
                except ValueError:
                    send_safe(bot, chat_id, "❌ Пожалуйста, введите корректное число минут (целое положительное число).")
                    return
                
                try:
                    task = create_task(db, agent, "start_timer", {"duration": duration_min, "action": "shutdown"}, "telegram", confirmed=True)
                    send_safe(
                        bot,
                        chat_id,
                        f"✅ Таймер выключения на {duration_min} мин. запущен! (Задача: {task.task_id})",
                        reply_markup=types.InlineKeyboardMarkup().row(
                            types.InlineKeyboardButton("⏰ Проверить статус", callback_data=f"saas_timer:{agent_id}")
                        )
                    )
                except Exception as exc:
                    send_safe(bot, chat_id, f"❌ Ошибка запуска таймера: {exc}")

    @bot.callback_query_handler(func=lambda call: True)
    def callback_handler(call):
        data = call.data or ""
        if data.startswith("saas_"):
            answer_callback(bot, call)
            tg_id = getattr(call.from_user, "id", 0)
            username = getattr(call.from_user, "username", None)
            with db_session() as db:
                user = ensure_telegram_user(db, tg_id, username)
                if data == "saas_new_key":
                    key = generate_activation_key_for_user(db, user.id)
                    text = (
                        "🔑 *Твой новый ключ активации:* `{}`\n"
                        "_(Нажми на ключ выше, чтобы скопировать)_\n\n"
                        "Введи его в запущенном `PCManager_Agent.exe` для автоматической привязки."
                    ).format(key)
                    markup = types.InlineKeyboardMarkup()
                    markup.row(
                        types.InlineKeyboardButton("📥 Скачать Agent.exe", callback_data="saas_download"),
                        types.InlineKeyboardButton("🖥️ Мои устройства", callback_data="saas_my_devices")
                    )
                    send_safe(bot, call.message.chat.id, text, reply_markup=markup, parse_mode="Markdown")
                elif data == "saas_download":
                    send_agent_file(bot, call.message.chat.id)
                elif data == "saas_my_devices":
                    agents = db.query(Agent).filter(Agent.user_id == user.id).all()
                    markup = types.InlineKeyboardMarkup()
                    if not agents:
                        text = "🖥️ *У тебя пока нет привязанных устройств.*\n\nЗапусти `PCManager_Agent.exe` и введи свой ключ активации."
                    else:
                        text = "🖥️ *Выбери устройство для управления:*"
                        for a in agents:
                            status_emoji = "🟢" if compute_agent_status(a) == "online" else "🔴"
                            markup.row(types.InlineKeyboardButton(f"{status_emoji} {a.name} ({a.agent_id})", callback_data=f"saas_panel:{a.agent_id}"))
                    
                    markup.row(
                        types.InlineKeyboardButton("🔑 Получить новый ключ", callback_data="saas_new_key"),
                        types.InlineKeyboardButton("📥 Скачать Agent.exe", callback_data="saas_download")
                    )
                    send_safe(bot, call.message.chat.id, text, reply_markup=markup, parse_mode="Markdown")
                elif data.startswith("saas_panel:"):
                    agent_id = data.split(":", 1)[1]
                    agent = db.query(Agent).filter(Agent.agent_id == agent_id, Agent.user_id == user.id).first()
                    if not agent:
                        send_safe(bot, call.message.chat.id, "❌ Устройство не найдено.")
                        return
                    is_update_available = is_newer_version(agent.version, settings.latest_agent_version)
                    status = compute_agent_status(agent)
                    status_emoji = "🟢" if status == "online" else "🔴"
                    text = (
                        f"🖥️ *Управление устройством: {agent.name}*\n"
                        f"└ ID: `{agent.agent_id}`\n"
                        f"└ Статус: {status_emoji} {status}\n"
                        f"└ ОС: {agent.platform} | Версия: {agent.version}\n"
                        f"└ IP: {agent.local_ip or '-'}\n"
                        f"└ Текущая задача: {agent.current_task or 'нет'}\n"
                        f"└ Активность: {agent.last_seen_at.strftime('%Y-%m-%d %H:%M:%S') if agent.last_seen_at else '-'}"
                    )
                    if is_update_available:
                        text += f"\n\n⚠️ *Доступно обновление агента до v{settings.latest_agent_version}!*"
                    markup = types.InlineKeyboardMarkup()
                    if status == "online":
                        if is_update_available:
                            markup.row(
                                types.InlineKeyboardButton(f"🔄 Обновить агента до v{settings.latest_agent_version}", callback_data=f"saas_update_agent:{agent_id}")
                            )
                        markup.row(
                            types.InlineKeyboardButton("📸 Скриншот", callback_data=f"saas_action:{agent_id}:take_screenshot"),
                            types.InlineKeyboardButton("💻 Система", callback_data=f"saas_action:{agent_id}:get_system_info")
                        )
                        markup.row(
                            types.InlineKeyboardButton("📋 Процессы", callback_data=f"saas_action:{agent_id}:get_process_list"),
                            types.InlineKeyboardButton("📹 Вебка / Камера", callback_data=f"saas_cam:{agent_id}")
                        )
                        markup.row(
                            types.InlineKeyboardButton("🎥 Запись экрана", callback_data=f"saas_screen_rec:{agent_id}"),
                            types.InlineKeyboardButton("⌨️ Клавиатура", callback_data=f"saas_keys:{agent_id}")
                        )
                        markup.row(
                            types.InlineKeyboardButton("🤖 Автоматизация", callback_data=f"saas_auto:{agent_id}"),
                            types.InlineKeyboardButton("🔌 Питание", callback_data=f"saas_power:{agent_id}")
                        )
                        markup.row(
                            types.InlineKeyboardButton("🎮 Игры / Лаунчеры", callback_data=f"saas_games:{agent_id}")
                        )
                        markup.row(
                            types.InlineKeyboardButton("🛋️ Пульт", callback_data=f"saas_remote:{agent_id}"),
                            types.InlineKeyboardButton("⏰ Таймер", callback_data=f"saas_timer:{agent_id}")
                        )
                    else:
                        markup.row(types.InlineKeyboardButton("💤 Устройство не в сети", callback_data="saas_noop"))
                    markup.row(
                        types.InlineKeyboardButton("🔄 Обновить", callback_data=f"saas_panel:{agent_id}"),
                        types.InlineKeyboardButton("◀️ Назад к списку", callback_data="saas_my_devices")
                    )
                    send_safe(bot, call.message.chat.id, text, reply_markup=markup, parse_mode="Markdown")
                elif data.startswith("saas_update_agent:"):
                    agent_id = data.split(":", 1)[1]
                    agent = db.query(Agent).filter(Agent.agent_id == agent_id, Agent.user_id == user.id).first()
                    if not agent:
                        send_safe(bot, call.message.chat.id, "❌ Устройство не найдено.")
                        return
                    try:
                        task = create_task(db, agent, "update_agent", {}, "telegram", confirmed=True)
                        send_safe(
                            bot,
                            call.message.chat.id,
                            f"✅ Запрос на обновление отправлен на {agent.name}! (Задача: {task.task_id})",
                            reply_markup=types.InlineKeyboardMarkup().row(
                                types.InlineKeyboardButton("◀️ Вернуться в панель", callback_data=f"saas_panel:{agent_id}")
                            )
                        )
                    except Exception as exc:
                        send_safe(bot, call.message.chat.id, f"❌ Ошибка отправки команды обновления: {exc}")
                elif data.startswith("saas_keys:"):
                    agent_id = data.split(":", 1)[1]
                    agent = db.query(Agent).filter(Agent.agent_id == agent_id, Agent.user_id == user.id).first()
                    if not agent:
                        send_safe(bot, call.message.chat.id, "❌ Устройство не найдено.")
                        return
                    text = f"⌨️ *Эмуляция клавиш для {agent.name}:*\nВыбери клавишу для нажатия:"
                    markup = types.InlineKeyboardMarkup()
                    markup.row(
                        types.InlineKeyboardButton("W", callback_data=f"saas_press:{agent_id}:w"),
                        types.InlineKeyboardButton("A", callback_data=f"saas_press:{agent_id}:a"),
                        types.InlineKeyboardButton("S", callback_data=f"saas_press:{agent_id}:s"),
                        types.InlineKeyboardButton("D", callback_data=f"saas_press:{agent_id}:d")
                    )
                    markup.row(
                        types.InlineKeyboardButton("Space (Пробел)", callback_data=f"saas_press:{agent_id}:space"),
                        types.InlineKeyboardButton("Enter (Ввод)", callback_data=f"saas_press:{agent_id}:enter")
                    )
                    markup.row(
                        types.InlineKeyboardButton("E", callback_data=f"saas_press:{agent_id}:e"),
                        types.InlineKeyboardButton("Z", callback_data=f"saas_press:{agent_id}:z"),
                        types.InlineKeyboardButton("Esc", callback_data=f"saas_press:{agent_id}:esc"),
                        types.InlineKeyboardButton("Shift", callback_data=f"saas_press:{agent_id}:shift")
                    )
                    markup.row(types.InlineKeyboardButton("◀️ Назад в меню устройства", callback_data=f"saas_panel:{agent_id}"))
                    send_safe(bot, call.message.chat.id, text, reply_markup=markup, parse_mode="Markdown")
                elif data.startswith("saas_cam:"):
                    agent_id = data.split(":", 1)[1]
                    agent = db.query(Agent).filter(Agent.agent_id == agent_id, Agent.user_id == user.id).first()
                    if not agent:
                        send_safe(bot, call.message.chat.id, "❌ Устройство не найдено.")
                        return
                    text = f"📹 *Управление камерой для {agent.name}:*"
                    markup = types.InlineKeyboardMarkup()
                    markup.row(
                        types.InlineKeyboardButton("📸 Сделать фото", callback_data=f"saas_action:{agent_id}:take_photo"),
                        types.InlineKeyboardButton("📹 Видео (5с)", callback_data=f"saas_action:{agent_id}:record_video_5")
                    )
                    markup.row(
                        types.InlineKeyboardButton("📹 Видео (10с)", callback_data=f"saas_action:{agent_id}:record_video_10"),
                        types.InlineKeyboardButton("📹 Видео (30с)", callback_data=f"saas_action:{agent_id}:record_video_30")
                    )
                    markup.row(types.InlineKeyboardButton("◀️ Назад в меню устройства", callback_data=f"saas_panel:{agent_id}"))
                    send_safe(bot, call.message.chat.id, text, reply_markup=markup, parse_mode="Markdown")
                elif data.startswith("saas_screen_rec:"):
                    agent_id = data.split(":", 1)[1]
                    agent = db.query(Agent).filter(Agent.agent_id == agent_id, Agent.user_id == user.id).first()
                    if not agent:
                        send_safe(bot, call.message.chat.id, "❌ Устройство не найдено.")
                        return
                    text = f"🎥 *Запись экрана для {agent.name}:*\nВыбери длительность записи:"
                    markup = types.InlineKeyboardMarkup()
                    markup.row(
                        types.InlineKeyboardButton("🎥 Экран (5с)", callback_data=f"saas_action:{agent_id}:record_screen_5"),
                        types.InlineKeyboardButton("🎥 Экран (10с)", callback_data=f"saas_action:{agent_id}:record_screen_10")
                    )
                    markup.row(
                        types.InlineKeyboardButton("🎥 Экран (30с)", callback_data=f"saas_action:{agent_id}:record_screen_30")
                    )
                    markup.row(types.InlineKeyboardButton("◀️ Назад в меню устройства", callback_data=f"saas_panel:{agent_id}"))
                    send_safe(bot, call.message.chat.id, text, reply_markup=markup, parse_mode="Markdown")
                elif data.startswith("saas_auto:"):
                    agent_id = data.split(":", 1)[1]
                    agent = db.query(Agent).filter(Agent.agent_id == agent_id, Agent.user_id == user.id).first()
                    if not agent:
                        send_safe(bot, call.message.chat.id, "❌ Устройство не найдено.")
                        return
                    sys_info = agent.system_info or {}
                    rules = sys_info.get("automation_rules", [])
                    
                    text = f"🤖 *Управление автоматизацией для {agent.name}:*\n\n"
                    text += "*Базовые службы:*\n"
                    text += "• Anti-AFK (имитация присутствия)\n"
                    text += "• Автоэкран (периодические скриншоты)\n\n"
                    
                    markup = types.InlineKeyboardMarkup()
                    markup.row(
                        types.InlineKeyboardButton("🟢 Старт Anti-AFK", callback_data=f"saas_action:{agent_id}:anti_afk_start"),
                        types.InlineKeyboardButton("🔴 Стоп Anti-AFK", callback_data=f"saas_action:{agent_id}:anti_afk_stop")
                    )
                    markup.row(
                        types.InlineKeyboardButton("📸 Старт Автоэкран", callback_data=f"saas_action:{agent_id}:autoscreen_start"),
                        types.InlineKeyboardButton("🔴 Стоп Автоэкран", callback_data=f"saas_action:{agent_id}:autoscreen_stop")
                    )
                    
                    text += "*Активные правила:* \n"
                    if rules:
                        for idx, rule in enumerate(rules):
                            r_id = rule.get("id")
                            name = rule.get("name", "Правило")
                            trigger = rule.get("trigger", "time")
                            r_time = rule.get("time", "22:00")
                            action = rule.get("action", "sleep_pc")
                            action_label = {"sleep_pc": "💤 Сон", "lock_pc": "🔒 Блок", "monitor_off": "🖥️ Погаснуть", "screenshot": "📸 Скриншот"}.get(action, action)
                            
                            if trigger == "startup":
                                desc = f"{idx+1}. {name}: [При старте] ➡️ {action_label}"
                            else:
                                desc = f"{idx+1}. {name}: [В {r_time}] ➡️ {action_label}"
                            text += f"• {desc}\n"
                            markup.row(
                                types.InlineKeyboardButton(f"🗑️ Удалить #{idx+1}", callback_data=f"saas_del_rule:{agent_id}:{r_id}")
                            )
                    else:
                        text += "_Правила автоматизации по расписанию не добавлены._\n"
                        
                    text += "\n*Добавить готовые правила:* \n"
                    markup.row(
                        types.InlineKeyboardButton("💤 Сон в 22:00", callback_data=f"saas_add_rule:{agent_id}:sleep_2200"),
                        types.InlineKeyboardButton("🖥️ Погаснуть в 23:00", callback_data=f"saas_add_rule:{agent_id}:mon_2300")
                    )
                    markup.row(
                        types.InlineKeyboardButton("🔒 Блок в 18:00", callback_data=f"saas_add_rule:{agent_id}:lock_1800"),
                        types.InlineKeyboardButton("📸 Скрин при старте", callback_data=f"saas_add_rule:{agent_id}:scr_boot")
                    )
                    markup.row(types.InlineKeyboardButton("◀️ Назад в меню устройства", callback_data=f"saas_panel:{agent_id}"))
                    send_safe(bot, call.message.chat.id, text, reply_markup=markup, parse_mode="Markdown")
                elif data.startswith("saas_power:"):
                    agent_id = data.split(":", 1)[1]
                    agent = db.query(Agent).filter(Agent.agent_id == agent_id, Agent.user_id == user.id).first()
                    if not agent:
                        send_safe(bot, call.message.chat.id, "❌ Устройство не найдено.")
                        return
                    text = f"🔌 *Управление питанием для {agent.name}:*\nВыбери действие:"
                    markup = types.InlineKeyboardMarkup()
                    markup.row(
                        types.InlineKeyboardButton("🔒 Заблокировать", callback_data=f"saas_action:{agent_id}:lock_pc"),
                        types.InlineKeyboardButton("💤 Спящий режим", callback_data=f"saas_action:{agent_id}:sleep_pc")
                    )
                    markup.row(
                        types.InlineKeyboardButton("🖥️ Погасить монитор", callback_data=f"saas_action:{agent_id}:monitor_off")
                    )
                    markup.row(
                        types.InlineKeyboardButton("🔴 Выключить ПК", callback_data=f"saas_action:{agent_id}:shutdown_now")
                    )
                    markup.row(types.InlineKeyboardButton("◀️ Назад в меню устройства", callback_data=f"saas_panel:{agent_id}"))
                    send_safe(bot, call.message.chat.id, text, reply_markup=markup, parse_mode="Markdown")
                elif data.startswith("saas_games:"):
                    agent_id = data.split(":", 1)[1]
                    agent = db.query(Agent).filter(Agent.agent_id == agent_id, Agent.user_id == user.id).first()
                    if not agent:
                        send_safe(bot, call.message.chat.id, "❌ Устройство не найдено.")
                        return
                    sys_info = agent.system_info or {}
                    games_list = sys_info.get("games_list", [])
                    text = f"🎮 *Игротека для {agent.name}:*\n"
                    markup = types.InlineKeyboardMarkup()
                    if games_list:
                        text += "Доступные игры (Steam, Epic & RP):\n"
                        for game in games_list:
                            title = game.get("title", "Неизвестная игра")
                            store = str(game.get("store", "steam")).upper()
                            playtime = game.get("playtime_hours", 0.0)
                            game_key = title.lower().strip().replace(" ", "_").replace("-", "_")
                            if store == "STEAM" and playtime > 0:
                                playtime_str = f" ⏳ В игре: {playtime} ч."
                            else:
                                playtime_str = ""
                            text += f"\n• *{title}* [{store}]{playtime_str}"
                            markup.row(
                                types.InlineKeyboardButton(f"🕹️ Старт {title[:12]}", callback_data=f"saas_launch_app:{agent_id}:{game_key}"),
                                types.InlineKeyboardButton("⏹️ Закрыть", callback_data=f"saas_close_app:{agent_id}:{game_key}")
                            )
                    else:
                        launchers = sys_info.get("launchers", [])
                        if launchers:
                            for launcher_key in launchers:
                                label = launcher_key.replace("_", " ").title()
                                markup.row(
                                    types.InlineKeyboardButton(f"🕹️ {label}", callback_data=f"saas_launch_app:{agent_id}:{launcher_key}"),
                                    types.InlineKeyboardButton("⏹️ Закрыть", callback_data=f"saas_close_app:{agent_id}:{launcher_key}")
                                )
                        else:
                            text += "\n\n_Игры не обнаружены. Убедитесь, что лаунчеры установлены, и обновите статус._"
                            markup.row(types.InlineKeyboardButton("🔄 Обновить статус", callback_data=f"saas_action:{agent_id}:get_system_info"))
                    markup.row(types.InlineKeyboardButton("◀️ Назад в меню устройства", callback_data=f"saas_panel:{agent_id}"))
                    send_safe(bot, call.message.chat.id, text, reply_markup=markup, parse_mode="Markdown")
                elif data.startswith("saas_launch_app:"):
                    _, agent_id, launcher_key = data.split(":", 2)
                    agent = db.query(Agent).filter(Agent.agent_id == agent_id, Agent.user_id == user.id).first()
                    if not agent:
                        send_safe(bot, call.message.chat.id, "❌ Устройство не найдено.")
                        return
                    try:
                        task = create_task(db, agent, "launch_allowed_app", {"app_key": launcher_key}, "telegram", confirmed=True)
                        send_safe(
                            bot,
                            call.message.chat.id,
                            f"✅ Команда запуска '{launcher_key.replace('_', ' ').title()}' отправлена! (Задача: {task.task_id})",
                            reply_markup=types.InlineKeyboardMarkup().row(types.InlineKeyboardButton("◀️ Назад к играм", callback_data=f"saas_games:{agent_id}"))
                        )
                    except Exception as exc:
                        send_safe(bot, call.message.chat.id, f"❌ Ошибка запуска: {exc}")
                elif data.startswith("saas_close_app:"):
                    _, agent_id, launcher_key = data.split(":", 2)
                    agent = db.query(Agent).filter(Agent.agent_id == agent_id, Agent.user_id == user.id).first()
                    if not agent:
                        send_safe(bot, call.message.chat.id, "❌ Устройство не найдено.")
                        return
                    try:
                        task = create_task(db, agent, "close_allowed_app", {"app_key": launcher_key}, "telegram", confirmed=True)
                        send_safe(
                            bot,
                            call.message.chat.id,
                            f"✅ Команда закрытия '{launcher_key.replace('_', ' ').title()}' отправлена! (Задача: {task.task_id})",
                            reply_markup=types.InlineKeyboardMarkup().row(types.InlineKeyboardButton("◀️ Назад к играм", callback_data=f"saas_games:{agent_id}"))
                        )
                    except Exception as exc:
                        send_safe(bot, call.message.chat.id, f"❌ Ошибка закрытия: {exc}")
                elif data == "saas_noop":
                    pass
                elif data.startswith("saas_press:"):
                    _, agent_id, key = data.split(":", 2)
                    agent = db.query(Agent).filter(Agent.agent_id == agent_id, Agent.user_id == user.id).first()
                    if not agent:
                        send_safe(bot, call.message.chat.id, "❌ Устройство не найдено.")
                        return
                    try:
                        task = create_task(db, agent, "press_key", {"key": key}, "telegram")
                        send_safe(
                            bot,
                            call.message.chat.id,
                            f"✅ Клавиша '{key.upper()}' успешно отправлена на {agent.name}! (Задача: {task.task_id})",
                            reply_markup=types.InlineKeyboardMarkup().row(types.InlineKeyboardButton("◀️ Назад к клавиатуре", callback_data=f"saas_keys:{agent_id}"))
                        )
                    except Exception as exc:
                        send_safe(bot, call.message.chat.id, f"❌ Ошибка отправки клавиши: {exc}")
                elif data.startswith("saas_action:"):
                    _, agent_id, action = data.split(":", 2)
                    agent = db.query(Agent).filter(Agent.agent_id == agent_id, Agent.user_id == user.id).first()
                    if not agent:
                        send_safe(bot, call.message.chat.id, "❌ Устройство не найдено.")
                        return
                    action_payloads = {
                        "take_screenshot": ("take_screenshot", {"save_to_server": True, "quality": 80}),
                        "get_system_info": ("get_system_info", {}),
                        "get_process_list": ("get_process_list", {}),
                        "anti_afk_start": ("anti_afk_start", {}),
                        "anti_afk_stop": ("anti_afk_stop", {}),
                        "autoscreen_start": ("autoscreen_start", {}),
                        "autoscreen_stop": ("autoscreen_stop", {}),
                        "take_photo": ("camera_snapshot", {"save_to_server": True}),
                        "record_video_5": ("record_video", {"duration_seconds": 5, "save_to_server": True}),
                        "record_video_10": ("record_video", {"duration_seconds": 10, "save_to_server": True}),
                        "record_video_30": ("record_video", {"duration_seconds": 30, "save_to_server": True}),
                        "lock_pc": ("lock_pc", {}),
                        "sleep_pc": ("sleep_pc", {}),
                        "monitor_off": ("monitor_off", {}),
                        "shutdown_now": ("shutdown_now", {}),
                    }
                    if action not in action_payloads:
                        send_safe(bot, call.message.chat.id, "❌ Неизвестное действие.")
                        return
                    act_type, payload = action_payloads[action]
                    try:
                        task = create_task(db, agent, act_type, payload, "telegram", confirmed=True)
                        send_safe(
                            bot,
                            call.message.chat.id,
                            f"✅ Команда отправлена на {agent.name}! Выполняется... (Задача: {task.task_id})",
                            reply_markup=types.InlineKeyboardMarkup().row(types.InlineKeyboardButton("◀️ Вернуться в панель", callback_data=f"saas_panel:{agent_id}"))
                        )
                    except Exception as exc:
                        send_safe(bot, call.message.chat.id, f"❌ Ошибка отправки команды: {exc}")
                elif data.startswith("saas_remote:"):
                    agent_id = data.split(":", 1)[1]
                    agent = db.query(Agent).filter(Agent.agent_id == agent_id, Agent.user_id == user.id).first()
                    if not agent:
                        send_safe(bot, call.message.chat.id, "❌ Устройство не найдено.")
                        return
                    text = f"🛋️ *Виртуальный пульт управления для {agent.name}:*\nВы можете управлять курсором мыши, кликами и медиаплеером."
                    markup = types.InlineKeyboardMarkup()
                    
                    markup.row(
                        types.InlineKeyboardButton("📜 Вверх", callback_data=f"saas_remote_action:{agent_id}:scroll_up"),
                        types.InlineKeyboardButton("⬆️ Вверх", callback_data=f"saas_remote_action:{agent_id}:move_up"),
                        types.InlineKeyboardButton("🖱️ 2x ЛКМ", callback_data=f"saas_remote_action:{agent_id}:click_double")
                    )
                    markup.row(
                        types.InlineKeyboardButton("◀️ Влево", callback_data=f"saas_remote_action:{agent_id}:move_left"),
                        types.InlineKeyboardButton("🖱️ ЛКМ", callback_data=f"saas_remote_action:{agent_id}:click_left"),
                        types.InlineKeyboardButton("🖱️ ПКМ", callback_data=f"saas_remote_action:{agent_id}:click_right"),
                        types.InlineKeyboardButton("▶️ Вправо", callback_data=f"saas_remote_action:{agent_id}:move_right")
                    )
                    markup.row(
                        types.InlineKeyboardButton("📜 Вниз", callback_data=f"saas_remote_action:{agent_id}:scroll_down"),
                        types.InlineKeyboardButton("⬇️ Вниз", callback_data=f"saas_remote_action:{agent_id}:move_down"),
                        types.InlineKeyboardButton("⌨️ Текст", callback_data=f"saas_remote_type:{agent_id}")
                    )
                    markup.row(
                        types.InlineKeyboardButton("⏯️ Пауза", callback_data=f"saas_remote_action:{agent_id}:play_pause"),
                        types.InlineKeyboardButton("🔇 Звук", callback_data=f"saas_remote_action:{agent_id}:mute"),
                        types.InlineKeyboardButton("🔉 Тише", callback_data=f"saas_remote_action:{agent_id}:volume_down"),
                        types.InlineKeyboardButton("🔊 Громче", callback_data=f"saas_remote_action:{agent_id}:volume_up"),
                        types.InlineKeyboardButton("🖥️ Свернуть", callback_data=f"saas_remote_action:{agent_id}:show_desktop")
                    )
                    markup.row(
                        types.InlineKeyboardButton("◀️ Назад в меню устройства", callback_data=f"saas_panel:{agent_id}")
                    )
                    send_safe(bot, call.message.chat.id, text, reply_markup=markup, parse_mode="Markdown")
                    
                elif data.startswith("saas_remote_action:"):
                    parts = data.split(":")
                    agent_id = parts[1]
                    remote_act = parts[2]
                    
                    agent = db.query(Agent).filter(Agent.agent_id == agent_id, Agent.user_id == user.id).first()
                    if not agent:
                        send_safe(bot, call.message.chat.id, "❌ Устройство не найдено.")
                        return
                        
                    payload = {}
                    if remote_act == "move_up":
                        payload = {"action": "move", "dx": 0, "dy": -50}
                    elif remote_act == "move_down":
                        payload = {"action": "move", "dx": 0, "dy": 50}
                    elif remote_act == "move_left":
                        payload = {"action": "move", "dx": -50, "dy": 0}
                    elif remote_act == "move_right":
                        payload = {"action": "move", "dx": 50, "dy": 0}
                    elif remote_act == "click_left":
                        payload = {"action": "click_left"}
                    elif remote_act == "click_double":
                        payload = {"action": "click_double"}
                    elif remote_act == "click_right":
                        payload = {"action": "click_right"}
                    elif remote_act == "scroll_up":
                        payload = {"action": "scroll_up"}
                    elif remote_act == "scroll_down":
                        payload = {"action": "scroll_down"}
                    elif remote_act == "play_pause":
                        payload = {"action": "media", "key": "play_pause"}
                    elif remote_act == "mute":
                        payload = {"action": "media", "key": "mute"}
                    elif remote_act == "volume_up":
                        payload = {"action": "media", "key": "volume_up"}
                    elif remote_act == "volume_down":
                        payload = {"action": "media", "key": "volume_down"}
                    elif remote_act == "show_desktop":
                        payload = {"action": "media", "key": "show_desktop"}
                        
                    try:
                        create_task(db, agent, "remote_input", payload, "telegram", confirmed=True)
                        bot.answer_callback_query(call.id, text=f"Отправлено: {remote_act}")
                    except Exception as exc:
                        bot.answer_callback_query(call.id, text=f"Ошибка: {exc}", show_alert=True)
                        
                elif data.startswith("saas_remote_type:"):
                    agent_id = data.split(":", 1)[1]
                    agent = db.query(Agent).filter(Agent.agent_id == agent_id, Agent.user_id == user.id).first()
                    if not agent:
                        send_safe(bot, call.message.chat.id, "❌ Устройство не найдено.")
                        return
                    USER_STATES[call.message.chat.id] = {"action": "type_text", "agent_id": agent_id}
                    send_safe(bot, call.message.chat.id, "⌨️ *Введите текст для отправки на компьютер:*\n\n_(Текст будет набран на ПК в текущем активном окне)_", parse_mode="Markdown")
                    
                elif data.startswith("saas_timer:"):
                    agent_id = data.split(":", 1)[1]
                    agent = db.query(Agent).filter(Agent.agent_id == agent_id, Agent.user_id == user.id).first()
                    if not agent:
                        send_safe(bot, call.message.chat.id, "❌ Устройство не найдено.")
                        return
                    sys_info = agent.system_info or {}
                    timer_info = sys_info.get("timer") or {}
                    timer_active = timer_info.get("active", False)
                    timer_remaining = timer_info.get("remaining_minutes", 0)
                    
                    markup = types.InlineKeyboardMarkup()
                    if timer_active:
                        text = (
                            f"⏰ *Таймер выключения активен!*\n\n"
                            f"└ Осталось: `{timer_remaining} мин.`\n"
                            f"└ Действие: `Выключение ПК`"
                        )
                        markup.row(
                            types.InlineKeyboardButton("❌ Отменить таймер", callback_data=f"saas_cancel_timer:{agent_id}"),
                            types.InlineKeyboardButton("🔄 Обновить", callback_data=f"saas_timer:{agent_id}")
                        )
                    else:
                        text = (
                            f"⏰ *Таймер выключения для {agent.name}:*\n\n"
                            f"В данный момент таймер не запущен.\n\n"
                            f"Введите в чат количество минут для выключения (например, `45`):"
                        )
                        USER_STATES[call.message.chat.id] = {"action": "set_timer", "agent_id": agent_id}
                        markup.row(
                            types.InlineKeyboardButton("🔄 Обновить статус", callback_data=f"saas_timer:{agent_id}")
                        )
                    markup.row(
                        types.InlineKeyboardButton("◀️ Назад в меню устройства", callback_data=f"saas_panel:{agent_id}")
                    )
                    send_safe(bot, call.message.chat.id, text, reply_markup=markup, parse_mode="Markdown")
                    
                elif data.startswith("saas_cancel_timer:"):
                    agent_id = data.split(":", 1)[1]
                    agent = db.query(Agent).filter(Agent.agent_id == agent_id, Agent.user_id == user.id).first()
                    if not agent:
                        send_safe(bot, call.message.chat.id, "❌ Устройство не найдено.")
                        return
                    try:
                        create_task(db, agent, "cancel_timer", {}, "telegram", confirmed=True)
                        send_safe(
                            bot,
                            call.message.chat.id,
                            f"✅ Запрос на отмену таймера отправлен на {agent.name}!",
                            reply_markup=types.InlineKeyboardMarkup().row(
                                types.InlineKeyboardButton("◀️ Вернуться в таймер", callback_data=f"saas_timer:{agent_id}")
                            )
                        )
                    except Exception as exc:
                        send_safe(bot, call.message.chat.id, f"❌ Ошибка отмены таймера: {exc}")
            return

        if not callback_owner_only(bot, call):
            return
        answer_callback(bot, call)
        safe_bot_log({"event": "callback_pressed", "user_id": call.from_user.id, "callback_data": data, "time": datetime.utcnow().isoformat()})
        try:
            if data in {"main_menu", "menu:main"}:
                send_safe(bot, call.message.chat.id, start_text(), reply_markup=main_menu_keyboard())
            elif data in {"refresh_status", "status"}:
                send_safe(bot, call.message.chat.id, status_text(), reply_markup=main_menu_keyboard())
            elif data in {"show_agents", "agents", "menu:agents", "agents_ip"}:
                markup = types.InlineKeyboardMarkup()
                with db_session() as db:
                    for a in db.query(Agent).all():
                        if compute_agent_status(a) == "online" and is_newer_version(a.version, settings.latest_agent_version):
                            markup.row(types.InlineKeyboardButton(f"🔄 Обновить {a.name}", callback_data=f"update_agent:{a.agent_id}"))
                markup.row(types.InlineKeyboardButton(BTN["main_menu"], callback_data="main_menu"))
                send_safe(bot, call.message.chat.id, agents_text(), reply_markup=markup, parse_mode="Markdown")
            elif data.startswith("update_agent:"):
                agent_id = data.split(":", 1)[1]
                with db_session() as db:
                    agent = db.query(Agent).filter(Agent.agent_id == agent_id).first()
                    if not agent:
                        send_safe(bot, call.message.chat.id, "❌ Агент не найден.", reply_markup=back_keyboard())
                    else:
                        try:
                            task = create_task(db, agent, "update_agent", {}, "telegram", confirmed=True)
                            send_safe(
                                bot,
                                call.message.chat.id,
                                f"✅ Запрос на обновление отправлен на {agent.name}! (Задача: {task.task_id})",
                                reply_markup=back_keyboard()
                            )
                        except Exception as exc:
                            send_safe(bot, call.message.chat.id, f"❌ Ошибка отправки команды обновления: {exc}", reply_markup=back_keyboard())
            elif data in {"show_files", "files", "menu:files"}:
                send_safe(bot, call.message.chat.id, file_list_text(), reply_markup=files_keyboard())
            elif data in {"show_logs", "logs"}:
                send_safe(bot, call.message.chat.id, logs_text(), reply_markup=back_keyboard())
            elif data in {"show_server_ip", "server_ip", "menu:server"}:
                send_safe(bot, call.message.chat.id, server_ip_text(), reply_markup=main_menu_keyboard())
            elif data in {"show_recent_tasks", "tasks", "recent_tasks"}:
                send_safe(bot, call.message.chat.id, tasks_text(), reply_markup=back_keyboard())
            elif data == "show_diagnostics":
                send_safe(bot, call.message.chat.id, diagnostics_text(), reply_markup=main_menu_keyboard())
            elif data == "show_wol":
                send_safe(bot, call.message.chat.id, wol_text(), reply_markup=wol_keyboard())
            elif data.startswith("wake:"):
                device_name = data.split(":", 1)[1]
                result = wake_device(device_name)
                with db_session() as db:
                    add_log(db, "info", "telegram", "wol_wake", f"Wake-on-LAN отправлен для {device_name}", result)
                send_safe(bot, call.message.chat.id, f"Пакет Wake-on-LAN отправлен: {device_name}", reply_markup=wol_keyboard())
            elif data in {"show_photos", "photos"}:
                send_safe(bot, call.message.chat.id, file_list_text("server_webcam_photo") + "\n\n" + file_list_text("agent_camera_photo"), reply_markup=files_keyboard())
            elif data in {"show_screenshots", "screenshots", "server_screens"}:
                send_safe(bot, call.message.chat.id, file_list_text("server_screenshot") + "\n\n" + file_list_text("agent_screenshot"), reply_markup=files_keyboard())
            elif data in {"show_videos", "videos", "server_webcam_videos"}:
                send_safe(bot, call.message.chat.id, file_list_text("server_webcam_video") + "\n\n" + file_list_text("agent_camera_video"), reply_markup=files_keyboard())
            elif data in {"menu:media", "media_agents"}:
                send_safe(bot, call.message.chat.id, file_list_text("server_screenshot") + "\n\n" + file_list_text("server_webcam_photo") + "\n\n" + file_list_text("server_webcam_video"), reply_markup=files_keyboard())
            elif data == "server_screen":
                with db_session() as db:
                    asset = create_server_screenshot(db, "telegram")
                send_asset(bot, call.message.chat.id, asset)
            elif data in {"confirm:server_webcam", "server_webcam_photos"}:
                send_safe(bot, call.message.chat.id, "Подтвердить фото с веб-камеры сервера?", reply_markup=confirm_keyboard("server_webcam_photo"))
            elif data.startswith("confirm:server_video"):
                duration = data.split(":")[-1] if data.split(":")[-1].isdigit() else "10"
                send_safe(bot, call.message.chat.id, f"Подтвердить запись видео с веб-камеры сервера на {duration} сек.?", reply_markup=confirm_keyboard(f"server_webcam_video:{duration}"))
            elif data == "confirm:server_webcam_photo":
                with db_session() as db:
                    asset = create_server_webcam_photo(db, "telegram")
                send_asset(bot, call.message.chat.id, asset)
            elif data.startswith("confirm:server_webcam_video"):
                duration = int(data.split(":")[-1]) if data.split(":")[-1].isdigit() else 10
                with db_session() as db:
                    asset = create_server_webcam_video(db, duration, "telegram")
                send_asset(bot, call.message.chat.id, asset)
            elif data.startswith("cancel_task:"):
                cancel_task_by_id(bot, call.message.chat.id, data.split(":", 1)[1])
            elif data.startswith("retry_task:"):
                retry_task_by_id(bot, call.message.chat.id, data.split(":", 1)[1])
            elif data == "show_storage":
                send_safe(bot, call.message.chat.id, get_storage_report(), parse_mode="Markdown", reply_markup=main_menu_keyboard())
            else:
                safe_bot_log({"event": "unknown_callback", "callback_data": data, "time": datetime.utcnow().isoformat()})
                answer_callback(bot, call, RU_TEXTS["unknown_button"])
                send_safe(bot, call.message.chat.id, RU_TEXTS["unknown_button"], reply_markup=main_menu_keyboard())
        except Exception as exc:
            logger.exception("Ошибка обработки callback %s", data)
            safe_bot_log({"event": "callback_failed", "callback_data": data, "error": str(exc), "time": datetime.utcnow().isoformat()})
            send_safe(bot, call.message.chat.id, f"Ошибка: {exc}", reply_markup=main_menu_keyboard())

    return bot


def cancel_task_by_id(bot: telebot.TeleBot, chat_id: int, task_id: str) -> None:
    with db_session() as db:
        task = db.query(Task).filter(Task.task_id == task_id).first()
        if not task:
            send_safe(bot, chat_id, RU_TEXTS["task_not_found"])
            return
        cancel_task(db, task)
        add_log(db, "warning", "telegram", "task_cancelled", f"Задача {task.task_id} отменена", {"task_id": task.task_id})
    send_safe(bot, chat_id, "Задача отменена.", reply_markup=back_keyboard())


def retry_task_by_id(bot: telebot.TeleBot, chat_id: int, task_id: str) -> None:
    with db_session() as db:
        task = db.query(Task).filter(Task.task_id == task_id).first()
        if not task:
            send_safe(bot, chat_id, RU_TEXTS["task_not_found"])
            return
        try:
            retried = retry_task(db, task, "telegram")
            add_log(db, "info", "telegram", "task_retried", f"Задача {task.task_id} повторена", {"new_task_id": retried.task_id})
            send_safe(bot, chat_id, f"Повтор создан: {retried.task_id}", reply_markup=back_keyboard())
        except ValueError as exc:
            send_safe(bot, chat_id, f"Повтор запрещён: {exc}", reply_markup=back_keyboard())



def run_sudo(cmd: str) -> str:
    try:
        result = subprocess.run(f"echo '8008' | sudo -S {cmd}", shell=True, capture_output=True, text=True, timeout=10)
        out = result.stdout.strip()
        if not out and result.stderr:
            return "ERR: " + result.stderr.strip()
        return out
    except Exception as e:
        return str(e)


def make_progress_bar(pct, width=12):
    filled = int(round(max(0.0, min(100.0, pct)) / 100.0 * width))
    bar = "█" * filled + "░" * (width - filled)
    return f"[{bar}]"


def get_storage_report() -> str:
    try:
        import shutil
        
        # SSD usage
        ssd_tot, ssd_usd, ssd_fre = shutil.disk_usage("/")
        ssd_pct = (ssd_usd / ssd_tot) * 100 if ssd_tot > 0 else 0
        
        # HDD usage
        hdd_tot, hdd_usd, hdd_fre = shutil.disk_usage("/data")
        hdd_pct = (hdd_usd / hdd_tot) * 100 if hdd_tot > 0 else 0
        
        report = (
            f"📊 **Анализ накопителей сервера:**\n\n"
            f"💾 **Хранилище HDD (`/data`):**\n"
            f"`{make_progress_bar(hdd_pct)}` `{hdd_pct:.1f}%`\n"
            f"Всего: `{hdd_tot / (1024**3):.1f} GB`\n"
            f"Занято: `{hdd_usd / (1024**3):.1f} GB`\n"
            f"Свободно: `{hdd_fre / (1024**3):.1f} GB`\n\n"
            f"💿 **Системный SSD (`/`):**\n"
            f"`{make_progress_bar(ssd_pct)}` `{ssd_pct:.1f}%`\n"
            f"Всего: `{ssd_tot / (1024**3):.1f} GB`\n"
            f"Занято: `{ssd_usd / (1024**3):.1f} GB`\n"
            f"Свободно: `{ssd_fre / (1024**3):.1f} GB`"
        )
        return report
    except Exception as e:
        return f"❌ Ошибка получения данных о дисках: {e}"




def get_routing_for_log_entry(entry: LogEntry, db) -> tuple[telebot.TeleBot | None, list[int]]:
    agent_id = str((entry.meta or {}).get("agent_id") or "")
    task_id = str((entry.meta or {}).get("task_id") or "")
    if not agent_id and task_id:
        task = db.query(Task).filter(Task.task_id == task_id).first()
        if task:
            agent_id = task.agent_id
    
    if agent_id:
        agent = db.query(Agent).filter(Agent.agent_id == agent_id).first()
        if agent and agent.user_id:
            user = db.query(User).filter(User.id == agent.user_id).first()
            if user and user.telegram_id:
                try:
                    target_bot = CLIENT_BOT or BOT
                    return target_bot, [int(user.telegram_id)]
                except Exception:
                    pass
    
    # Fallback to Admin Bot
    try:
        user_ids = list(settings.allowed_telegram_ids)
    except Exception:
        user_ids = []
    return ADMIN_BOT or BOT, user_ids


def notification_loop() -> None:
    while True:
        try:
            if not (BOT or CLIENT_BOT):
                time.sleep(5)
                continue
                
            # --- AUTOMATED DAILY REPORT TRIGGER (at 22:00 / 10 PM) ---
            now_dt = datetime.now()
            current_date = now_dt.strftime("%Y-%m-%d")
            if now_dt.hour == 22:
                flag_file = Path(settings.data_dir) / "last_daily_report_date.txt"
                try:
                    last_date = flag_file.read_text(encoding="utf-8").strip() if flag_file.exists() else ""
                except Exception:
                    last_date = ""
                if last_date != current_date:
                    try:
                        flag_file.write_text(current_date, encoding="utf-8")
                    except Exception:
                        pass
                    # Send storage report to admin bot / allowed telegram IDs
                    report = get_storage_report()
                    try:
                        user_ids = list(settings.allowed_telegram_ids)
                    except Exception:
                        user_ids = []
                    target_bot = ADMIN_BOT or BOT
                    if target_bot:
                        for user_id in user_ids:
                            send_safe(target_bot, user_id, report, parse_mode="Markdown")

            # --- PROCESS NEW LOG ENTRIES & SEND NOTIFICATIONS / SCREENSHOTS ---
            with db_session() as db:
                entries = db.query(LogEntry).filter(LogEntry.id > int(STATE["last_log_id"])).order_by(LogEntry.id.asc()).limit(50).all()
                for entry in entries:
                    STATE["last_log_id"] = entry.id
                    should_notify = entry.event in NOTIFY_EVENTS or (entry.level.lower() == "error" and entry.event not in SUPPRESSED_ERROR_EVENTS)
                    
                    if should_notify:
                        if entry.event in {"task_done", "task_failed"} and was_task_already_notified(entry):
                            continue
                        
                        parse_mode = None
                        if entry.event == "threshold_alert":
                            text = entry.message
                            parse_mode = "Markdown"
                        elif entry.event in {"task_done", "task_failed"}:
                            text = task_notification_text(entry)
                            parse_mode = "HTML"
                        else:
                            text = f"[{entry.level}] {entry.source}/{entry.event}\n{entry.message}"
                            
                        bot_instance, user_ids = get_routing_for_log_entry(entry, db)
                        if bot_instance:
                            for user_id in user_ids:
                                if parse_mode:
                                    send_safe(bot_instance, user_id, text, parse_mode=parse_mode)
                                else:
                                    send_safe(bot_instance, user_id, text)
                    
                    if entry.event == "agent_screenshot_uploaded" or (entry.event == "file_uploaded" and (entry.meta or {}).get("type") in {"agent_screenshot", "agent_camera_photo", "agent_camera_video"}):
                        send_uploaded_asset(entry)
                    if entry.event == "task_done":
                        send_completed_media(entry)
            
            time.sleep(5)
        except Exception as exc:
            logger.exception("Ошибка цикла уведомлений: %s", exc)
            time.sleep(5)


def was_task_already_notified(entry: LogEntry) -> bool:
    task_id = str((entry.meta or {}).get("task_id") or "")
    if not task_id:
        return False
    if task_id in NOTIFIED_TASK_IDS:
        return True
    NOTIFIED_TASK_IDS.add(task_id)
    if len(NOTIFIED_TASK_IDS) > 500:
        for old in list(NOTIFIED_TASK_IDS)[:100]:
            NOTIFIED_TASK_IDS.discard(old)
    return False


def task_notification_text(entry: LogEntry) -> str:
    import html
    task_id = str((entry.meta or {}).get("task_id") or "")
    if not task_id:
        return f"🖥️ PC Manager\n\n📢 {html.escape(entry.message)}"
    with db_session() as db:
        task = db.query(Task).filter(Task.task_id == task_id).first()
        if not task:
            return f"🖥️ PC Manager\n\n📢 {html.escape(entry.message)}"
        is_ok = task.status in {"success", "done"}
        emoji = "✅" if is_ok else "❌"
        title = "Команда выполнена" if is_ok else "Ошибка команды"
        action = ACTION_LABELS.get(task.action, task.action)
        
        # Format result carefully
        result = pretty_task_result(task.action, task.error or task.result or "")
        if len(result) > 260:
            result = result[:260].rstrip() + "..."
            
        title_esc = html.escape(title)
        agent_esc = html.escape(task.agent_id)
        action_esc = html.escape(action)
        result_esc = html.escape(result)
        
        # Simplified and attractive HTML message layout
        lines = [
            f"🖥️ <b>{title_esc}</b>",
            f"👤 Агент: <code>{agent_esc}</code>",
            f"⚙️ Действие: <b>{action_esc}</b>"
        ]
        
        # If it's screenshot or video command, we only state that it completed, not showing file number as requested.
        if task.action in {"screenshot", "take_screenshot", "camera_snapshot", "record_video", "recordvideo"}:
            lines.append(f"{emoji} Команда <code>{action_esc}</code> успешно выполнена!")
        else:
            lines.append(f"{emoji} Результат: {result_esc}")
            
        return "\n".join(lines)


def short_task_id(task_id: str) -> str:
    return task_id[:8] if task_id else "-"


def format_bytes(value: Any) -> str:
    try:
        size = float(value or 0)
    except Exception:
        size = 0.0
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size < 1024 or unit == "TB":
            return f"{size:.1f} {unit}" if unit != "B" else f"{int(size)} B"
        size /= 1024
    return f"{size:.1f} TB"


def format_seconds(value: Any) -> str:
    try:
        seconds = int(value or 0)
    except Exception:
        seconds = 0
    days, rem = divmod(seconds, 86400)
    hours, rem = divmod(rem, 3600)
    minutes, _ = divmod(rem, 60)
    parts = []
    if days:
        parts.append(f"{days} \u0434")
    if hours:
        parts.append(f"{hours} \u0447")
    if minutes or not parts:
        parts.append(f"{minutes} \u043c\u0438\u043d")
    return " ".join(parts)


def yes_no(value: Any, yes: str = "\u0434\u0430", no: str = "\u043d\u0435\u0442") -> str:
    return yes if bool(value) else no


def compact_lines(lines: list[str]) -> str:
    return "\n".join(line for line in lines if line)


def pretty_process_list(items: list[Any]) -> str:
    processes = [item for item in items if isinstance(item, dict)]
    top = sorted(processes, key=lambda item: float(item.get("memory_mb") or 0), reverse=True)[:5]
    lines = [f"\u041f\u0440\u043e\u0446\u0435\u0441\u0441\u043e\u0432: {len(processes)}"]
    for proc in top:
        name = proc.get("name") or "process"
        pid = proc.get("pid") or "-"
        mem = proc.get("memory_mb")
        mem_text = f"{float(mem):.1f} MB" if mem is not None else "-"
        lines.append(f"- {name} PID {pid}, RAM {mem_text}")
    return compact_lines(lines)


def pretty_automation_state(name: str, state: dict[str, Any]) -> str:
    running = yes_no(state.get("running"), "\u0440\u0430\u0431\u043e\u0442\u0430\u0435\u0442", "\u0432\u044b\u043a\u043b\u044e\u0447\u0435\u043d")
    last_error = state.get("last_error") or ""
    line = f"{name}: {running}"
    if last_error:
        line += f", \u043e\u0448\u0438\u0431\u043a\u0430: {last_error}"
    return line


def pretty_dict_result(action: str, data: dict[str, Any]) -> str:
    if action == "cleanup_screenshots" and "removed" in data:
        removed = data.get("removed", 0)
        freed_text = format_bytes(data.get("freed_bytes"))
        after = data.get("total_after")
        tail = f", \u043e\u0441\u0442\u0430\u043b\u043e\u0441\u044c {after}" if after is not None else ""
        return f"\u0443\u0434\u0430\u043b\u0435\u043d\u043e {removed}, \u043e\u0441\u0432\u043e\u0431\u043e\u0436\u0434\u0435\u043d\u043e {freed_text}{tail}"
    if action == "game_status":
        launcher = "\u0437\u0430\u043f\u0443\u0449\u0435\u043d" if data.get("majestic_launcher") else "\u043d\u0435 \u0437\u0430\u043f\u0443\u0449\u0435\u043d"
        gta = "\u0437\u0430\u043f\u0443\u0449\u0435\u043d\u0430" if data.get("gta5") else "\u043d\u0435 \u0437\u0430\u043f\u0443\u0449\u0435\u043d\u0430"
        processes = data.get("known_processes") or []
        process_text = ", ".join(str(item) for item in processes) if processes else "\u043d\u0435 \u043d\u0430\u0439\u0434\u0435\u043d\u044b"
        return compact_lines([f"\u041b\u0430\u0443\u043d\u0447\u0435\u0440: {launcher}", f"GTA V: {gta}", f"\u041f\u0440\u043e\u0446\u0435\u0441\u0441\u044b: {process_text}"])
    if action in {"screenshot", "take_screenshot"} or data.get("file_id"):
        lines = ["\u0421\u043a\u0440\u0438\u043d\u0448\u043e\u0442 \u0433\u043e\u0442\u043e\u0432"]
        if data.get("file_id"):
            lines.append(f"\u0424\u0430\u0439\u043b ID: {data.get('file_id')}")
        if data.get("size_bytes"):
            lines.append(f"\u0420\u0430\u0437\u043c\u0435\u0440: {format_bytes(data.get('size_bytes'))}")
        if data.get("uploaded") is not None:
            lines.append(f"\u041d\u0430 \u0441\u0435\u0440\u0432\u0435\u0440\u0435: {yes_no(data.get('uploaded'))}")
        return compact_lines(lines)
    if action in {"system_info", "get_system_info"}:
        sys_info = data.get("system_info") if isinstance(data.get("system_info"), dict) else data
        return compact_lines([
            f"ПК: {sys_info.get('hostname') or '-'}",
            f"Пользователь: {sys_info.get('username') or '-'}",
            f"OS: {sys_info.get('platform') or sys_info.get('os') or '-'}",
            f"CPU: {sys_info.get('cpu_percent', '-')}%",
            f"RAM: {sys_info.get('ram_percent', '-')}% ({format_bytes(sys_info.get('ram_used'))} / {format_bytes(sys_info.get('ram_total'))})",
            f"Uptime: {format_seconds(sys_info.get('uptime_seconds'))}",
        ])
    if action in {"disk_info", "get_disk_info"}:
        drives = data.get("drives") or []
        lines = [f"\u0414\u0438\u0441\u043a\u043e\u0432: {len(drives)}"]
        for drive in drives[:5]:
            if isinstance(drive, dict):
                lines.append(f"- {drive.get('mountpoint') or drive.get('device')}: {drive.get('percent', '-')}%, \u0441\u0432\u043e\u0431\u043e\u0434\u043d\u043e {format_bytes(drive.get('free'))}")
        return compact_lines(lines)
    if action in {"temperature"}:
        if not data or data.get("available") is False:
            return "\u0422\u0435\u043c\u043f\u0435\u0440\u0430\u0442\u0443\u0440\u0430 \u043d\u0435\u0434\u043e\u0441\u0442\u0443\u043f\u043d\u0430"
        return f"\u041c\u0430\u043a\u0441\u0438\u043c\u0443\u043c: {data.get('max_c', '-')}\u00b0C"
    if action == "restart_allowed_app":
        return compact_lines([
            f"\u041f\u0440\u0438\u043b\u043e\u0436\u0435\u043d\u0438\u0435: {data.get('app') or '-'}",
            f"\u0417\u0430\u0432\u0435\u0440\u0448\u0435\u043d\u043e \u043f\u0440\u043e\u0446\u0435\u0441\u0441\u043e\u0432: {data.get('terminated_processes', 0)}",
            f"\u0417\u0430\u043f\u0443\u0449\u0435\u043d\u043e: {yes_no(data.get('started'))}",
        ])
    if action == "press_key":
        return f"\u041a\u043b\u0430\u0432\u0438\u0448\u0430 {str(data.get('key') or '').upper()} \u043d\u0430\u0436\u0430\u0442\u0430 \u043d\u0430 {data.get('duration_seconds', '-')} \u0441"
    if action == "click_preset":
        return f"\u041a\u043b\u0438\u043a: {data.get('preset') or '-'} ({data.get('x')}, {data.get('y')})"
    if action == "release_keys":
        return "\u041a\u043b\u0430\u0432\u0438\u0448\u0438 \u043e\u0442\u043f\u0443\u0449\u0435\u043d\u044b"
    if action == "launch_allowed_app":
        return f"\u0417\u0430\u043f\u0443\u0441\u043a: {data.get('app_key') or '-'}"
    if action in {"volume_up", "volume_down"}:
        return "\u0413\u0440\u043e\u043c\u043a\u043e\u0441\u0442\u044c \u0438\u0437\u043c\u0435\u043d\u0435\u043d\u0430"
    if action in {"desktop_left", "desktop_right", "desktop_new", "desktop_close"}:
        return data.get("message") or "\u0433\u043e\u0442\u043e\u0432\u043e"
    if action in {"anti_afk_start", "anti_afk_stop"}:
        if data.get("already_running"):
            return "Anti-AFK \u0443\u0436\u0435 \u0440\u0430\u0431\u043e\u0442\u0430\u0435\u0442"
        if data.get("started"):
            return f"Anti-AFK \u0432\u043a\u043b\u044e\u0447\u0451\u043d: {data.get('min_minutes')}-{data.get('max_minutes')} \u043c\u0438\u043d"
        if data.get("stopping"):
            return "Anti-AFK \u043e\u0441\u0442\u0430\u043d\u0430\u0432\u043b\u0438\u0432\u0430\u0435\u0442\u0441\u044f"
    if action in {"auto_screen_start", "auto_screen_stop"}:
        if data.get("already_running"):
            return "\u0410\u0432\u0442\u043e\u0441\u043a\u0440\u0438\u043d \u0443\u0436\u0435 \u0440\u0430\u0431\u043e\u0442\u0430\u0435\u0442"
        if data.get("started"):
            return f"\u0410\u0432\u0442\u043e\u0441\u043a\u0440\u0438\u043d \u0432\u043a\u043b\u044e\u0447\u0451\u043d: \u043a\u0430\u0436\u0434\u044b\u0435 {data.get('interval_seconds')} \u0441"
        if data.get("stopping"):
            return "\u0410\u0432\u0442\u043e\u0441\u043a\u0440\u0438\u043d \u043e\u0441\u0442\u0430\u043d\u0430\u0432\u043b\u0438\u0432\u0430\u0435\u0442\u0441\u044f"
    if action == "automation_status":
        return compact_lines([
            pretty_automation_state("Anti-AFK", data.get("anti_afk") or {}),
            pretty_automation_state("\u0410\u0432\u0442\u043e\u0441\u043a\u0440\u0438\u043d", data.get("auto_screen") or {}),
        ])
    if data.get("message"):
        return str(data.get("message"))
    if data.get("ok") is True:
        return "\u0433\u043e\u0442\u043e\u0432\u043e"
    return json.dumps(data, ensure_ascii=False)


def pretty_task_result(action: str, result: str) -> str:
    text = sanitize_result(result)
    if not text:
        return "\u0431\u0435\u0437 \u043f\u043e\u0434\u0440\u043e\u0431\u043d\u043e\u0441\u0442\u0435\u0439"
    try:
        data = json.loads(text)
        if isinstance(data, dict):
            if action in {"process_list", "get_process_list"} and "items" in data:
                return pretty_process_list(data["items"])
            return pretty_dict_result(action, data)
        if isinstance(data, list):
            if action in {"process_list", "get_process_list"}:
                return pretty_process_list(data)
            return f"\u042d\u043b\u0435\u043c\u0435\u043d\u0442\u043e\u0432: {len(data)}"
    except Exception:
        pass
    return text


def sanitize_result(result: str) -> str:
    text = str(result)
    for secret in [settings.server_access_key, settings.telegram_bot_token]:
        if secret:
            text = text.replace(secret, "[HIDDEN]")
    text = text.replace("\\n", " ").replace("\n", " ")
    while "  " in text:
        text = text.replace("  ", " ")
    return text.strip()


def send_completed_media(entry: LogEntry) -> None:
    task_id = str((entry.meta or {}).get("task_id") or "")
    if not task_id or not (BOT or CLIENT_BOT):
        return
    with db_session() as db:
        task = db.query(Task).filter(Task.task_id == task_id).first()
        if not task or task.action not in {"camera_snapshot"} or not task.result:
            return
        try:
            result_data = json.loads(task.result) or {}
            file_id = int(result_data.get("file_id") or 0)
            asset = db.query(FileAsset).filter(FileAsset.id == file_id, FileAsset.is_active == True).first()  # noqa: E712

            # Determine routing
            bot_instance = BOT
            user_ids = list(settings.allowed_telegram_ids or [])
            if task.agent_id:
                agent = db.query(Agent).filter(Agent.agent_id == task.agent_id).first()
                if agent and agent.user_id:
                    user = db.query(User).filter(User.id == agent.user_id).first()
                    if user and user.telegram_id:
                        bot_instance = CLIENT_BOT or BOT
                        user_ids = [int(user.telegram_id)]

            if asset:
                for user_id in user_ids:
                    send_asset(bot_instance, user_id, asset)
            elif result_data.get("base64") and result_data.get("mime_type", "").startswith("image/"):
                # Fallback: send photo from base64 embedded in result
                import base64 as _b64
                import io
                raw = _b64.b64decode(result_data["base64"])
                for user_id in user_ids:
                    try:
                        buf = io.BytesIO(raw)
                        buf.name = "photo.jpg"
                        send_safe(bot_instance, user_id, "📷 Фото с камеры")
                        bot_instance.send_photo(user_id, buf)
                    except Exception:
                        logger.exception("Не удалось отправить base64 фото камеры")
        except Exception:
            logger.exception("Не удалось отправить медиа завершённой задачи")


def send_uploaded_asset(entry: LogEntry) -> None:
    if not (BOT or CLIENT_BOT):
        return
    try:
        file_id = int((entry.meta or {}).get("file_id") or 0)
    except Exception:
        file_id = 0
    if not file_id:
        return
    with db_session() as db:
        asset = db.query(FileAsset).filter(FileAsset.id == file_id, FileAsset.is_active == True).first()  # noqa: E712
        if not asset:
            return
        bot_instance = BOT
        user_ids = settings.allowed_telegram_ids
        if asset.agent_id:
            agent = db.query(Agent).filter(Agent.agent_id == asset.agent_id).first()
            if agent and agent.user_id:
                user = db.query(User).filter(User.id == agent.user_id).first()
                if user and user.telegram_id:
                    bot_instance = CLIENT_BOT or BOT
                    user_ids = [int(user.telegram_id)]
        for user_id in user_ids:
            try:
                send_asset(bot_instance, user_id, asset)
            except Exception:
                logger.exception("Не удалось отправить загруженный скриншот в Telegram")


ADMIN_BOT: telebot.TeleBot | None = None
CLIENT_BOT: telebot.TeleBot | None = None


def run_bot_forever() -> None:
    global BOT, ADMIN_BOT, CLIENT_BOT
    ADMIN_TOKEN = "8635021652:AAEN4dA-oYkdOKW6YpOJ5RMn8Qy7Nf5p1Yc"
    CLIENT_TOKEN = "8368299868:AAE6XDZ1x84XaT3RVcQ0FkS6cFbcCYFXan0"
    
    try:
        ADMIN_BOT = build_bot(ADMIN_TOKEN, is_admin=True)
        BOT = ADMIN_BOT
        logger.info("Admin Telegram bot initialized.")
    except Exception as e:
        logger.error("Failed to initialize Admin Telegram bot: %s", e)

    try:
        CLIENT_BOT = build_bot(CLIENT_TOKEN, is_admin=False)
        logger.info("SaaS Client Telegram bot initialized.")
    except Exception as e:
        logger.error("Failed to initialize SaaS Client Telegram bot: %s", e)

    with db_session() as db:
        latest = db.query(LogEntry).order_by(LogEntry.id.desc()).first()
        STATE["last_log_id"] = int(latest.id) if latest else 0
    
    threading.Thread(target=notification_loop, name="telegram-notifier", daemon=True).start()
    
    if ADMIN_BOT:
        def poll_admin():
            while True:
                try:
                    logger.info("Admin bot polling active")
                    ADMIN_BOT.infinity_polling(timeout=20, long_polling_timeout=20, allowed_updates=["message", "callback_query"])
                except Exception as exc:
                    logger.warning("Admin bot polling error: %s", exc)
                    time.sleep(5)
        threading.Thread(target=poll_admin, name="admin-bot-polling", daemon=True).start()

    if CLIENT_BOT:
        def poll_client():
            while True:
                try:
                    logger.info("SaaS Client bot polling active")
                    CLIENT_BOT.infinity_polling(timeout=20, long_polling_timeout=20, allowed_updates=["message", "callback_query"])
                except Exception as exc:
                    logger.warning("SaaS Client bot polling error: %s", exc)
                    time.sleep(5)
        threading.Thread(target=poll_client, name="client-bot-polling", daemon=True).start()

    while True:
        time.sleep(1)


def start_bot_thread() -> threading.Thread:
    thread = threading.Thread(target=run_bot_forever, name="telegram-bot", daemon=True)
    thread.start()
    return thread
