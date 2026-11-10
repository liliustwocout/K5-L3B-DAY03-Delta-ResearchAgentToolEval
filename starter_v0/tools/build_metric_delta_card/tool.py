from __future__ import annotations

from decimal import Decimal
from math import isfinite
from typing import Any

from tools._shared import err, telegram_markdown_text, telegram_markdown_url


def _read_observation(observation: Any, field: str) -> tuple[Decimal, str, str, str | None]:
    if not isinstance(observation, dict):
        raise ValueError(f"{field} must be an object")
    value = observation.get("value")
    if type(value) not in (int, float) or not isfinite(value):
        raise ValueError(f"{field}.value must be a finite number")
    period, unit = observation.get("period"), observation.get("unit")
    if not isinstance(period, str) or not period.strip():
        raise ValueError(f"{field}.period must be a non-empty string")
    if not isinstance(unit, str) or not unit.strip():
        raise ValueError(f"{field}.unit must be a non-empty string")
    raw_url = observation.get("url")
    url = None if raw_url in (None, "") else telegram_markdown_url(raw_url, f"{field}.url")
    return Decimal(str(value)), period.strip(), unit.strip(), url


def _display(value: Decimal, unit: str = "", *, signed: bool = False) -> str:
    number = f"{value:+,.6f}" if signed and value else f"{value:,.6f}"
    number = number.rstrip("0").rstrip(".")
    if unit == "%":
        return f"{number}%"
    return f"{number} {unit}".rstrip()


def build_metric_delta_card(metric: str, baseline: dict[str, Any], current: dict[str, Any]) -> dict[str, Any]:
    try:
        if not isinstance(metric, str) or not metric.strip():
            raise ValueError("metric must be a non-empty string")
        before, before_period, unit, before_url = _read_observation(baseline, "baseline")
        after, after_period, current_unit, after_url = _read_observation(current, "current")
        if unit != current_unit:
            raise ValueError("baseline and current must use the same unit")

        difference = after - before
        relative = difference / before * 100 if before > 0 else None
        if not isfinite(difference) or (relative is not None and not isfinite(relative)):
            raise ValueError("calculated change is outside the supported numeric range")

        delta_unit = "điểm phần trăm" if unit == "%" else unit
        before_display = _display(before, unit)
        after_display = _display(after, unit)
        absolute_display = _display(difference, delta_unit, signed=True)
        relative_display = _display(relative, "%", signed=True) if relative is not None else None
        baseline_note = "Cần mốc gốc lớn hơn 0 để báo phần trăm thay đổi."

        lines = [
            f"📊 *Thay đổi số liệu*\n{telegram_markdown_text(metric)}",
            f"{telegram_markdown_text(before_period)} → {telegram_markdown_text(after_period)}",
            f"{telegram_markdown_text(before_display)} → {telegram_markdown_text(after_display)}",
            f"*Chênh lệch tuyệt đối* · {telegram_markdown_text(absolute_display)}",
            f"*So với kỳ gốc* · {relative_display or baseline_note}",
        ]
        if before_url:
            lines.append(f"• [Nguồn kỳ gốc]({before_url})")
        if after_url:
            lines.append(f"• [Nguồn kỳ mới]({after_url})")
        markdown = "\n".join(lines)
        if len(markdown.encode("utf-16-le")) // 2 > 4096:
            raise ValueError("metric card is too long for one Telegram message")

        return {
            "tool": "build_metric_delta_card",
            "metric": metric.strip(),
            "baseline": {"period": before_period, "display": before_display, "url": before_url},
            "current": {"period": after_period, "display": after_display, "url": after_url},
            "absolute_delta": float(difference),
            "absolute_display": absolute_display,
            "relative_change_percent": float(relative) if relative is not None else None,
            "relative_display": relative_display,
            "relative_note": baseline_note if relative is None else None,
            "markdown": markdown,
        }
    except (ValueError, OverflowError) as exc:
        return err("build_metric_delta_card", exc)
