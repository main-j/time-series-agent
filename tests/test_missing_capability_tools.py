"""Tests for tools added to close the MMTS capability gaps."""
from __future__ import annotations

import numpy as np
import pytest

from ts_agent.tools.registry import build_default_registry


@pytest.fixture
def reg():
    return build_default_registry()


NEW_TOOLS = {
    "crossing_points",
    "advanced_features",
    "counterfactual_simulate",
    "extrema_align",
    "lag_corr_scan",
    "reverse_match",
    "robust_shape_match",
    "caption_verify",
}


def test_all_missing_capability_tools_are_registered(reg):
    assert NEW_TOOLS.issubset(reg._specs)


def test_crossing_points_returns_exact_indices(reg):
    result = reg.run("crossing_points", {"threshold_value": 1.0}, [[0.0, 2.0, 0.0, 2.0]])
    assert result.success
    assert result.data["n_crossings"] == 3
    assert result.data["crossing_indices"] == [1, 2, 3]


def test_crossing_points_local_count_uses_whole_series_median_by_default(reg):
    values = [0.0, 0.0, 0.0, 10.0, 11.0, 12.0, 13.0]
    whole = reg.run("crossing_points", {"start": 3, "end": 6}, [values])
    window = reg.run(
        "crossing_points",
        {"start": 3, "end": 6, "threshold_scope": "window"},
        [values],
    )
    assert whole.success and window.success
    assert whole.data["threshold"] == 10.0
    assert whole.data["n_crossings"] == 1
    assert window.data["threshold"] == 11.5
    assert window.data["n_crossings"] == 1
    assert whole.data["threshold_scope"] == "series"


def test_crossing_points_rejects_invalid_mode_and_scope(reg):
    assert not reg.run("crossing_points", {"threshold_mode": "medain"}, [[1.0, 2.0]]).success
    assert not reg.run("crossing_points", {"threshold_scope": "local"}, [[1.0, 2.0]]).success


def test_advanced_features_cover_distribution_and_variance(reg):
    values = [0.0] * 20 + [1.0, 3.0, 8.0, 20.0] * 10
    result = reg.run("advanced_features", {"arch_lags": 3, "chunk_size": 10}, [values])
    assert result.success
    assert result.data["iqr"] >= 0
    assert result.data["skewness"] > 0
    assert 0 <= result.data["normalized_entropy"] <= 1
    assert result.data["n_chunks"] >= 2
    assert result.data["arch_lm_stat"] is not None
    assert 0 <= result.data["arch_lm_r2"] <= 1
    assert result.data["entropy_definition"] == "normalized non-DC power spectral entropy"


def test_advanced_features_spectral_entropy_distinguishes_sine_from_noise(reg):
    rng = np.random.default_rng(1)
    x = np.arange(256)
    sine = np.sin(2 * np.pi * x / 16)
    noise = rng.normal(size=256)
    periodic = reg.run("advanced_features", {}, [sine.tolist()])
    random = reg.run("advanced_features", {}, [noise.tolist()])
    assert periodic.success and random.success
    assert periodic.data["normalized_spectral_entropy"] < 0.1
    assert random.data["normalized_spectral_entropy"] > 0.8


def test_advanced_features_arch_exposes_r2_and_lm_identity(reg):
    rng = np.random.default_rng(2)
    values = rng.normal(size=100)
    result = reg.run("advanced_features", {"arch_lags": 5}, [values.tolist()])
    assert result.success
    expected_lm = (len(values) - result.data["arch_lags"]) * result.data["arch_lm_r2"]
    assert result.data["arch_lm_stat"] == pytest.approx(expected_lm)


def test_counterfactual_simulate_does_not_mutate_bound_series(reg):
    source = [[1.0, 2.0, 3.0, 4.0]]
    result = reg.run(
        "counterfactual_simulate",
        {
            "series_index": 1,
            "operations": [
                {"op": "set_value", "index": 2, "value": 20.0},
                {"op": "shift", "start": 0, "end": 1, "amount": 2.0},
            ],
        },
        source,
    )
    assert result.success
    assert result.data["after"]["max"] == 20.0
    assert result.data["after"]["mean"] > result.data["before"]["mean"]
    assert result.data["n_changed"] == 3
    assert source == [[1.0, 2.0, 3.0, 4.0]]


