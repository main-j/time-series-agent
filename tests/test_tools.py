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
