from __future__ import annotations

import os

import streamlit as st

from chat import ARTIFACTS_DIR, run_model_tool_loop
from providers import make_provider
from tools import TOOL_FUNCTIONS, load_tool_declarations, to_openai_tools


EXAMPLE_METRIC = "Tỷ lệ chuyển đổi"
EXAMPLE_BASELINE = {"period": "Tháng 9", "value": 20, "unit": "%", "url": "https://example.com/september"}
EXAMPLE_CURRENT = {"period": "Tháng 10", "value": 26, "unit": "%", "url": "https://example.org/october"}
EXAMPLE_QUESTION = (
    "Tính mức thay đổi tỷ lệ chuyển đổi từ tháng 9 (20%) sang tháng 10 (26%). "
    "Dùng hai số liệu minh họa đã cho. "
    "Link trích dẫn tháng 9 là https://example.com/september và tháng 10 là https://example.org/october."
)


def render_metric_card(card: dict) -> None:
    with st.container(border=True):
        st.caption("SO SÁNH HAI KỲ")
        st.subheader(card["metric"])
        before, after = card["baseline"], card["current"]
        before_column, after_column = st.columns(2)
        before_column.metric(before["period"], before["display"])
        after_column.metric(after["period"], after["display"])
        change_column, relative_column = st.columns(2)
        change_column.metric("Chênh lệch tuyệt đối", card["absolute_display"])
        relative_column.metric("So với kỳ gốc", card["relative_display"] or "—")
        if card["relative_note"]:
            st.caption(card["relative_note"])
        links = [
            f"[{label}]({observation['url']})"
            for label, observation in (("Nguồn kỳ gốc", before), ("Nguồn kỳ mới", after))
            if observation["url"]
        ]
        if links:
            st.markdown(" · ".join(links))


def render_message(message: dict) -> None:
    with st.chat_message(message["role"]):
        for card in message.get("cards", []):
            render_metric_card(card)
        if message["content"]:
            st.markdown(message["content"])


def main() -> None:
    st.set_page_config(page_title="Delta Research", page_icon="📊", layout="centered")
    st.title("Delta Research")
    st.caption("Đọc nguồn, đối chiếu thông tin và giải thích số liệu.")

    if "messages" not in st.session_state:
        st.session_state.messages = []
    history = st.session_state.messages

    if not history:
        st.markdown("**Dữ liệu minh họa**")
        render_metric_card(TOOL_FUNCTIONS["build_metric_delta_card"](EXAMPLE_METRIC, EXAMPLE_BASELINE, EXAMPLE_CURRENT))
    for message in history:
        render_message(message)

    use_example = st.button("Chạy câu hỏi mẫu")
    question = st.chat_input("Hỏi về hai kỳ số liệu hoặc yêu cầu đối chiếu nguồn…")
    if use_example:
        question = EXAMPLE_QUESTION
    if not question:
        return
    if not os.getenv("OPENROUTER_API_KEY"):
        st.error("Cần cấu hình OPENROUTER_API_KEY trong starter_v0/.env để chạy chat live.")
        return

    prompt = (ARTIFACTS_DIR / "system_prompt.md").read_text(encoding="utf-8")
    prompt += "\nThis web demo is read-only. For Telegram requests show a preview and direct the user to the CLI to post."
    declarations = load_tool_declarations(ARTIFACTS_DIR / "tools.yaml")
    tools = to_openai_tools([tool for tool in declarations if tool["name"] != "send"])
    user_message = {"role": "user", "content": question}
    messages = [
        {"role": "system", "content": prompt},
        *({"role": message["role"], "content": message["content"]} for message in history[-10:]),
        user_message,
    ]
    render_message(user_message)
    try:
        with st.spinner("Đang xử lý câu hỏi…"):
            result = run_model_tool_loop(
                provider=make_provider("openrouter"), messages=messages, tools=tools, model=None, max_tool_rounds=4,
            )
    except Exception as exc:
        st.error(f"Chat live gặp lỗi ({type(exc).__name__}).")
        return

    cards = [
        event["result"] for event in result["tool_events"]
        if event["tool"] == "build_metric_delta_card" and "markdown" in event["result"]
    ]
    assistant_message = {"role": "assistant", "content": result["assistant_text"], "cards": cards}
    history.extend([user_message, assistant_message])
    render_message(assistant_message)


if __name__ == "__main__":
    main()