def test_counterfactual_replace_segment_resamples_source(reg):
    result = reg.run(
        "counterfactual_simulate",
        {
            "series_index": 1,
            "operations": [
                {
                    "op": "replace_segment",
                    "start": 1,
                    "end": 3,
                    "source_series_index": 2,
                    "source_start": 0,
                    "source_end": 1,
                }
            ],
        },
        [[0.0] * 5, [10.0, 20.0]],
    )
    assert result.success
    assert result.data["n_changed"] == 3
    assert result.data["after"]["max"] == 20.0


def test_counterfactual_one_based_default_interval_includes_last_point(reg):
    result = reg.run(
        "counterfactual_simulate",
        {"index_base": 1, "operations": [{"op": "shift", "amount": 10.0}]},
        [[1.0, 2.0, 3.0, 4.0]],
    )
    assert result.success
    assert result.data["n_changed"] == 4
    assert result.data["after"]["end_value"] == 14.0


def test_counterfactual_counts_only_actual_changes(reg):
    result = reg.run(
        "counterfactual_simulate",
        {"operations": [{"op": "shift", "amount": 0.0}]},
        [[1.0, 2.0, 3.0]],
    )
    assert result.success
    assert result.data["n_changed"] == 0
    assert result.data["changed_preview"] == []


def test_counterfactual_rejects_oob_and_reports_exact_indices(reg):
    bad = reg.run(
        "counterfactual_simulate",
        {"operations": [{"op": "shift", "start": 99, "end": 100, "amount": 1}]},
        [[1.0, 2.0, 3.0]],
    )
    good = reg.run(
        "counterfactual_simulate",
        {
            "operations": [{"op": "set_value", "index": 2, "value": 9.0}],
            "report_indices": [2],
        },
        [[1.0, 2.0, 3.0]],
    )
    assert not bad.success
    assert good.success
    assert good.data["reported_values"] == [{"index": 2, "before": 3.0, "after": 9.0}]


def test_extrema_align_identical_events(reg):
    wave = [0.0, 2.0, 0.0, 2.0, 0.0]
    result = reg.run(
        "extrema_align",
        {"series_index_1": 1, "series_index_2": 2, "kind": "peaks", "max_lag": 2},
        [wave, wave],
    )
    assert result.success
    assert result.data["events_1"] == result.data["events_2"]
    assert result.data["mean_abs_normalized_position_delta"] == 0.0
    assert result.data["best_event_lag"] == 0


def test_extrema_align_penalizes_events_discarded_by_lag(reg):
    result = reg.run(
        "extrema_align",
        {"kind": "peaks", "max_lag": 4},
        [[0, 2, 0, 2, 0, 2, 0], [0, 0, 0, 0, 0, 2, 0]],
    )
    assert result.success
    assert result.data["best_event_jaccard"] == pytest.approx(1 / 3)
    assert result.data["best_event_match_coverage"] == pytest.approx(1 / 3)


def test_extrema_align_no_events_reports_insufficient(reg):
    result = reg.run("extrema_align", {}, [[1.0] * 10, [2.0] * 10])
    assert result.success
    assert result.data["best_event_lag"] is None
    assert result.data["best_event_jaccard"] is None
    assert result.data["alignment_status"] == "insufficient_extrema"


def test_lag_corr_scan_finds_delayed_second_series(reg):
    rng = np.random.default_rng(42)
    first = rng.normal(size=80)
    second = np.r_[np.zeros(3), first[:-3]]
    result = reg.run(
        "lag_corr_scan",
        {"series_index_1": 1, "series_index_2": 2, "max_lag": 6},
        [first.tolist(), second.tolist()],
    )
    assert result.success
    assert result.data["best_lag"] == 3
    assert result.data["lead_lag_hint"] == "series_1_leads_series_2"
    assert result.data["best_corr"] > 0.99


def test_lag_corr_scan_prevents_two_point_spurious_correlation(reg):
    rng = np.random.default_rng(5)
    result = reg.run(
        "lag_corr_scan",
        {"max_lag": 28},
        [rng.normal(size=30).tolist(), rng.normal(size=30).tolist()],
    )
    assert result.success
    assert result.data["best_overlap"] >= result.data["min_overlap"]
    assert all(item["overlap"] >= result.data["min_overlap"] for item in result.data["lags"])


def test_lag_corr_scan_tie_prefers_zero_lag(reg):
    values = [float(i) for i in range(20)]
    result = reg.run("lag_corr_scan", {"max_lag": 5}, [values, values])
    assert result.success
    assert result.data["best_lag"] == 0
    assert result.data["lead_lag_hint"] == "synchronous"


