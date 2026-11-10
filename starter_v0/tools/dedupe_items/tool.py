from __future__ import annotations

import re
from typing import Any
from urllib.parse import parse_qsl, urlencode, urlsplit

from tools._shared import err, fold_text

TRACKING_PARAMS = {"fbclid", "gclid", "ref", "ref_src", "igshid", "mc_cid", "mc_eid"}


def _norm_url(url: str) -> str | None:
    """Đưa URL về dạng so sánh: bỏ www, fragment, tham số theo dõi, dấu `/` cuối; sắp xếp tham số."""
    try:
        parts = urlsplit(url.strip())
        host = (parts.hostname or "").lower()
    except ValueError:
        return None
    if not host:
        return None
    if host.startswith("www."):
        host = host[4:]
    query = sorted(
        (key, value)
        for key, value in parse_qsl(parts.query, keep_blank_values=True)
        if not key.lower().startswith("utm_") and key.lower() not in TRACKING_PARAMS
    )
    path = parts.path.rstrip("/") or "/"
    return f"{host}{path}" + (f"?{urlencode(query)}" if query else "")


def _norm_title(title: str) -> str | None:
    text = re.sub(r"[^a-z0-9 ]+", " ", fold_text(title))
    text = " ".join(text.split())
    return text or None


def dedupe_items(items: list[dict[str, Any]]) -> dict[str, Any]:
    try:
        if not isinstance(items, list):
            raise ValueError("items must be a list")
        kept: list[dict[str, Any]] = []
        removed: list[dict[str, Any]] = []
        seen_url: dict[str, int] = {}
        seen_title: dict[str, int] = {}
        for index, item in enumerate(items):
            if not isinstance(item, dict):
                removed.append({"index": index, "reason": "not_an_object"})
                continue
            url, title = item.get("url"), item.get("title")
            url_key = _norm_url(url) if isinstance(url, str) else None
            title_key = _norm_title(title) if isinstance(title, str) else None
            if url_key and url_key in seen_url:
                removed.append({"index": index, "reason": "same_url", "duplicate_of_index": seen_url[url_key], "title": title, "url": url})
            elif title_key and title_key in seen_title:
                removed.append({"index": index, "reason": "same_title", "duplicate_of_index": seen_title[title_key], "title": title, "url": url})
            else:
                kept.append(item)
                if url_key:
                    seen_url[url_key] = index
                if title_key:
                    seen_title[title_key] = index
        return {
            "tool": "dedupe_items",
            "items": kept,
            "kept_count": len(kept),
            "removed": removed,
            "removed_count": len(removed),
        }
    except ValueError as exc:
        return err("dedupe_items", exc)
