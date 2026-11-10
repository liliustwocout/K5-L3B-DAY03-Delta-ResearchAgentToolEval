"""TODO CP3 (student): Tool Unit Test Challenge.

Each test below is a stub. Replace `pytest.skip(...)` with a real test.
Patterns to copy are in test_tools_examples.py. Fixtures are in conftest.py.

Rules:
- Offline only: mock HTTP with `fake_http`, set fake keys with `monkeypatch.setenv`.
- One behaviour per test. Name the test after the behaviour, not the function.
- Done = `pytest tests/ -v` shows 0 skipped, 0 failed.
"""
from __future__ import annotations

import pytest

from conftest import FakeResponse  # noqa: F401  (you will need it)
from tools import TOOL_FUNCTIONS  # noqa: F401

TODO = "TODO CP3 (student): implement this test"


# ---------------- clarify ----------------

def test_clarify_choice_returns_options_and_awaits_user() -> None:
    # Call clarify with response_type="choice" and 2 options.
    # Assert: options are returned unchanged, awaiting_user is True.
    pytest.skip(TODO)


# ---------------- format ----------------

def test_format_sections_groups_items_by_section() -> None:
    # Items with section "A", "B", "A" -> markdown has exactly one "## A" and one "## B".
    pytest.skip(TODO)


def test_format_thread_numbers_items() -> None:
    # template="thread" -> lines start with "1/", "2/", ...
    pytest.skip(TODO)


def test_format_empty_items_does_not_crash() -> None:
    # items=None and items=[] -> item_count == 0, no exception.
    pytest.skip(TODO)


# ---------------- send (guardrail) ----------------

def test_send_confirmed_posts_to_telegram(monkeypatch, fake_http) -> None:
    # Set TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID, mock HTTP.
    # Assert: exactly one POST, URL contains the token, json has chat_id + text, status == "sent".
    pytest.skip(TODO)


def test_send_confirmed_without_env_returns_error_and_no_request(fake_http) -> None:
    pytest.skip(TODO)


# ---------------- lookup ----------------

def test_lookup_without_timeframe_omits_time_range(monkeypatch, fake_http) -> None:
    # timeframe=None -> request body has no "time_range" key.
    pytest.skip(TODO)


# ---------------- fetch ----------------

def test_fetch_maps_firecrawl_response(monkeypatch, fake_http) -> None:
    # Mock {"data": {"markdown": "...", "metadata": {"title": "T", "sourceURL": "https://..."}}}
    # Assert title/url/source/summary in result["items"][0].
    pytest.skip(TODO)


def test_fetch_truncates_markdown_to_4000_chars(monkeypatch, fake_http) -> None:
    pytest.skip(TODO)


# ---------------- timeline / social_search ----------------

def test_timeline_respects_limit_and_skips_items_without_id(monkeypatch, fake_http) -> None:
    # Mock {"timeline": [...]} with 1 item missing tweet_id and 6 valid items, limit=3.
    # Assert 3 items, and each url looks like https://x.com/<handle>/status/<id>.
    pytest.skip(TODO)


def test_social_search_passes_search_type(monkeypatch, fake_http) -> None:
    # Assert the request params carry the query and search_type ("Top" / "Latest").
    pytest.skip(TODO)


# ---------------- policy (local knowledge + trust boundary) ----------------

def test_policy_empty_query_returns_no_results() -> None:
    pytest.skip(TODO)


def test_policy_area_filter_only_returns_that_area() -> None:
    # policy_area="data_privacy" -> every result has policy_area == "data_privacy".
    pytest.skip(TODO)


def test_policy_instruction_like_lines_go_to_untrusted_text() -> None:
    # One policy file contains a quoted line that tries to give the assistant orders.
    # Query that section (source_citation) and assert: that line is in untrusted_text, NOT in facts.
    pytest.skip(TODO)


# ---------------- YOUR NEW TOOL(S) ----------------
# Write at least 3 tests per tool your team adds:
#   1. happy path (mocked if it calls an API)
#   2. bad / missing input from the model (empty string, wrong type, out-of-enum value)
#   3. failure path (missing key, HTTP error, timeout) -> returns error dict, does not raise

def test_evidence_card_shows_conflicting_sources_with_links() -> None:
    card = TOOL_FUNCTIONS["build_evidence_card"](
        claim="Startup A gọi vốn 50 triệu USD",
        evidence=[
            {"url": "https://example.com/a", "summary": "Công bố 50 triệu USD.", "stance": "supports"},
            {"url": "https://example.org/b", "summary": "Đưa tin 40 triệu USD.", "stance": "contradicts"},
        ],
    )

    assert card["status"] == "mixed"
    markdown = card["markdown"]
    assert "*✅ Nguồn ủng hộ*\n• [Nguồn 1](https://example.com/a) — Công bố 50 triệu USD." in markdown
    assert "*⚠️ Nguồn đưa thông tin khác*\n• [Nguồn 2](https://example.org/b) — Đưa tin 40 triệu USD." in markdown
    assert "Chưa đủ căn cứ để chốt." in markdown


def test_evidence_card_reports_insufficient_evidence_when_no_source_is_clear() -> None:
    card = TOOL_FUNCTIONS["build_evidence_card"](
        claim="Dự án [A] đạt *mục tiêu*",
        evidence=[{
            "url": "https://example.com/report_(2026)",
            "summary": "Báo cáo chỉ ghi trạng thái đang_triển_khai.",
            "stance": "unclear",
        }],
    )

    assert card["status"] == "insufficient"
    markdown = card["markdown"]
    assert r"Dự án \[A] đạt \*mục tiêu\*" in markdown
    assert "[Nguồn 1](https://example.com/report_%282026%29)" in markdown
    assert r"đang\_triển\_khai" in markdown
    assert "Chưa đủ bằng chứng" in markdown