def test_reverse_match_ranks_true_reverse_first(reg):
    query = [0.0, 1.0, 4.0, 9.0]
    result = reg.run(
        "reverse_match",
        {"query_series_index": 1, "candidate_series_indices": [2, 3], "method": "euclidean"},
        [query, query[::-1], query],
    )
    assert result.success
    assert result.data["nearest"]["series_index"] == 2
    assert result.data["nearest"]["reverse_distance"] == pytest.approx(0.0)


def test_reverse_match_rejects_invalid_method_and_empty_candidates(reg):
    series = [[1.0, 2.0], [2.0, 1.0]]
    invalid = reg.run("reverse_match", {"method": "cosine"}, series)
    empty = reg.run(
        "reverse_match",
        {"query_series_index": 1, "candidate_series_indices": [1]},
        series,
    )
    assert not invalid.success
    assert not empty.success


def test_robust_shape_match_handles_offset_scale_and_outlier(reg):
    query = np.sin(np.linspace(0, 2 * np.pi, 60))
    similar = 100 + 4 * query
    similar[10] += 30
    different = np.linspace(-1, 1, 60)
    result = reg.run(
        "robust_shape_match",
        {"query_series_index": 1, "candidate_series_indices": [2, 3], "winsor_percentile": 5},
        [query.tolist(), similar.tolist(), different.tolist()],
    )
    assert result.success
    assert result.data["nearest"]["series_index"] == 2
    assert result.data["winner_margin"] > 0


@pytest.mark.parametrize("winsor", [-1, 50, 75, float("nan")])
def test_robust_shape_match_rejects_invalid_winsor(reg, winsor):
    result = reg.run(
        "robust_shape_match",
        {"winsor_percentile": winsor},
        [[1.0, 2.0, 3.0], [1.0, 2.0, 3.0]],
    )
    assert not result.success


def test_caption_verify_ranks_series_by_structured_claims(reg):
    rising = [float(i) for i in range(30)]
    falling = rising[::-1]
    result = reg.run(
        "caption_verify",
        {
            "candidate_series_indices": [1, 2],
            "claims": [{"type": "trend", "expected": "upward"}],
        },
        [rising, falling],
    )
    assert result.success
    assert result.data["best_match"]["series_index"] == 1
    assert result.data["best_match"]["score"] == 1.0


def test_caption_verify_parses_false_string_strictly(reg):
    result = reg.run(
        "caption_verify",
        {"claims": [{"type": "has_anomaly", "expected": "false"}]},
        [[0.0, 1.0, -1.0, 0.5, -0.5] * 20],
    )
    assert result.success
    assert result.data["best_match"]["claims"][0]["passed"] is True


def test_caption_verify_excludes_candidate_with_no_applicable_claims(reg):
    result = reg.run(
        "caption_verify",
        {
            "candidate_series_indices": [1, 2],
            "claims": [{"type": "trend", "expected": "upward", "series_index": 2}],
        },
        [[4.0, 3.0, 2.0], [4.0, 3.0, 2.0]],
    )
    assert result.success
    assert result.data["best_match"]["series_index"] == 2
    assert result.data["best_match"]["score"] == 0.0


def test_caption_verify_supports_scalar_and_exact_extrema_claims(reg):
    values = [0.0, 2.0, 0.0, 1.0, 0.0]
    result = reg.run(
        "caption_verify",
        {
            "claims": [
                {"type": "max", "expected": 2.0},
                {"type": "max_index", "expected": 1},
                {"type": "n_peaks", "expected": 2},
                {"type": "end", "expected": 0.0},
            ]
        },
        [values],
    )
    assert result.success
    assert result.data["best_match"]["passed_claims"] == 4


@pytest.mark.parametrize("tool", sorted(NEW_TOOLS))
def test_missing_capability_tools_reject_nonfinite_input(reg, tool):
    args = {"series_index": 1}
    if tool in {"extrema_align", "lag_corr_scan"}:
        args = {"series_index_1": 1, "series_index_2": 2}
    elif tool in {"reverse_match", "robust_shape_match"}:
        args = {"query_series_index": 1}
    elif tool == "caption_verify":
        args = {"claims": [{"type": "trend", "expected": "upward"}]}
    elif tool == "counterfactual_simulate":
        args = {"operations": [{"op": "set_value", "index": 0, "value": 1.0}]}
    result = reg.run(tool, args, [[1.0, float("nan")], [1.0, 2.0]])
    assert not result.success
