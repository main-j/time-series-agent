from ts_agent.tools.registry import build_default_registry
from ts_agent.data.mmts import format_series_text, _parse_series


def test_tools_describe():
    reg = build_default_registry()
    series = [[1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0]]
    res = reg.run("describe_series", {}, series)
    assert res.success
    assert res.data["series"][0]["length"] == 8


def test_parse_series_univariate_and_multi():
    assert _parse_series("[1,2,3]") == [[1.0, 2.0, 3.0]]
    assert _parse_series("[[1,2],[3,4]]") == [[1.0, 2.0], [3.0, 4.0]]
    text = format_series_text([[1, 2, 3]])
    assert "Given Time Series 1" in text


def test_pairwise_distance():
    reg = build_default_registry()
    series = [
        [0, 1, 2, 3, 4, 5],
        [0, 1, 2, 3, 4, 6],
        [10, 10, 10, 10, 10, 10],
    ]
    res = reg.run("pairwise_distance", {"method": "euclidean"}, series)
    assert res.success
    assert res.data["nearest"]["series_index"] == 2


def test_reject_nonfinite_and_empty():
    reg = build_default_registry()
    assert not reg.run("describe_series", {}, []).success
    assert not reg.run("describe_series", {}, [[]]).success
    assert not reg.run("sliding_stats", {}, [[1.0, float("nan"), 3.0]]).success
    assert not reg.run("fft_period", {}, [[1.0, float("inf"), 3.0]]).success


def test_lag_corr_zero_variance():
    reg = build_default_registry()
    res = reg.run("lag_corr", {"lag": 1}, [[5.0] * 20])
    assert not res.success
    assert "zero-variance" in (res.error or "")


def test_multi_series_fanout_and_select():
    reg = build_default_registry()
    series = [
        [1, 3, 2, 5, 4, 6, 3, 7],
        [10, 11, 12, 13, 14, 15, 16, 17],
        [5, 4, 3, 2, 1, 0, -1, -2],
    ]
    res = reg.run("local_extrema", {}, series)
    assert res.success
    assert res.data["n_series"] == 3
    assert {x["series_index"] for x in res.data["series"]} == {1, 2, 3}

    res2 = reg.run("local_extrema", {"series_index": 2}, series)
    assert res2.success
    assert res2.data["series_index"] == 2
    assert res2.data["n_troughs"] == 0

    res3 = reg.run("diff_stats", {"series": "Time Series 3"}, series)
    assert res3.success
    assert res3.data["series_index"] == 3
    assert res3.data["mean_diff"] < 0


def test_reject_raw_series_array_in_arguments():
    reg = build_default_registry()
    series = [
        [1.0, 2.0, 3.0, 4.0, 5.0, 6.0],
        [9.0, 8.0, 7.0, 6.0, 5.0, 4.0],
    ]
    raw = list(series[1])
    res = reg.run("sliding_stats", {"series": raw, "window_size": 3}, series)
    assert not res.success
    assert "Do not pass raw series values" in (res.error or "")


def test_window_alias_and_interval_pair():
    reg = build_default_registry()
    series = [[1, 2, 3, 4, 10, 11, 12, 13]]
    res = reg.run("sliding_stats", {"window_size": 3, "series_index": 1}, series)
    assert res.success
    assert res.data["window"] == 3

    res2 = reg.run(
        "interval_compare",
        {"left_interval": [0, 3], "right_interval": [4, 7], "series_index": 1},
        series,
    )
    assert res2.success
    assert res2.data["mode"] == "pair"
    assert res2.data["mean_delta"] > 0


def test_lag_corr_all_pairs():
    reg = build_default_registry()
    series = [
        [1.0, 2.0, 3.0, 4.0, 5.0, 6.0],
        [6.0, 5.0, 4.0, 3.0, 2.0, 1.0],
        [1.0, 1.5, 2.0, 2.5, 3.0, 3.5],
    ]
    res = reg.run(
        "lag_corr",
        {"lag": 0, "series_index_1": "all", "series_index_2": "all"},
        series,
    )
    assert res.success
    assert res.data["mode"] == "cross_all"
    assert len(res.data["pairs"]) == 3
    # series1 vs series2 should be strongly negative
    pair12 = next(p for p in res.data["pairs"] if p["series_index_1"] == 1 and p["series_index_2"] == 2)
    assert pair12["corr"] < -0.9


