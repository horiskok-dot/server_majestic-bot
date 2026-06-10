from __future__ import annotations

import logging
from typing import Any

import requests

from ..config import get_settings


logger = logging.getLogger("notify")


def telegram_notify(text: str, meta: dict[str, Any] | None = None) -> bool:
    """Send a short owner-only Telegram notification if bot settings are present."""
    settings = get_settings()
    if not settings.telegram_bot_enabled or not settings.telegram_bot_token or not settings.allowed_telegram_ids:
        return False
    safe_text = (text or "").strip()[:3500]
    if not safe_text:
        return False
    ok = True
    for chat_id in settings.allowed_telegram_ids:
        try:
            response = requests.post(
                f"https://api.telegram.org/bot{settings.telegram_bot_token}/sendMessage",
                json={"chat_id": chat_id, "text": safe_text},
                timeout=12,
            )
            if response.status_code >= 400:
                ok = False
                logger.warning("Telegram notify failed: %s", response.status_code)
        except Exception as exc:
            ok = False
            logger.warning("Telegram notify failed: %s", exc)
    return ok
