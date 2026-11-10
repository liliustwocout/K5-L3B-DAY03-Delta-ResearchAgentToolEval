from __future__ import annotations

from typing import Any
from urllib.parse import urlsplit

from tools._shared import err

# Danh sách nhỏ theo chính sách trích dẫn nguồn (company_policy/source-citation-policy.md).
TIER1 = {
    "arxiv.org", "openai.com", "anthropic.com", "deepmind.google", "ai.google", "blog.google",
    "github.com", "huggingface.co", "nature.com", "science.org", "who.int", "europa.eu",
}
TIER1_SUFFIXES = (".gov", ".edu", ".gov.vn", ".edu.vn")
TIER2 = {
    "reuters.com", "apnews.com", "bloomberg.com", "theverge.com", "techcrunch.com", "wired.com",
    "nytimes.com", "bbc.com", "bbc.co.uk", "wsj.com", "ft.com", "arstechnica.com", "cnn.com",
    "vnexpress.net", "tuoitre.vn", "thanhnien.vn",
}
TIER3 = {
    "x.com", "twitter.com", "reddit.com", "facebook.com", "medium.com", "youtube.com", "tiktok.com",
    "news.ycombinator.com", "t.me", "substack.com", "linkedin.com",
}
LABELS = {
    "tier1": "Nguồn gốc hoặc chính thức",
    "tier2": "Báo chí uy tín",
    "tier3": "Mạng xã hội, diễn đàn (chỉ là tín hiệu ban đầu)",
    "unknown": "Chưa xác định",
    "invalid": "Không phải URL hợp lệ",
}
MAX_URLS = 50


def _host(url: str) -> str | None:
    """Tên miền chữ thường, bỏ `www.` và cổng. Trả None nếu không phải URL http(s) hợp lệ."""
    try:
        parts = urlsplit(url.strip())
        host = parts.hostname
    except ValueError:
        return None
    if parts.scheme not in {"http", "https"} or not host:
        return None
    host = host.lower()
    return host[4:] if host.startswith("www.") else host


def _matches(host: str, names: set[str]) -> bool:
    # Khớp đúng tên miền hoặc tên miền con, để `arxiv.org.evil.com` và `notarxiv.org` không lọt vào tier1.
    return any(host == name or host.endswith("." + name) for name in names)


def _tier(host: str) -> str:
    if _matches(host, TIER1) or host.endswith(TIER1_SUFFIXES):
        return "tier1"
    if _matches(host, TIER2):
        return "tier2"
    if _matches(host, TIER3):
        return "tier3"
    return "unknown"


def rate_sources(urls: list[str]) -> dict[str, Any]:
    try:
        if not isinstance(urls, list):
            raise ValueError("urls must be a list of URL strings")
        if len(urls) > MAX_URLS:
            raise ValueError(f"at most {MAX_URLS} urls per call")
        items: list[dict[str, str]] = []
        summary: dict[str, int] = {}
        for index, url in enumerate(urls):
            if not isinstance(url, str):
                raise ValueError(f"urls[{index}] must be a string")
            host = _host(url)
            tier = _tier(host) if host else "invalid"
            items.append({"url": url, "domain": host or "", "tier": tier, "label": LABELS[tier]})
            summary[tier] = summary.get(tier, 0) + 1
        return {
            "tool": "rate_sources",
            "items": items,
            "summary": summary,
            "note": "Phân loại theo tên miền, không đánh giá nội dung từng bài.",
        }
    except ValueError as exc:
        return err("rate_sources", exc)
