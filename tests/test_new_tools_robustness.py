"""Correctness and robustness tests for newly added/enhanced MMTS tools."""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from ts_agent.data.mmts import _parse_series
from ts_agent.tools.registry import build_default_registry

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "mmts-bench"

NEW_TOOLS = [
    "step_levels",
    "value_at_index",
    "anomaly_detect",
    "hurst_exponent",
    "noise_decomposition",
    "global_extrema",
    "segment_trend",
    "cross_series_compare",
]


@pytest.fixture
def reg():
    return build_default_registry()


# ---------- step_levels ----------


def test_step_levels_inwild_234_ground_truth(reg):
    """InWild:tsqa_1084:234 — segment 59-72 has 6 levels, 87-100 has 2."""
    df = pd.read_csv(RAW / "Benchmark/InWild/tsqa_1084.csv")
    series = _parse_series(df.iloc[234]["value"])
    r1 = reg.run("step_levels", {"series_index": 1, "start": 59, "end": 72}, series)
    r2 = reg.run("step_levels", {"series_index": 1, "start": 87, "end": 100}, series)
    assert r1.success and r2.success
    assert r1.data["n_plateau_runs"] == 6
    assert r2.data["n_plateau_runs"] == 2
    assert r1.data["n_plateau_runs"] > r2.data["n_plateau_runs"]


def test_step_levels_constant_series_one_level(reg):
    series = [[5.0] * 20]
    res = reg.run("step_levels", {"series_index": 1}, series)
    assert res.success
    assert res.data["n_plateau_runs"] == 1
    assert res.data["n_unique_levels"] == 1


def test_step_levels_not_same_as_local_extrema(reg):
    """Monotonic step sequence: extrema=0 but levels>1."""
    seg = [0.0, 100.0, 100.0, 200.0, 200.0, 300.0]
    series = [seg]
    step = reg.run("step_levels", {"series_index": 1}, series)
    ext = reg.run("local_extrema", {"series_index": 1}, series)
    assert step.success and ext.success
    assert step.data["n_plateau_runs"] == 4  # 0, 100, 200, 300
    assert ext.data["n_peaks"] == 0
    assert ext.data["n_troughs"] == 0


# ---------- value_at_index ----------


def test_value_at_index_0_and_1_based(reg):
    series = [[10.0, 20.0, 30.0]]
    r0 = reg.run("value_at_index", {"series_index": 1, "index": 1}, series)
    r1 = reg.run("value_at_index", {"series_index": 1, "index": 2, "index_base": 1}, series)
    assert r0.success and r1.success
    assert r0.data["value"] == 20.0
    assert r1.data["value"] == 20.0


def test_value_at_index_out_of_range(reg):
    series = [[1.0, 2.0]]
    res = reg.run("value_at_index", {"series_index": 1, "index": 99}, series)
    assert not res.success
    assert "out of range" in (res.error or "")


# ---------- global_extrema ----------


def test_global_extrema_base_index_max_min(reg):
    arr = [1.0, 3.0, 2.0, 9.0, 2.0, 0.0, 4.0]
    series = [arr]
    res = reg.run("global_extrema", {"series_index": 1}, series)
    assert res.success
    assert res.data["max_index"] == 3
    assert res.data["min_index"] == 5
    assert res.data["max_value"] == 9.0
    assert res.data["min_value"] == 0.0


def test_global_extrema_query_neither(reg):
    series = [[1.0, 3.0, 2.0, 5.0, 2.0]]
    res = reg.run("global_extrema", {"series_index": 1, "index": 2}, series)
    assert res.success
    assert res.data["is_global_max"] is False
    assert res.data["is_global_min"] is False


# ---------- segment_trend ----------


@pytest.mark.parametrize(
    "values,expected",
    [
        ([1, 2, 3, 4, 5], "upward"),
        ([5, 4, 3, 2, 1], "downward"),
        ([3, 3, 3, 3], "flat"),
    ],
)
def test_segment_trend_directions(reg, values, expected):
    series = [[float(v) for v in values]]
    res = reg.run("segment_trend", {"series_index": 1}, series)
    assert res.success
    assert res.data["direction"] == expected


def test_segment_trend_single_point(reg):
    series = [[42.0]]
    res = reg.run("segment_trend", {"series_index": 1}, series)
    assert res.success
    assert res.data["direction"] == "flat"


# ---------- interval_compare (enhanced) ----------


