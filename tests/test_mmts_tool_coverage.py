"""MMTS-driven tool coverage audit and robustness checks on real samples."""
from __future__ import annotations

import ast
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

import pandas as pd
import pytest

from ts_agent.data.mmts import _parse_series
from ts_agent.tools.registry import build_default_registry

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "mmts-bench"
INDEX = ROOT / "data" / "processed" / "mmts-bench" / "index.jsonl"

TASK_TOOLS = {
    "basic analysis": ["describe_series"],
    "trend analysis": ["describe_series", "segment_trend", "hurst_exponent"],
    "seasonality analysis": ["fft_period", "stl_strength", "autocorr"],
    "noise analysis": ["noise_decomposition", "sliding_stats"],
    "volatility analysis": ["sliding_stats", "diff_stats"],
    "stationarity": ["adf_stationarity"],
    "index": ["global_extrema", "value_at_index", "segment_trend", "local_extrema"],
    "deductive reasoning": ["interval_compare", "step_levels", "segment_trend"],
    "inductive reasoning": ["interval_compare", "segment_trend", "change_points"],
    "causal reasoning": ["lag_corr", "interval_compare"],
    "analogical reasoning": ["cross_series_compare", "interval_compare", "segment_trend"],
    "counterfactual reasoning": ["interval_compare", "lag_corr", "segment_trend"],
    "choose it": ["pairwise_distance"],
    "find it": ["subsequence_locate"],
    "reverse it": ["smooth_reverse_stats"],
    "smooth it": ["smooth_reverse_stats", "pairwise_distance"],
    "caption": [
        "describe_series",
        "step_levels",
        "local_extrema",
        "fft_period",
        "stl_strength",
        "segment_trend",
        "noise_decomposition",
        "anomaly_detect",
    ],
}

KW_TOOLS = [
    (r"\b(step|plateau|stepwise|step level)\b", ["step_levels"]),
    (r"\b(hurst|persisten)\b", ["hurst_exponent"]),
    (r"\b(anomaly|outlier|spike)\b", ["anomaly_detect"]),
    (r"\b(value at index|at index \d+)\b", ["value_at_index", "global_extrema"]),
    (r"\b(global max|global min)\b", ["global_extrema"]),
]


def _load_index():
    return [json.loads(l) for l in INDEX.read_text().splitlines() if l.strip()]


def _parse_tasks(row) -> list[str]:
    tt = row.get("task_type")
    try:
        items = ast.literal_eval(str(tt)) if isinstance(tt, str) else tt
        return [str(x).strip().lower() for x in items]
    except Exception:
        return [str(tt).strip().lower()]


def _route_agents(meta, tasks):
    subset = meta["subset"]
    if subset == "Base":
        return ["short", "medium", "long"], ["structure"]
    if subset == "Match":
        return ["short"], ["matching"]
    if subset == "Align":
        return ["short", "medium"], ["alignment"]
    homo = (
        ["short", "medium"]
        if meta.get("local_overall") == "local"
        else ["short", "medium", "long"]
    )
    if any(
        k in t
        for t in tasks
        for k in ("causal", "deductive", "inductive", "analog", "counterfactual")
    ):
        return homo, ["reasoning", "structure"]
    return homo, ["structure"]


HOMO_EXTRA = {
    "Base": ["describe_series", "segment_trend", "fft_period", "stl_strength", "autocorr", "adf_stationarity", "noise_decomposition", "hurst_exponent", "global_extrema"],
    "InWild": ["describe_series", "interval_compare", "segment_trend", "step_levels", "local_extrema", "cross_series_compare", "lag_corr"],
    "Align": ["describe_series", "step_levels", "local_extrema", "fft_period", "stl_strength", "segment_trend"],
    "Match": ["describe_series", "local_extrema", "diff_stats", "sliding_stats"],
}

HETERO_TASK_TOOLS = TASK_TOOLS


def _needed_for_homo(meta, row) -> set[str]:
    tools = set(HOMO_EXTRA.get(meta["subset"], ["describe_series"]))
    q = str(row["question"]).lower()
    for pat, ts in KW_TOOLS:
        if re.search(pat, q, re.I):
            tools.update(ts)
    if meta.get("local_overall") == "local" or "index" in q:
        tools.update(["interval_compare", "segment_trend", "value_at_index", "global_extrema"])
    tasks = _parse_tasks(row)
    if any("analog" in t for t in tasks) and len(_parse_series(row["value"])) >= 2:
        tools.add("cross_series_compare")
    if any("causal" in t for t in tasks):
        tools.add("lag_corr")
    return tools


