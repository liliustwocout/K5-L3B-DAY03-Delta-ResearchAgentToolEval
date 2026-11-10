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


# ---------------- rate_sources ----------------

def test_rate_sources_groups_urls_by_domain_tier() -> None:
    result = TOOL_FUNCTIONS["rate_sources"](urls=[
        "https://arxiv.org/abs/1706.03762",
        "https://www.reuters.com/world/x",
        "https://x.com/sama/status/1",
        "https://random-blog.io/post",
    ])

    assert [item["tier"] for item in result["items"]] == ["tier1", "tier2", "tier3", "unknown"]
    assert result["summary"] == {"tier1": 1, "tier2": 1, "tier3": 1, "unknown": 1}


def test_rate_sources_does_not_trust_lookalike_domains() -> None:
    result = TOOL_FUNCTIONS["rate_sources"](urls=[
        "https://arxiv.org.evil.com/abs/1",
        "https://notarxiv.org/abs/1",
        "https://cs.stanford.edu/paper",
    ])

    assert [item["tier"] for item in result["items"]] == ["unknown", "unknown", "tier1"]


def test_rate_sources_marks_malformed_url_invalid_without_failing_the_call() -> None:
    result = TOOL_FUNCTIONS["rate_sources"](urls=["không phải url", "ftp://arxiv.org/x", "https://arxiv.org/abs/1"])

    assert [item["tier"] for item in result["items"]] == ["invalid", "invalid", "tier1"]
    assert "error" not in result


def test_rate_sources_returns_error_for_non_list_or_non_string_items() -> None:
    assert TOOL_FUNCTIONS["rate_sources"](urls="https://arxiv.org/abs/1")["error"] == "ValueError"
    assert TOOL_FUNCTIONS["rate_sources"](urls=["https://arxiv.org/abs/1", 123])["error"] == "ValueError"
    assert TOOL_FUNCTIONS["rate_sources"](urls=["https://a.com"] * 51)["error"] == "ValueError"


# ---------------- dedupe_items ----------------

def test_dedupe_items_removes_same_url_ignoring_tracking_and_trailing_slash() -> None:
    result = TOOL_FUNCTIONS["dedupe_items"](items=[
        {"title": "A", "url": "https://www.a.com/x/?utm_source=tw&id=1"},
        {"title": "B", "url": "https://a.com/x?id=1#top"},
        {"title": "C", "url": "https://a.com/x?id=2"},
    ])

    assert [item["title"] for item in result["items"]] == ["A", "C"]
    assert result["removed"] == [{"index": 1, "reason": "same_url", "duplicate_of_index": 0, "title": "B", "url": "https://a.com/x?id=1#top"}]


def test_dedupe_items_removes_same_title_ignoring_case_accents_and_punctuation() -> None:
    result = TOOL_FUNCTIONS["dedupe_items"](items=[
        {"title": "Tin AI hôm nay!", "url": "https://b.com/1"},
        {"title": "tin ai hom nay", "url": "https://c.com/2"},
    ])

    assert result["kept_count"] == 1
    assert result["removed"][0]["reason"] == "same_title"


def test_dedupe_items_skips_non_objects_and_keeps_items_without_url_or_title() -> None:
    result = TOOL_FUNCTIONS["dedupe_items"](items=["chuỗi lạ", {"summary": "chỉ có tóm tắt"}, {"summary": "chỉ có tóm tắt"}])

    assert result["kept_count"] == 2
    assert result["removed"] == [{"index": 0, "reason": "not_an_object"}]


def test_dedupe_items_returns_error_when_items_is_not_a_list() -> None:
    assert TOOL_FUNCTIONS["dedupe_items"](items={"title": "A"})["error"] == "ValueError"


# ---------------- parse_time_range ----------------

def test_parse_time_range_today_and_yesterday_use_given_base_date() -> None:
    today = TOOL_FUNCTIONS["parse_time_range"](text="Tin hôm nay", today="2026-11-10")
    yesterday = TOOL_FUNCTIONS["parse_time_range"](text="hôm qua", today="2026-11-10")

    assert (today["start_date"], today["end_date"], today["timeframe"]) == ("2026-11-10", "2026-11-10", "day")
    assert (yesterday["start_date"], yesterday["end_date"], yesterday["timeframe"]) == ("2026-11-09", "2026-11-09", "week")


def test_parse_time_range_counted_days_and_english_phrases() -> None:
    three_days = TOOL_FUNCTIONS["parse_time_range"](text="3 ngày qua", today="2026-11-10")
    two_weeks = TOOL_FUNCTIONS["parse_time_range"](text="last 2 weeks", today="2026-11-10")

    assert (three_days["start_date"], three_days["days"], three_days["timeframe"]) == ("2026-11-08", 3, "week")
    assert (two_weeks["start_date"], two_weeks["days"], two_weeks["timeframe"]) == ("2026-10-28", 14, "month")


def test_parse_time_range_unknown_phrase_is_unrecognized_not_an_error() -> None:
    result = TOOL_FUNCTIONS["parse_time_range"](text="hello", today="2026-11-10")

    assert result["status"] == "unrecognized"
    assert "error" not in result


def test_parse_time_range_returns_error_for_bad_input_from_model() -> None:
    assert TOOL_FUNCTIONS["parse_time_range"](text="")["error"] == "ValueError"
    assert TOOL_FUNCTIONS["parse_time_range"](text="hôm nay", today="10/11/2026")["error"] == "ValueError"
    assert TOOL_FUNCTIONS["parse_time_range"](text="9999 ngày qua")["error"] == "ValueError"
