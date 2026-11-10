from __future__ import annotations

import re
from typing import Any
from urllib.parse import quote, urlsplit

from tools._shared import err


HEADINGS = {
    "supports": "✅ Nguồn ủng hộ",
    "contradicts": "⚠️ Nguồn đưa thông tin khác",
    "unclear": "🧩 Nguồn chưa đủ rõ",
}


def _markdown_text(value: str) -> str:
    return re.sub(r"([_*`\[])", r"\\\1", " ".join(value.split()))


def _markdown_url(url: Any, index: int) -> str:
    if not isinstance(url, str) or any(char.isspace() or ord(char) < 32 for char in url):
        raise ValueError(f"evidence[{index}].url must be an HTTP(S) URL")
    parts = urlsplit(url)
    if parts.scheme not in {"http", "https"} or not parts.hostname or parts.username is not None or "\\" in url:
        raise ValueError(f"evidence[{index}].url must be an HTTP(S) URL without credentials")
    # Encode parentheses so the URL cannot terminate the Telegram Markdown link.
    return quote(url, safe=":/?#[]@!$&'*+,;=%")


def build_evidence_card(claim: str, evidence: list[dict[str, str]]) -> dict[str, Any]:
    try:
        if not isinstance(claim, str) or not claim.strip():
            raise ValueError("claim must be a non-empty string")
        if not isinstance(evidence, list):
            raise ValueError("evidence must be a list")

        groups: dict[str, list[str]] = {stance: [] for stance in HEADINGS}
        for index, item in enumerate(evidence):
            if not isinstance(item, dict):
                raise ValueError(f"evidence[{index}] must be an object")
            stance = item.get("stance")
            if not isinstance(stance, str) or stance not in groups:
                raise ValueError(f"evidence[{index}].stance must be supports, contradicts, or unclear")
            summary = item.get("summary")
            if not isinstance(summary, str) or not summary.strip():
                raise ValueError(f"evidence[{index}].summary must be a non-empty string")
            url = _markdown_url(item.get("url"), index)
            groups[stance].append(f"• [Nguồn {index + 1}]({url}) — {_markdown_text(summary)}")

        if groups["supports"] and groups["contradicts"]:
            status = "mixed"
            conclusion = "Các nguồn được cung cấp mâu thuẫn. Chưa đủ căn cứ để chốt."
        elif groups["supports"]:
            status = "support_only"
            conclusion = "Có nguồn ủng hộ nhận định trong danh sách này. Kết luận chỉ dựa trên các nguồn đã cho."
        elif groups["contradicts"]:
            status = "contradiction_only"
            conclusion = "Có nguồn đưa thông tin trái với nhận định trong danh sách này."
        else:
            status = "insufficient"
            conclusion = "Chưa đủ bằng chứng trong các nguồn được cung cấp để đánh giá nhận định."

        sections = [f"🔎 *Đối chiếu bằng chứng*\n{_markdown_text(claim)}"]
        for stance, entries in groups.items():
            if entries:
                sections.append("\n".join([f"*{HEADINGS[stance]}*", *entries]))
        sections.append(f"*Kết luận*\n{conclusion}")
        markdown = "\n\n".join(sections)
        if len(markdown.encode("utf-16-le")) // 2 > 4096:
            raise ValueError("Evidence card is too long for one Telegram message. Use fewer or shorter excerpts.")
        return {"tool": "build_evidence_card", "status": status, "markdown": markdown}
    except ValueError as exc:
        return err("build_evidence_card", exc)
