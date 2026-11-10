from __future__ import annotations

import re
import unicodedata
from pathlib import Path
from typing import Any
from urllib.parse import quote, urlparse, urlsplit


ROOT = Path(__file__).resolve().parents[1]
TIMEOUT = 30


def err(tool: str, exc: Exception) -> dict[str, Any]:
    return {"tool": tool, "error": type(exc).__name__, "message": str(exc)}


def telegram_markdown_text(value: str) -> str:
    return re.sub(r"([_*`\[])", r"\\\1", " ".join(value.split()))


def telegram_markdown_url(url: Any, field: str) -> str:
    if not isinstance(url, str) or any(char.isspace() or ord(char) < 32 for char in url):
        raise ValueError(f"{field} must be an HTTP(S) URL")
    parts = urlsplit(url)
    if parts.scheme not in {"http", "https"} or not parts.hostname or parts.username is not None or "\\" in url:
        raise ValueError(f"{field} must be an HTTP(S) URL without credentials")
    # Encode parentheses so the URL cannot terminate the Markdown link.
    return quote(url, safe=":/?#[]@!$&'*+,;=%")


def domain(url: str) -> str:
    try:
        return urlparse(url).netloc.replace("www.", "")
    except Exception:
        return ""


def fold_text(text: str) -> str:
    decomposed = unicodedata.normalize("NFD", text.lower())
    return "".join(ch for ch in decomposed if unicodedata.category(ch) != "Mn")


def terms(text: str) -> set[str]:
    stopwords = {
        "a", "an", "and", "are", "as", "at", "by", "for", "from", "in", "is", "of", "on", "or", "the", "to",
        "ban", "bao", "can", "cho", "co", "cua", "duoc", "gi", "giup", "la", "lam", "minh", "mot", "nay",
        "nen", "the", "thi", "trong", "va", "ve", "voi",
    }
    folded = fold_text(text)
    return {term for term in re.findall(r"[a-z0-9]+", folded) if len(term) > 1 and term not in stopwords}