def _needed_for_hetero(role: str, meta, row) -> set[str]:
    tools: set[str] = set()
    for t in _parse_tasks(row):
        tools.update(HETERO_TASK_TOOLS.get(t, ["describe_series"]))
    q = str(row["question"]).lower()
    for pat, ts in KW_TOOLS:
        if re.search(pat, q, re.I):
            tools.update(ts)
    if role == "alignment" or meta["subset"] == "Align":
        tools.update(HETERO_TASK_TOOLS["caption"])
    if role == "matching" or meta["subset"] == "Match":
        for t in _parse_tasks(row):
            tools.update(HETERO_TASK_TOOLS.get(t, ["pairwise_distance"]))
    return tools


def audit_gaps():
    reg = build_default_registry()
    role_tools = {
        r: {s.name for s in reg.list_for_roles([r])}
        for r in ["short", "medium", "long", "structure", "reasoning", "matching", "alignment"]
    }
    cache: dict[str, pd.DataFrame] = {}
    gaps: dict[str, Counter] = defaultdict(Counter)

    for meta in _load_index():
        key = meta["source_file"]
        if key not in cache:
            cache[key] = pd.read_csv(RAW / key)
        row = cache[key].iloc[int(meta["row_index"])]
        homo, hetero = _route_agents(meta, _parse_tasks(row))
        homo_need = _needed_for_homo(meta, row)
        for role in homo:
            for t in homo_need:
                if t not in role_tools[role]:
                    gaps[role][t] += 1
        for role in hetero:
            need = _needed_for_hetero(role, meta, row)
            for t in need:
                if t not in role_tools[role]:
                    gaps[role][t] += 1
    return gaps


def test_mmts_role_tool_coverage_has_no_gaps():
    gaps = audit_gaps()
    assert not gaps, f"MMTS tool gaps remain: { {k: dict(v) for k, v in gaps.items()} }"


@pytest.fixture
def reg():
    return build_default_registry()


def test_cross_series_compare_analogical():
    reg = build_default_registry()
    s1 = [float(i) for i in range(600, 700)]
    s2 = [float(700 - i) for i in range(100)]
    res = reg.run(
        "cross_series_compare",
        {"series_index_1": 1, "series_index_2": 2, "start": 0, "end": 99},
        [s1, s2],
    )
    assert res.success
    assert res.data["series_1"]["direction"] == "upward"
    assert res.data["series_2"]["direction"] == "downward"
    assert res.data["same_trend_direction"] is False


def test_interval_compare_includes_peak_stats():
    reg = build_default_registry()
    series = [[1, 2, 5, 2, 1, 10, 3, 1]]
    res = reg.run(
        "interval_compare",
        {"left_interval": [0, 3], "right_interval": [4, 7], "series_index": 1},
        series,
    )
    assert res.success
    assert "left_n_peaks" in res.data
    assert "right_max" in res.data
    assert res.data["right_max"] == 10.0


def test_global_extrema_index_classification():
    reg = build_default_registry()
    series = [[1, 3, 2, 5, 2, 1, 4, 1]]
    res = reg.run("global_extrema", {"series_index": 1, "index": 3}, series)
    assert res.success
    assert res.data["is_global_max"] is True
    assert res.data["max_index"] == 3


def test_segment_trend_direction():
    reg = build_default_registry()
    series = [[1.0, 2.0, 3.0, 4.0, 5.0]]
    res = reg.run("segment_trend", {"series_index": 1}, series)
    assert res.success
    assert res.data["direction"] == "upward"


def test_robustness_on_real_mmts_samples(reg):
    """Smoke-run primary tools on one sample per subset/task bucket."""
    cache: dict[str, pd.DataFrame] = {}
    seen: set[str] = set()
    for meta in _load_index():
        key = meta["source_file"]
        if key not in cache:
            cache[key] = pd.read_csv(RAW / key)
        row = cache[key].iloc[int(meta["row_index"])]
        bucket = f"{meta['subset']}:{_parse_tasks(row)[0]}"
        if bucket in seen:
            continue
        seen.add(bucket)
        series = _parse_series(row["value"])
        homo, hetero = _route_agents(meta, _parse_tasks(row))
        role = hetero[0]
        tools = {s.name for s in reg.list_for_roles([role])}
        # run a minimal tool subset per bucket
        if "describe_series" in tools:
            assert reg.run("describe_series", {}, series).success, bucket
        if "step_levels" in tools and len(series[0]) > 5:
            assert reg.run("step_levels", {"series_index": 1, "start": 0, "end": 4}, series).success, bucket
        if "cross_series_compare" in tools and len(series) >= 2:
            n = min(len(series[0]), len(series[1]))
            assert reg.run(
                "cross_series_compare",
                {"series_index_1": 1, "series_index_2": 2, "start": 0, "end": max(1, n - 1)},
                series,
            ).success, bucket
        if len(seen) >= 20:
            break
    assert len(seen) >= 10
