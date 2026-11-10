"""UI Streamlit cho Research Agent.

Chạy:  streamlit run app.py   ->  http://localhost:8501
Cần key của một provider trong .env (xem docs/TOOL-SETUP.md).
"""
from __future__ import annotations

import json
import os

import streamlit as st

from chat import ARTIFACTS_DIR, run_model_tool_loop  # chat.py nạp .env khi import
from providers import make_provider
from tools import load_tool_declarations, to_openai_tools

SAMPLES = [
    "Tweet mới nhất của Sam Altman là gì?",
    "Mọi người đang bàn gì về GPT-5 trên Twitter?",
    "Tin tức AI hôm nay có gì nổi bật?",
    "Tóm tắt 5 tweet mới nhất giúp mình",
    "Đăng bản tin này lên Telegram giúp mình",
]
PROVIDERS = {
    "openrouter": "OPENROUTER_API_KEY",
    "openai": "OPENAI_API_KEY",
    "anthropic": "ANTHROPIC_API_KEY",
    "gemini": "GEMINI_API_KEY",
    "ollama": None,
}

st.set_page_config(page_title="Research Agent", page_icon="🔎")
st.title("🔎 Research Agent")
st.caption("Tìm tin, tweet, đọc link, paper arXiv, tra chính sách. Thiếu thông tin thì agent hỏi lại.")

# Mặc định chọn provider đầu tiên có key trong .env.
default = next((n for n, k in PROVIDERS.items() if k and os.getenv(k)), "openrouter")

with st.sidebar:
    provider_name = st.selectbox("Provider", list(PROVIDERS), index=list(PROVIDERS).index(default))

    st.subheader("Câu hỏi mẫu")
    st.caption("Bấm một nút để gửi luôn câu đó.")
    for i, sample in enumerate(SAMPLES):
        if st.button(sample, key=f"sample_{i}", use_container_width=True):
            st.session_state["pending"] = sample

    st.subheader("Gửi lên Telegram")
    st.markdown(
        "1. Gõ ví dụ: `Đăng \"Xin chào\" lên Telegram`\n"
        "2. Agent **hỏi xác nhận** trước, chưa gửi.\n"
        "3. Trả lời `Có` thì agent mới gửi; trả lời `Không` thì dừng.\n\n"
        "Cần `TELEGRAM_BOT_TOKEN` và `TELEGRAM_CHAT_ID` trong `.env`, và đã bấm **Start** với bot. "
        "Tin sẽ được gửi thật."
    )
    if st.button("Xóa hội thoại", use_container_width=True):
        st.session_state["history"] = []
        st.rerun()


@st.cache_resource
def _setup(name: str):
    prompt = (ARTIFACTS_DIR / "system_prompt.md").read_text(encoding="utf-8")
    tools = to_openai_tools(load_tool_declarations(ARTIFACTS_DIR / "tools.yaml"))
    return make_provider(name), prompt, tools


provider, system_prompt, tools = _setup(provider_name)
st.session_state.setdefault("history", [])

for msg in st.session_state["history"]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

user_text = st.chat_input("Hỏi gì đó (tin tức, tweet, URL, paper, policy)...") or st.session_state.pop("pending", None)

if user_text:
    st.session_state["history"].append({"role": "user", "content": user_text})
    with st.chat_message("user"):
        st.markdown(user_text)
    messages = [{"role": "system", "content": system_prompt}, *st.session_state["history"][-10:]]
    with st.chat_message("assistant"):
        with st.spinner("Đang xử lý..."):
            try:
                out = run_model_tool_loop(provider=provider, messages=messages, tools=tools, model=None, max_tool_rounds=4)
            except Exception as exc:  # lỗi provider/mạng
                out = {"assistant_text": f"Lỗi: {type(exc).__name__}: {str(exc)[:200]}", "tool_events": []}
        for ev in out["tool_events"]:
            with st.expander(f"🔧 {ev['tool']}"):
                st.code(json.dumps(ev["args"], ensure_ascii=False, indent=2), language="json")
        st.markdown(out["assistant_text"])
    st.session_state["history"].append({"role": "assistant", "content": out["assistant_text"]})
