from __future__ import annotations

import os
from typing import Any

import requests

from tools._shared import TIMEOUT, err


def send_telegram(text: str = "", confirmed: bool = False, chat_id: str | None = None) -> dict[str, Any]:
    """Gửi tin Telegram. `chat_id` là tùy chọn, không khai báo trong tools.yaml (model không thấy);
    chỉ code gọi tool (ví dụ UI web) truyền vào. Không có thì dùng TELEGRAM_CHAT_ID trong .env."""
    if not confirmed:
        return {
            "tool": "send_telegram",
            "status": "needs_confirmation",
            "message": "Only send after the user explicitly confirms.",
        }
    try:
        token = os.getenv("TELEGRAM_BOT_TOKEN")
        chat_id = str(chat_id).strip() if chat_id else os.getenv("TELEGRAM_CHAT_ID")
        if not token or not chat_id:
            raise RuntimeError("Missing TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID env var")
        response = requests.post(
            f"https://api.telegram.org/bot{token}/sendMessage",
            json={"chat_id": chat_id, "text": text, "parse_mode": "Markdown"},
            timeout=TIMEOUT,
        )
        response.raise_for_status()
        return {"tool": "send_telegram", "status": "sent"}
    except Exception as exc:
        return err("send_telegram", exc)