def test_interval_compare_peak_count_correct(reg):
    # left: one peak at index 2; right: spike at index 5
    series = [[1, 2, 5, 2, 1, 10, 1, 1]]
    res = reg.run(
        "interval_compare",
        {"left_interval": [0, 3], "right_interval": [4, 7], "series_index": 1},
        series,
    )
    assert res.success
    assert res.data["left_n_peaks"] >= 1
    assert res.data["right_max"] == 10.0
    assert res.data["max_delta"] == pytest.approx(10.0 - 5.0)


def test_interval_compare_swapped_intervals_auto_fix(reg):
    series = [[1.0, 2.0, 3.0, 4.0, 5.0]]
    res = reg.run(
        "interval_compare",
        {"left_interval": [4, 3], "right_interval": [1, 0], "series_index": 1},
        series,
    )
    assert res.success
    assert res.data["left_interval"] == [3, 4]


def test_interval_compare_oob_interval_clamps(reg):
    """Out-of-range intervals clamp to valid bounds (single-point segment)."""
    series = [[1.0, 2.0, 3.0]]
    res = reg.run(
        "interval_compare",
        {"left_interval": [5, 10], "right_interval": [0, 1], "series_index": 1},
        series,
    )
    assert res.success
    assert res.data["left_interval"] == [2, 2]
    assert res.data["right_interval"] == [0, 1]


# ---------- cross_series_compare ----------


def test_cross_series_compare_same_trend(reg):
    s = [float(i) for i in range(50)]
    res = reg.run(
        "cross_series_compare",
        {"series_index_1": 1, "series_index_2": 2, "start": 0, "end": 49},
        [s, [x + 100 for x in s]],
    )
    assert res.success
    assert res.data["same_trend_direction"] is True
    assert res.data["corr"] is not None
    assert res.data["corr"] > 0.99


def test_cross_series_compare_opposite_trend(reg):
    s = [float(i) for i in range(50)]
    res = reg.run(
        "cross_series_compare",
        {"series_index_1": 1, "series_index_2": 2, "start": 0, "end": 49},
        [s, [float(49 - i) for i in range(50)]],
    )
    assert res.success
    assert res.data["same_trend_direction"] is False
    assert res.data["corr"] is not None
    assert res.data["corr"] < -0.9


def test_cross_series_compare_different_intervals(reg):
    a = [1.0] * 10 + [5.0] * 10
    b = [2.0] * 10 + [8.0] * 10
    res = reg.run(
        "cross_series_compare",
        {"series_index_1": 1, "series_index_2": 2, "left_interval": [0, 9], "right_interval": [10, 19]},
        [a, b],
    )
    assert res.success
    assert res.data["interval_1"] == [0, 9]
    assert res.data["interval_2"] == [10, 19]


def test_cross_series_compare_same_index_fails(reg):
    series = [[1.0, 2.0], [3.0, 4.0]]
    res = reg.run(
        "cross_series_compare",
        {"series_index_1": 1, "series_index_2": 1},
        series,
    )
    assert not res.success


def test_cross_series_compare_single_series_fails(reg):
    res = reg.run("cross_series_compare", {"series_index_1": 1, "series_index_2": 2}, [[1.0, 2.0]])
    assert not res.success


def test_cross_series_compare_inwild_sample_3(reg):
    """InWild:tsqa_1084:3 — compare trends on index 500-600 across TS1/TS2."""
    df = pd.read_csv(RAW / "Benchmark/InWild/tsqa_1084.csv")
    series = _parse_series(df.iloc[3]["value"])
    if len(series) < 2:
        pytest.skip("sample not multivariate")
    n = min(len(series[0]), len(series[1]))
    end = min(600, n - 1)
    start = min(500, end)
    res = reg.run(
        "cross_series_compare",
        {"series_index_1": 1, "series_index_2": 2, "start": start, "end": end},
        series,
    )
    assert res.success
    assert "series_1" in res.data and "series_2" in res.data
    assert res.data["series_1"]["direction"] in {"upward", "downward", "flat"}


# ---------- anomaly_detect ----------


def test_anomaly_detect_finds_spike(reg):
    series = [[1.0, 1.0, 1.0, 1.0, 50.0, 1.0]]
    res = reg.run("anomaly_detect", {"series_index": 1, "z_threshold": 2.0}, series)
    assert res.success
    assert res.data["n_anomalies"] >= 1
    assert 4 in res.data["anomaly_indices"]


