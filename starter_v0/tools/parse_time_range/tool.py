from __future__ import annotations

import re
from datetime import date, timedelta
from typing import Any

from tools._shared import err, fold_text

UNIT_DAYS = {"ngay": 1, "tuan": 7, "thang": 30, "nam": 365, "day": 1, "week": 7, "month": 30, "year": 365}
FIXED = [  # (cụm đã bỏ dấu, số ngày tính lùi từ hôm nay)
    ("hom nay", 1), ("today", 1),
    ("hom qua", 2), ("yesterday", 2),
    ("tuan nay", 7), ("tuan qua", 7), ("this week", 7), ("last week", 7),
    ("thang nay", 30), ("thang qua", 30), ("this month", 30), ("last month", 30),
    ("nam nay", 365), ("nam qua", 365), ("this year", 365), ("last year", 365),
]
COUNTED = re.compile(r"(?:(\d{1,4})\s*(ngay|tuan|thang|nam)\s*(?:qua|truoc|gan day))|(?:(?:last|past)\s+(\d{1,4})\s*(day|week|month|year)s?)")
MAX_DAYS = 3660


def _bucket(days: int) -> str:
    """Mức nhỏ nhất của `lookup` (day/week/month/year) đủ bao phủ số ngày."""
    for name, limit in (("day", 1), ("week", 7), ("month", 31), ("year", 366)):
        if days <= limit:
            return name
    return "year"


def _parse_today(today: str | None) -> date:
    if today is None or today == "":
        return date.today()
    if not isinstance(today, str):
        raise ValueError("today must be an ISO date string like 2026-11-10")
    try:
        return date.fromisoformat(today)
    except ValueError:
        raise ValueError("today must be an ISO date string like 2026-11-10") from None


def parse_time_range(text: str, today: str | None = None) -> dict[str, Any]:
    try:
        if not isinstance(text, str) or not text.strip():
            raise ValueError("text must be a non-empty string")
        base = _parse_today(today)
        folded = " " + " ".join(fold_text(text).split()) + " "

        days: int | None = None
        matched = ""
        counted = COUNTED.search(folded)
        if counted:
            number = int(counted.group(1) or counted.group(3))
            unit = counted.group(2) or counted.group(4)
            days, matched = number * UNIT_DAYS[unit], counted.group(0).strip()
            if days < 1 or days > MAX_DAYS:
                raise ValueError(f"time range must be between 1 and {MAX_DAYS} days")
        else:
            for phrase, span in FIXED:
                if f" {phrase} " in folded:
                    days, matched = span, phrase
                    break
        if days is None:
            return {"tool": "parse_time_range", "status": "unrecognized",
                    "message": "Không nhận ra cụm thời gian. Hỏi lại người dùng khoảng thời gian cụ thể."}

        yesterday_only = matched in {"hom qua", "yesterday"}
        end = base - timedelta(days=1) if yesterday_only else base
        start = end if yesterday_only else base - timedelta(days=days - 1)
        return {
            "tool": "parse_time_range",
            "status": "ok",
            "matched": matched,
            "today": base.isoformat(),
            "start_date": start.isoformat(),
            "end_date": end.isoformat(),
            "days": (end - start).days + 1,
            "timeframe": _bucket((base - start).days + 1),
            "note": "Tính theo ngày gần nhất (cuốn chiếu), không theo tuần hay tháng lịch. `timeframe` là mức nhỏ nhất của lookup đủ bao phủ khoảng này.",
        }
    except ValueError as exc:
        return err("parse_time_range", exc)