def test_evidence_card_rejects_unknown_stance_from_model() -> None:
    card = TOOL_FUNCTIONS["build_evidence_card"](
        claim="Một nhận định",
        evidence=[{"url": "https://example.com/a", "summary": "Trích đoạn.", "stance": "verified"}],
    )

    assert card["error"] == "ValueError"
    assert "evidence[0].stance" in card["message"]
    assert "markdown" not in card


def test_evidence_card_returns_error_for_malformed_source_url() -> None:
    card = TOOL_FUNCTIONS["build_evidence_card"](
        claim="Một nhận định",
        evidence=[{"url": "https:///missing-host", "summary": "Trích đoạn.", "stance": "supports"}],
    )

    assert card["error"] == "ValueError"
    assert "evidence[0].url" in card["message"]
    assert "markdown" not in card


def test_metric_card_distinguishes_percentage_points_from_relative_change() -> None:
    card = TOOL_FUNCTIONS["build_metric_delta_card"](
        "Tỷ lệ chuyển đổi",
        {"value": 20, "period": "Tháng 9", "unit": "%", "url": "https://example.com/september"},
        {"value": 26, "period": "Tháng 10", "unit": "%", "url": "https://example.org/october"},
    )

    assert card["absolute_delta"] == 6
    assert card["relative_change_percent"] == 30
    assert card["absolute_display"] == "+6 điểm phần trăm"
    assert card["relative_display"] == "+30%"
    assert "[Nguồn kỳ gốc](https://example.com/september)" in card["markdown"]
    assert "[Nguồn kỳ mới](https://example.org/october)" in card["markdown"]


@pytest.mark.parametrize("baseline", [0, -5])
def test_metric_card_omits_relative_change_for_nonpositive_baseline(baseline: int) -> None:
    card = TOOL_FUNCTIONS["build_metric_delta_card"](
        "Số lượt",
        {"value": baseline, "period": "Kỳ 1", "unit": "lượt"},
        {"value": 5, "period": "Kỳ 2", "unit": "lượt", "url": ""},
    )

    assert card["absolute_delta"] == 5 - baseline
    assert card["relative_change_percent"] is None
    assert card["relative_display"] is None
    assert card["current"]["url"] is None
    assert card["relative_note"] in card["markdown"]


def test_metric_card_rejects_incompatible_units() -> None:
    card = TOOL_FUNCTIONS["build_metric_delta_card"](
        "Doanh thu",
        {"value": 20, "period": "Kỳ 1", "unit": "USD"},
        {"value": 26, "period": "Kỳ 2", "unit": "VND"},
    )

    assert card["error"] == "ValueError"
    assert "same unit" in card["message"]
    assert "markdown" not in card


def test_metric_card_rejects_non_numeric_observation() -> None:
    card = TOOL_FUNCTIONS["build_metric_delta_card"](
        "Doanh thu",
        {"value": 20, "period": "Kỳ 1", "unit": "USD"},
        {"value": "26", "period": "Kỳ 2", "unit": "USD"},
    )

    assert card["error"] == "ValueError"
    assert "current.value" in card["message"]


def test_source_chain_counts_three_reports_using_the_same_origin() -> None:
    origin = "https://example.org/press"
    result = TOOL_FUNCTIONS["trace_source_chain"]([
        {"url": "https://example.com/a", "cites": [origin, origin]},
        {"url": "https://example.com/a", "cites": [origin]},
        {"url": "https://example.com/b", "cites": [origin]},
        {"url": "https://example.com/c", "cites": [origin]},
        {"url": origin, "title": "Thông cáo", "cites": []},
    ])

    assert result["entry_count"] == 3
    assert result["roots"] == [{"url": origin, "title": "Thông cáo", "article_count": 3}]
    assert len(result["edges"]) == 3
    assert f"[Nguồn 1]({origin})" in result["markdown"]


def test_source_chain_traces_two_separate_origins_through_intermediate_articles() -> None:
    relay = "https://example.com/relay"
    first, second = "https://example.org/first", "https://example.org/second"
    result = TOOL_FUNCTIONS["trace_source_chain"]([
        {"url": "https://example.com/a", "cites": [relay]},
        {"url": relay, "cites": [first]},
        {"url": "https://example.com/b", "cites": [second]},
        {"url": first, "cites": []},
        {"url": second, "cites": []},
    ])

    assert result["entry_count"] == 2
    assert {root["url"]: root["article_count"] for root in result["roots"]} == {first: 1, second: 1}
    assert result["unresolved_urls"] == []


def test_source_chain_marks_an_unavailable_citation_as_unresolved() -> None:
    unavailable = "https://example.org/unavailable"
    result = TOOL_FUNCTIONS["trace_source_chain"]([
        {"url": "https://example.com/a", "cites": [unavailable]},
    ])

    assert result["roots"] == []
    assert result["unresolved_urls"] == [unavailable]
    assert result["nodes"][-1]["kind"] == "unresolved"


def test_source_chain_returns_error_for_circular_citations() -> None:
    first, second = "https://example.org/first", "https://example.org/second"
    result = TOOL_FUNCTIONS["trace_source_chain"]([
        {"url": first, "cites": [second]},
        {"url": second, "cites": [first]},
    ])

    assert result["error"] == "ValueError"
    assert "cycle" in result["message"]
    assert "markdown" not in result


def test_source_chain_returns_error_for_malformed_citation_input() -> None:
    result = TOOL_FUNCTIONS["trace_source_chain"]([
        {"url": "https://example.com/a", "cites": "https://example.org/press"},
    ])

    assert result["error"] == "ValueError"
    assert "articles[0].cites" in result["message"]
