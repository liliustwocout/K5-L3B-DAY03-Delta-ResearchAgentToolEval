from __future__ import annotations

import json
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
EXAMPLE_ORIGIN = "https://example.org/press"
EXAMPLE_ARTICLES = [
    {"title": "Báo A", "url": "https://example.com/a", "cites": [EXAMPLE_ORIGIN]},
    {"title": "Báo B", "url": "https://example.com/b", "cites": [EXAMPLE_ORIGIN]},
    {"title": "Báo C", "url": "https://example.net/c", "cites": [EXAMPLE_ORIGIN]},
    {"title": "Thông cáo Startup A", "url": EXAMPLE_ORIGIN, "cites": []},
]
EXAMPLE_SOURCE_QUESTION = (
    "Ba bài báo có dùng chung nguồn không? Vẽ sơ đồ từ đúng bốn tài liệu minh họa dưới đây.\n"
    "- Báo A (https://example.com/a) dẫn Thông cáo Startup A.\n"
    "- Báo B (https://example.com/b) dẫn Thông cáo Startup A.\n"
    "- Báo C (https://example.net/c) dẫn Thông cáo Startup A.\n"
    "- Thông cáo Startup A (https://example.org/press) là tài liệu cuối, có danh sách trích dẫn rỗng."
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


def render_source_map(card: dict) -> None:
    with st.container(border=True):
        st.caption("BẢN ĐỒ TRÍCH DẪN")
        st.subheader(f"{card['entry_count']} bài đầu chuỗi · {len(card['roots'])} nguồn cuối chuỗi")
        nodes = card["nodes"]
        node_ids = {node["url"]: index for index, node in enumerate(nodes, 1)}
        colors = {"article": "#E8EFF8", "root": "#D6F3E6", "unresolved": "#FFF0CA"}
        lines = [
            'digraph sources {',
            '  graph [bgcolor="transparent"];',
            '  node [shape=box, style="rounded,filled", fontname="Arial", fontcolor="#172033", color="#718099"];',
            '  edge [color="#718099"];',
        ]
        links = []
        for index, node in enumerate(nodes, 1):
            title = " ".join(node["title"].split())
            short_title = title[:41] + "…" if len(title) > 42 else title
            label = json.dumps(f"{index}. {short_title}", ensure_ascii=False)
            lines.append(f'  n{index} [label={label}, fillcolor="{colors[node["kind"]]}"];')
            links.append(f"[Tài liệu {index}]({node['url']})")
        for edge in card["edges"]:
            lines.append(f"  n{node_ids[edge['from_url']]} -> n{node_ids[edge['to_url']]};")
        st.graphviz_chart("\n".join([*lines, "}"]))
        st.caption("Mũi tên đi từ bài viết đến tài liệu được trích. Xanh lá là điểm cuối trong dữ liệu.")
        if card["unresolved_urls"]:
            st.caption(f"Màu vàng · {len(card['unresolved_urls'])} tài liệu chưa có dữ liệu để lần tiếp.")
        st.markdown(" · ".join(links))


CARD_RENDERERS = {
    "build_metric_delta_card": render_metric_card,
    "trace_source_chain": render_source_map,
}


def render_message(message: dict) -> None:
    with st.chat_message(message["role"]):
        for card in message.get("cards", []):
            CARD_RENDERERS[card["tool"]](card)
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
        metric_tab, source_tab = st.tabs(["So sánh số liệu", "Truy dấu nguồn"])
        with metric_tab:
            render_metric_card(TOOL_FUNCTIONS["build_metric_delta_card"](EXAMPLE_METRIC, EXAMPLE_BASELINE, EXAMPLE_CURRENT))
        with source_tab:
            render_source_map(TOOL_FUNCTIONS["trace_source_chain"](EXAMPLE_ARTICLES))
    for message in history:
        render_message(message)

    metric_button, source_button = st.columns(2)
    use_example = metric_button.button("Chạy mẫu số liệu")
    use_source_example = source_button.button("Chạy mẫu truy dấu nguồn")
    question = st.chat_input("Hỏi về số liệu, bằng chứng hoặc nguồn gốc của một tin…")
    if use_source_example:
        question = EXAMPLE_SOURCE_QUESTION
    elif use_example:
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
        if event["tool"] in CARD_RENDERERS and "markdown" in event["result"]
    ]
    assistant_message = {"role": "assistant", "content": result["assistant_text"], "cards": cards}
    history.extend([user_message, assistant_message])
    render_message(assistant_message)


if __name__ == "__main__":
    main()