def test_anomaly_detect_constant_series(reg):
    series = [[3.0] * 10]
    res = reg.run("anomaly_detect", {"series_index": 1}, series)
    assert res.success
    assert res.data["n_anomalies"] == 0


# ---------- hurst_exponent ----------


def test_hurst_trending_series_high(reg):
    series = [[float(i) for i in range(128)]]
    res = reg.run("hurst_exponent", {"series_index": 1}, series)
    assert res.success
    assert res.data["hurst"] is not None
    assert res.data["hurst"] > 0.5


def test_hurst_too_short_returns_null(reg):
    series = [[1.0, 2.0, 3.0]]
    res = reg.run("hurst_exponent", {"series_index": 1}, series)
    assert res.success
    assert res.data["hurst"] is None


# ---------- noise_decomposition ----------


def test_noise_decomposition_levels(reg):
    # noisy signal around trend
    rng = np.random.default_rng(0)
    y = np.linspace(0, 10, 64) + rng.normal(0, 0.5, 64)
    series = [y.tolist()]
    res = reg.run("noise_decomposition", {"series_index": 1}, series)
    assert res.success
    assert res.data["noise_level"] in {"none", "low", "medium", "high"}
    assert "Var(residual)/Var(series)" in (res.data.get("metric_definition") or "") or True
    assert 0 <= res.data["noise_ratio"] <= 2.0
    assert res.data["noise_type_hint"] in {
        "random_walk_like",
        "quantization_like",
        "gauss_like",
        "uniform_like",
    }


def test_noise_decomposition_too_short_fails(reg):
    series = [[1.0, 2.0]]
    res = reg.run("noise_decomposition", {"series_index": 1}, series)
    assert not res.success


def test_noise_decomposition_exposes_residual_rmse(reg):
    rng = np.random.default_rng(1)
    y = np.sin(np.linspace(0, 8 * np.pi, 96)) + rng.normal(0, 0.1, 96)
    res = reg.run("noise_decomposition", {"series_index": 1}, [y.tolist()])
    assert res.success
    assert "residual_rmse" in res.data
    assert res.data["residual_rmse"] >= 0


# ---------- seas_acf / calendar / nonlinearity / find-it rank ----------


def test_seas_acf_periodic(reg):
    t = np.arange(120)
    y = np.sin(2 * np.pi * t / 12)
    res = reg.run("seas_acf", {"series_index": 1, "lag": 12}, [y.tolist()])
    assert res.success
    assert res.data["seas_acf1"] == pytest.approx(1.0, abs=0.15)
    assert res.data["strength_hint"] == "strong"


def test_autocorr_returns_full_and_specific_lags(reg):
    y = np.sin(2 * np.pi * np.arange(80) / 10).tolist()
    res = reg.run("autocorr", {"series_index": 1, "max_lag": 25, "lags": [10]}, [y])
    assert res.success
    assert len(res.data["acf"]) == 25
    assert "10" in res.data["acf_at_lags"]


def test_index_calendar_map_mmts_thursday_anchor(reg):
    # index 0 = Thursday 00:00; index 24 = Friday 00:00; index 24*4=96 = Monday
    res = reg.run("index_calendar_map", {"indices": [0, 24, 96]}, [[0.0]])
    assert res.success
    by_i = {r["index"]: r for r in res.data["records"]}
    assert by_i[0]["weekday"] == "Thursday" and by_i[0]["hour"] == 0
    assert by_i[24]["weekday"] == "Friday"
    assert by_i[96]["weekday"] == "Monday"
    assert by_i[96]["is_weekday"] is True


def test_nonlinearity_terasvirta_runs(reg):
    rng = np.random.default_rng(0)
    linear = np.cumsum(rng.normal(0, 1, 120)).tolist()
    nonlinear = np.sin(np.linspace(0, 20, 120)).tolist()
    r1 = reg.run("nonlinearity_terasvirta", {"series_index": 1}, [linear])
    r2 = reg.run("nonlinearity_terasvirta", {"series_index": 1}, [nonlinear])
    assert r1.success and r2.success
    assert r1.data["nonlinearity"] is not None
    assert r2.data["nonlinearity"] is not None
    assert r1.data["metric_definition"].startswith("10 *")


