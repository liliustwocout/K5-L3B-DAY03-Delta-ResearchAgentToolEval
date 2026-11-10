"""Logic chat dùng chung cho UI web (Vercel và chạy local).

Nhận lịch sử hội thoại, chạy vòng model -> tool của `chat.py`, trả về câu trả lời
cùng tóm tắt các lần gọi tool. Không trả về key hay kết quả tool đầy đủ.
"""
from __future__ import annotations

import json
import os
import re
import time
from contextvars import ContextVar
from pathlib import Path
from typing import Any

from chat import run_model_tool_loop  # chat.py cũng nạp .env khi chạy local
from providers import make_provider
from tools import TOOL_FUNCTIONS, load_tool_declarations, to_openai_tools

ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS = ROOT / "artifacts"

MAX_MESSAGES = 10      # chỉ giữ 10 tin nhắn gần nhất
MAX_CHARS = 2000       # cắt mỗi tin nhắn
MAX_TOOL_ROUNDS = 4

_system_prompt = (ARTIFACTS / "system_prompt.md").read_text(encoding="utf-8")
def _strip_unsupported(node: Any) -> Any:
    """Bỏ `additionalProperties`: bản google-genai cũ (ghim trên Vercel) báo lỗi khi gặp trường này."""
    if isinstance(node, dict):
        return {key: _strip_unsupported(value) for key, value in node.items() if key != "additionalProperties"}
    if isinstance(node, list):
        return [_strip_unsupported(value) for value in node]
    return node


_tools = _strip_unsupported(to_openai_tools(load_tool_declarations(ARTIFACTS / "tools.yaml")))
_provider: Any = None


# ---- Gửi Telegram trên web: mỗi người nhận tin ở chat ID của chính họ ----
CHAT_ID_RE = re.compile(r"^-?\d{5,15}$")
SEND_LIMIT = 5            # tối đa 5 tin / chat ID / giờ (bộ nhớ của từng instance, chỉ là hàng rào mỏng)
SEND_WINDOW = 3600
MAX_SEND_CHARS = 1000

# Chat ID của người đang gọi, riêng cho từng yêu cầu (an toàn khi nhiều người dùng cùng lúc).
_chat_id: ContextVar[str | None] = ContextVar("chat_id", default=None)
_sent_log: dict[str, list[float]] = {}
_real_send = TOOL_FUNCTIONS["send"]


def valid_chat_id(value: Any) -> bool:
    return isinstance(value, str) and bool(CHAT_ID_RE.match(value.strip()))


def _allow(chat: str) -> bool:
    now = time.time()
    recent = [t for t in _sent_log.get(chat, []) if now - t < SEND_WINDOW]
    if len(recent) >= SEND_LIMIT:
        _sent_log[chat] = recent
        return False
    recent.append(now)
    _sent_log[chat] = recent
    return True


def _web_send(text: str = "", confirmed: bool = False) -> dict[str, Any]:
    """Thay cho tool `send` trên web. Model không chọn được người nhận: chat ID đến từ trình duyệt
    của người dùng, và tuyệt đối không dùng TELEGRAM_CHAT_ID của chủ dự án."""
    if os.getenv("DISABLE_SEND") == "1":  # công tắc khẩn cấp của chủ dự án, mặc định không đặt
        return {"tool": "send_telegram", "status": "disabled_on_web",
                "message": "Gửi Telegram đã bị tắt trên bản web này."}
    chat = _chat_id.get()
    if not chat:
        return {"tool": "send_telegram", "status": "needs_chat_id",
                "message": "Chưa có chat ID Telegram của người dùng. Nhờ họ nhập chat ID ở mục 'nhắn telegram' rồi thử lại."}
    if not confirmed:
        return _real_send(text=text, confirmed=False)  # chỉ trả needs_confirmation, không gọi mạng
    if not _allow(chat):
        return {"tool": "send_telegram", "status": "rate_limited",
                "message": f"Mỗi chat ID chỉ nhận tối đa {SEND_LIMIT} tin mỗi giờ. Thử lại sau."}
    return _real_send(text=text[:MAX_SEND_CHARS], confirmed=True, chat_id=chat)


TOOL_FUNCTIONS["send"] = _web_send  # cùng dict mà chat.py dùng


def get_provider() -> Any:
    global _provider
    if _provider is None:
        _provider = make_provider(os.getenv("WEB_PROVIDER", "gemini"))
    return _provider


def clean_messages(payload: Any) -> list[dict[str, str]]:
    """Kiểm tra đầu vào, ném ValueError nếu không hợp lệ."""
    if not isinstance(payload, dict) or not isinstance(payload.get("messages"), list):
        raise ValueError("Thiếu danh sách messages")
    cleaned: list[dict[str, str]] = []
    for item in payload["messages"]:
        if not isinstance(item, dict):
            raise ValueError("Mỗi message phải là object")
        role, content = item.get("role"), item.get("content")
        if role not in ("user", "assistant") or not isinstance(content, str) or not content.strip():
            raise ValueError("Message cần role user/assistant và content là chuỗi không rỗng")
        cleaned.append({"role": role, "content": content[:MAX_CHARS]})
    cleaned = cleaned[-MAX_MESSAGES:]
    if not cleaned or cleaned[-1]["role"] != "user":
        raise ValueError("Tin nhắn cuối phải là của người dùng")
    return cleaned


def _summarize(result: Any) -> str:
    if not isinstance(result, dict):
        return ""
    if "error" in result:
        return f"lỗi {result.get('error')}: {str(result.get('message', ''))[:120]}"
    if result.get("awaiting_user"):
        return "hỏi lại người dùng"
    if "markdown" in result:
        return f"digest {result.get('item_count', 0)} mục"
    if isinstance(result.get("items"), list):
        return f"{len(result['items'])} kết quả"
    if "status" in result:
        return str(result["status"])
    return "ok"


def handle_chat(payload: Any) -> tuple[int, dict[str, Any]]:
    """Trả về (mã HTTP, nội dung JSON)."""
    try:
        history = clean_messages(payload)
    except ValueError as exc:
        return 400, {"error": str(exc)}

    raw_chat = payload.get("telegram_chat_id")
    chat = raw_chat.strip() if isinstance(raw_chat, str) else raw_chat
    if chat in (None, ""):
        chat = None
    elif not valid_chat_id(chat):
        return 400, {"error": "Chat ID Telegram không hợp lệ: chỉ gồm chữ số (5 đến 15 chữ số)."}

    messages = [{"role": "system", "content": _system_prompt}, *history]
    token = _chat_id.set(chat)
    try:
        result = run_model_tool_loop(
            provider=get_provider(),
            messages=messages,
            tools=_tools,
            model=None,
            max_tool_rounds=MAX_TOOL_ROUNDS,
        )
    except Exception as exc:  # lỗi provider/mạng: không lộ chi tiết dài
        return 502, {"error": f"{type(exc).__name__}: {str(exc)[:200]}"}
    finally:
        _chat_id.reset(token)

    events = [
        {
            "tool": e.get("tool"),
            "args": json.dumps(e.get("args", {}), ensure_ascii=False)[:300],
            "summary": _summarize(e.get("result")),
        }
        for e in result.get("tool_events", [])
    ]
    return 200, {"reply": result.get("assistant_text", ""), "status": result.get("status"), "tool_events": events}
