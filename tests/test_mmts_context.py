"""Unit tests for MMTS structured context helpers."""
from __future__ import annotations

from ts_agent.data.mmts import (
    extract_focus_intervals,
    format_raw_value_text,
    infer_series_roles,
)
from ts_agent.schemas.models import SubsetName


def test_format_raw_value_text_returns_truncation_flag():
    short = [[1.0, 2.0], [3.0, 4.0]]
    text, truncated = format_raw_value_text(short, max_chars=None)
    assert truncated is False
    assert "Given Time Series 1" in text

    long_uni = list(range(100))
    text2, truncated2 = format_raw_value_text(long_uni, max_chars=80)
    assert truncated2 is True
    assert "[truncated]" in text2


def test_infer_series_roles_match():
    roles = infer_series_roles(SubsetName.MATCH, "Benchmark/Match/qats_400.csv", 5)
    assert roles["query_series_index"] == 1
    assert roles["candidate_series_indices"] == [2, 3, 4, 5]
    assert roles["option_to_series"] == {"A": 2, "B": 3, "C": 4, "D": 5}
    assert roles["align_direction"] is None


def test_infer_series_roles_align_directions():
    ts2c = infer_series_roles(SubsetName.ALIGN, "Benchmark/Align/ts2caption_qa_120.csv", 1)
    assert ts2c["align_direction"] == "ts2caption"
    assert ts2c["query_series_index"] == 1

    c2ts = infer_series_roles(SubsetName.ALIGN, "Benchmark/Align/caption2ts_qa_120.csv", 4)
    assert c2ts["align_direction"] == "caption2ts"
    assert c2ts["query_series_index"] is None
    assert c2ts["option_to_series"]["A"] == 1


def test_extract_focus_intervals():
    q = "Compare the segment from index 10 to index 20 with indices 30-40."
    intervals = extract_focus_intervals(q)
    assert [10, 20] in intervals
    assert [30, 40] in intervals