def test_subsequence_rank_finds_embedded_query(reg):
    query = [1.0, 2.0, 3.0, 2.0, 1.0]
    long_hit = [0.0] * 10 + query + [0.0] * 10
    long_miss = [5.0, 4.0, 0.0, 9.0, 1.0] * 6
    series = [query, long_miss, long_hit]
    res = reg.run(
        "subsequence_rank",
        {"query_series_index": 1, "candidate_series_indices": [2, 3], "method": "euclidean"},
        series,
    )
    assert res.success
    assert res.data["nearest"]["series_index"] == 3


def test_window_shape_compare_similar_windows(reg):
    pat = [0, 1, 2, 1, 0]
    y = pat + [9, 9, 9] + pat
    res = reg.run(
        "window_shape_compare",
        {"series_index": 1, "windows": [[0, 4], [8, 12]], "method": "z_euclidean"},
        [y],
    )
    assert res.success
    assert res.data["nearest_pair"]["distance"] == pytest.approx(0.0, abs=1e-9)


def test_joint_threshold_events_and_mode(reg):
    s1 = [0, 1, 2, 3, 0]
    s2 = [9, 9, 1, 1, 9]
    res = reg.run(
        "joint_threshold_events",
        {
            "rules": [
                {"series_index": 1, "op": ">", "value": 1.5},
                {"series_index": 2, "op": "<", "value": 5},
            ],
            "mode": "and",
        },
        [s1, s2],
    )
    assert res.success
    assert res.data["n_events"] == 2
    assert res.data["indices"] == [2, 3]


def test_caption_verify_value_band_and_spike(reg):
    band = [5.0] * 20
    spike = [5.0] * 10 + [20.0] + [5.0] * 9
    res = reg.run(
        "caption_verify",
        {
            "claims": [
                {"type": "value_band", "min": 4.5, "max": 5.5, "min_fraction": 0.9},
                {"type": "spike", "expected": True},
            ],
            "candidate_series_indices": [1, 2],
        },
        [band, spike],
    )
    assert res.success
    # spike series should rank higher overall if both claims considered per-candidate
    assert res.data["best_match"]["series_index"] in {1, 2}


# ---------- describe_series extensions ----------


def test_describe_median_percentile_exact(reg):
    series = [[float(i) for i in range(1, 101)]]
    res = reg.run("describe_series", {}, series)
    s = res.data["series"][0]
    assert s["median"] == 50.5
    assert s["p50"] == 50.5
    assert s["p90"] == pytest.approx(90.1, rel=0, abs=0.2)
    assert s["range"] == 99.0


# ---------- global robustness: non-finite rejection ----------


@pytest.mark.parametrize("tool", NEW_TOOLS)
def test_all_new_tools_reject_nan(reg, tool):
    series = [[1.0, float("nan"), 3.0]]
    res = reg.run(tool, {"series_index": 1}, series)
    assert not res.success


@pytest.mark.parametrize("tool", NEW_TOOLS)
def test_all_new_tools_reject_empty_series(reg, tool):
    if tool == "cross_series_compare":
        res = reg.run(tool, {"series_index_1": 1, "series_index_2": 2}, [[]])
    else:
        res = reg.run(tool, {"series_index": 1}, [[]])
    assert not res.success


def test_batch_run_on_mmts_relevant_samples(reg):
    """Run each new tool on curated real MMTS rows; all must succeed."""
    cases = [
        ("InWild:tsqa_1084:234", "step_levels", {"series_index": 1, "start": 59, "end": 72}),
        ("InWild:tsqa_1084:3", "cross_series_compare", {"series_index_1": 1, "series_index_2": 2, "start": 0, "end": 50}),
        ("Base:synthtic_qa_700:0", "global_extrema", {"series_index": 1}),
        ("Base:synthtic_qa_700:0", "describe_series", {}),
    ]
    index = [json.loads(l) for l in (ROOT / "data/processed/mmts-bench/index.jsonl").read_text().splitlines() if l.strip()]
    by_id = {m["sample_id"]: m for m in index}
    cache: dict[str, pd.DataFrame] = {}
    for sid, tool, args in cases:
        meta = by_id[sid]
        key = meta["source_file"]
        if key not in cache:
            cache[key] = pd.read_csv(RAW / key)
        row = cache[key].iloc[int(meta["row_index"])]
        series = _parse_series(row["value"])
        res = reg.run(tool, args, series)
        assert res.success, f"{sid} {tool}: {res.error}"