def test_local_extrema_allowed_for_reasoning():
    reg = build_default_registry()
    specs = {s.name: s for s in reg.list_for_roles(["reasoning"])}
    assert "local_extrema" in specs
    assert "lag_corr" in specs


def test_describe_includes_median_and_percentiles():
    reg = build_default_registry()
    series = [[float(i) for i in range(1, 101)]]
    res = reg.run("describe_series", {}, series)
    assert res.success
    s = res.data["series"][0]
    assert "median" in s and "p90" in s and "range" in s
    assert s["median"] == 50.5


def test_step_levels_on_staircase():
    reg = build_default_registry()
    # mimic InWild :234 segment 59-72 pattern
    seg = [0.0] + [100.0] * 5 + [200.0] + [400.0] * 3 + [600.0] * 2 + [700.0]
    series = [seg]
    res = reg.run("step_levels", {"series_index": 1, "start": 0, "end": len(seg) - 1}, series)
    assert res.success
    assert res.data["n_plateau_runs"] == 6
    assert res.data["n_unique_levels"] == 6

    seg2 = [800.0] * 3 + [1200.0] * 11
    full = seg + seg2
    start2 = len(seg)
    res2 = reg.run(
        "step_levels",
        {"series_index": 1, "start": start2, "end": len(full) - 1},
        [full],
    )
    assert res2.success
    assert res2.data["n_plateau_runs"] == 2


def test_value_at_index():
    reg = build_default_registry()
    series = [[10.0, 20.0, 30.0]]
    res = reg.run("value_at_index", {"series_index": 1, "index": 1}, series)
    assert res.success
    assert res.data["value"] == 20.0


def test_anomaly_detect_finds_spike():
    reg = build_default_registry()
    series = [[1.0, 1.0, 1.0, 1.0, 50.0, 1.0]]
    res = reg.run("anomaly_detect", {"series_index": 1, "z_threshold": 2.0}, series)
    assert res.success
    assert res.data["n_anomalies"] >= 1


def test_hurst_and_noise_decomposition_smoke():
    reg = build_default_registry()
    series = [[float(i) + 0.1 * (i % 7) for i in range(64)]]
    h = reg.run("hurst_exponent", {"series_index": 1}, series)
    assert h.success
    assert h.data["hurst"] is not None
    n = reg.run("noise_decomposition", {"series_index": 1}, series)
    assert n.success
    assert "noise_ratio" in n.data
    assert n.data["noise_level"] in {"none", "low", "medium", "high"}
    assert "Var(residual)/Var(series)" in n.data["metric_definition"]


def test_waveform_features_registered_for_core_roles():
    reg = build_default_registry()
    names = {s.name for s in reg.list_for_roles(["short", "structure"])}
    assert "waveform_features" in names


def test_fft_period_marks_near_length_untrusted():
    reg = build_default_registry()
    # Nearly monotonic: FFT often picks period ≈ length.
    y = [float(i) + 0.01 * (i % 3) for i in range(64)]
    res = reg.run("fft_period", {"series_index": 1}, [y])
    assert res.success
    assert "period_trusted" in res.data
    if res.data.get("dominant_period") and float(res.data["dominant_period"]) >= 0.5 * 64:
        assert res.data["period_trusted"] is False
        assert any("length" in w for w in (res.data.get("warnings") or []))


def test_alignment_role_has_new_tools():
    reg = build_default_registry()
    names = {s.name for s in reg.list_for_roles(["alignment"])}
    for tool in ["step_levels", "local_extrema", "fft_period", "stl_strength", "anomaly_detect"]:
        assert tool in names


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


def test_cross_series_compare_smoke():
    reg = build_default_registry()
    res = reg.run(
        "cross_series_compare",
        {"series_index_1": 1, "series_index_2": 2, "start": 0, "end": 9},
        [[float(i) for i in range(10)], [float(9 - i) for i in range(10)]],
    )
    assert res.success
    assert "same_trend_direction" in res.data


def test_global_extrema_and_segment_trend_registered_for_short():
    reg = build_default_registry()
    names = {s.name for s in reg.list_for_roles(["short"])}
    assert "global_extrema" in names
    assert "segment_trend" in names
    assert "cross_series_compare" in names


def test_catalog_mentions_series_index():
    reg = build_default_registry()
    text = reg.catalog_text(["short"])
    assert "series_index" in text
    assert "NEVER paste raw numeric arrays" in text
    assert "lag_corr is pairwise" in text
