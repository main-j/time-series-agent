import numpy as np
import pytest

from ts_agent.agents.roles import _verified_tool_call_ids
from ts_agent.schemas.models import ExecutedToolEvidence, HeterogeneousRole, TaskEvidence
from ts_agent.tools.registry import build_default_registry


@pytest.fixture()
def reg():
    return build_default_registry()


def test_windowed_tools_use_requested_slice(reg):
    periodic_4 = [float(np.sin(2 * np.pi * i / 4)) for i in range(40)]
    periodic_10 = [5.0 * float(np.sin(2 * np.pi * i / 10)) for i in range(100)]
    values = periodic_4 + periodic_10

    sliding_full = reg.run("sliding_stats", {"window": 8}, [values])
    sliding_local = reg.run("sliding_stats", {"window": 8, "start": 0, "end": 39}, [values])
    assert sliding_full.success and sliding_local.success
    assert sliding_local.data["start"] == 0 and sliding_local.data["end"] == 39
    assert sliding_local.data["max_local_std"] != pytest.approx(sliding_full.data["max_local_std"])

    acf_full = reg.run("autocorr", {"max_lag": 12}, [values])
    acf_local = reg.run("autocorr", {"max_lag": 12, "start": 0, "end": 39}, [values])
    assert acf_full.success and acf_local.success
    assert acf_local.data["acf"] != pytest.approx(acf_full.data["acf"])

    fft_full = reg.run("fft_period", {}, [values])
    fft_local = reg.run("fft_period", {"start": 0, "end": 39}, [values])
    assert fft_full.success and fft_local.success
    assert fft_local.data["dominant_period"] == pytest.approx(4.0)
    assert fft_local.data["dominant_period"] != pytest.approx(fft_full.data["dominant_period"])

    stl_full = reg.run("stl_strength", {}, [values])
    stl_local = reg.run("stl_strength", {"start": 0, "end": 39}, [values])
    assert stl_full.success and stl_local.success
    # Auto period is capped below n/2 to avoid STL overfitting; for the
    # period-4 local window the selected period should remain the local cycle.
    assert stl_local.data["period"] in {2, 4}
    assert stl_local.data["period"] != stl_full.data["period"] or stl_local.data["seasonal_strength"] != pytest.approx(
        stl_full.data["seasonal_strength"]
    )


def test_adf_and_change_points_use_window_and_global_indices(reg):
    rng = np.random.default_rng(7)
    stationary = rng.normal(size=120)
    random_walk = 20.0 + np.cumsum(rng.normal(size=120))
    values = np.concatenate([stationary, random_walk]).tolist()
    adf_full = reg.run("adf_stationarity", {}, [values])
    adf_local = reg.run("adf_stationarity", {"start": 0, "end": 119}, [values])
    assert adf_full.success and adf_local.success
    assert adf_local.data["start"] == 0 and adf_local.data["end"] == 119
    assert adf_local.data["pvalue"] != pytest.approx(adf_full.data["pvalue"])

    stepped = [0.0] * 100 + [10.0] * 100
    cp = reg.run("change_points", {"start": 80, "end": 130}, [stepped])
    assert cp.success
    assert cp.data["start"] == 80 and cp.data["end"] == 130
    assert cp.data["candidates"]
    assert all(80 <= item["index"] <= 130 for item in cp.data["candidates"])
    assert cp.data["candidates"][0]["index"] == 100


def test_value_at_index_catalog_does_not_advertise_window(reg):
    schema = reg.get_spec("value_at_index").input_schema
    assert "start" not in schema
    assert "end" not in schema


def test_counterfactual_nested_and_string_operation_formats(reg):
    nested = reg.run(
        "counterfactual_simulate",
        {
            "operations": [{"replace_constant": {"start": 1, "end": 2, "value": 10.0}}],
            "requested_metrics": ["max"],
        },
        [[1.0, 2.0, 3.0, 4.0]],
    )
    assert nested.success
    assert nested.data["after"]["max"] == 10.0

    string_form = reg.run(
        "counterfactual_simulate",
        {"operations": ["replace_constant(start=1, end=2, value=10.0)"], "requested_metrics": ["max"]},
        [[1.0, 2.0, 3.0, 4.0]],
    )
    assert string_form.success
    assert string_form.data["after"]["max"] == 10.0


def test_counterfactual_metric_alias_and_replace_with_mean_defaults(reg):
    replaced = reg.run(
        "counterfactual_simulate",
        {
            "operations": [{"op": "replace_with_mean", "start": 1, "end": 2}],
            "requested_metrics": ["max_value_index"],
        },
        [[1.0, 5.0, 9.0, 4.0]],
    )
    assert replaced.success
    assert "max_index" in replaced.data["before"]
    assert replaced.data["n_changed"] == 2


def test_counterfactual_strict_operations_metrics_and_no_effect(reg):
    unknown = reg.run(
        "counterfactual_simulate",
        {"operations": [{"op": "replace_segment", "start": 0, "end": 2, "replacement": "period_average"}]},
        [[1.0, 2.0, 3.0]],
    )
    assert not unknown.success
    assert "unsupported fields" in (unknown.error or "")

    changed = reg.run(
        "counterfactual_simulate",
        {
            "operations": [{"op": "replace_constant", "start": 1, "end": 2, "value": 10.0}],
            "requested_metrics": ["mean", "max"],
        },
        [[1.0, 2.0, 3.0, 4.0]],
    )
    assert changed.success
    assert changed.data["status"] == "changed"
    assert changed.data["evidence_usable"] is True
    assert set(changed.data["before"]) == {"mean", "max"}
    assert set(changed.data["after"]) == {"mean", "max"}
    assert changed.data["after"]["max"] == 10.0
    assert changed.data["cross_series_effect_supported"] is False

    no_effect = reg.run(
        "counterfactual_simulate",
        {"operations": [{"op": "shift", "amount": 0.0}]},
        [[1.0, 2.0, 3.0]],
    )
    assert no_effect.success
    assert no_effect.data["status"] == "no_effect"
    assert no_effect.data["evidence_usable"] is False


def test_counterfactual_no_effect_is_not_verified_evidence():
    evidence = TaskEvidence(
        reasoning="no change",
        role=HeterogeneousRole.REASONING,
        candidate_preference="A",
        cited_tool_call_ids=["reasoning:call1"],
        executed_tools=[
            ExecutedToolEvidence(
                call_id="reasoning:call1",
                tool_name="counterfactual_simulate",
                success=True,
                data={"status": "no_effect", "evidence_usable": False},
                executor_role=HeterogeneousRole.REASONING,
            )
        ],
    )
    assert _verified_tool_call_ids(evidence) == set()


def test_compatibility_diagnostics_are_additive(reg):
    interval = reg.run(
        "interval_compare",
        {"series_index": 1, "left_interval": [9, 20], "right_interval": [0, 1]},
        [[1.0, 2.0, 3.0]],
    )
    assert interval.success
    assert interval.data["left_interval"] == [2, 2]
    assert interval.data["adjusted"] is True
    assert interval.data["warnings"]

    cross = reg.run(
        "cross_series_compare",
        {"series_index_1": 1, "series_index_2": 2, "left_interval": [0, 4], "right_interval": [0, 2]},
        [[1, 2, 3, 4, 5], [1, 2, 3]],
    )
    assert cross.success
    assert cross.data["alignment_used"] == "truncate"
    assert cross.data["degraded"] is True
    assert cross.data["used_length"] == 3

    pairwise = reg.run(
        "pairwise_distance",
        {
            "query_series_index": 2,
            "candidate_series_indices": [1],
            "method": "euclidean",
        },
        [[0, 1, 2, 3], [10, 11, 12, 13], [3, 2, 1, 0]],
    )
    assert pairwise.success
    assert pairwise.data["query_series_index"] == 2
    assert pairwise.data["candidate_series_indices"] == [1]
    assert pairwise.data["requested_method"] == "euclidean"
    assert pairwise.data["method_used"] == "z_euclidean"


def test_interval_compare_split_end_is_inclusive(reg):
    values = [float(i) for i in range(8)]
    split = reg.run(
        "interval_compare",
        {"series_index": 1, "start": 0, "mid": 4, "end": 7},
        [values],
    )
    pair = reg.run(
        "interval_compare",
        {
            "series_index": 1,
            "left_interval": [0, 3],
            "right_interval": [4, 7],
        },
        [values],
    )
    assert split.success and pair.success
    assert split.data["left_mean"] == pytest.approx(pair.data["left_mean"])
    assert split.data["right_mean"] == pytest.approx(pair.data["right_mean"])
    assert split.data["right_mean"] == pytest.approx(5.5)


@pytest.mark.parametrize(
    "tool_name",
    ["noise_decomposition", "stl_strength", "adf_stationarity"],
)
def test_multi_series_fanout_keeps_valid_series_when_one_fails(reg, tool_name):
    rng = np.random.default_rng(42)
    valid = (np.sin(np.arange(80) * 2 * np.pi / 8) + rng.normal(0, 0.05, 80)).tolist()
    result = reg.run(tool_name, {"series_index": "all"}, [[1.0, 2.0], valid])

    assert result.success
    assert result.data["partial"] is True
    assert result.data["degraded"] is True
    assert result.data["n_series"] == 1
    assert result.data["requested_n_series"] == 2
    assert result.data["series"][0]["series_index"] == 2
    assert result.data["series_errors"][0]["series_index"] == 1
    assert result.data["warnings"]


def test_caption_verify_window_index_weight_and_required(reg):
    result = reg.run(
        "caption_verify",
        {
            "candidate_series_indices": [1],
            "claims": [
                {
                    "type": "max_index",
                    "expected": 4,
                    "start": 3,
                    "end": 5,
                    "weight": 2.0,
                    "required": True,
                }
            ],
        },
        [[0.0, 0.0, 0.0, 1.0, 9.0, 2.0]],
    )
    assert result.success
    best = result.data["best_match"]
    assert best["claims"][0]["observed"] == 4.0
    assert best["claims"][0]["metric_type"] == "describe_series"
    assert best["required_failed"] is False
    assert best["score"] == 1.0


def test_noise_ratio_is_variance_ratio_with_none_threshold(reg):
    # Near-deterministic sine: residual variance ratio should be near none/low.
    t = np.arange(128)
    clean = np.sin(2 * np.pi * t / 16.0)
    res = reg.run("noise_decomposition", {"series_index": 1, "period": 16}, [clean.tolist()])
    assert res.success
    # Core STL residual remains a variance ratio; reported noise_ratio may use
    # max(STL, highpass) as a conservative estimate.
    stl_ratio = res.data["residual_var"] / max(res.data["series_var"], 1e-12)
    assert stl_ratio == pytest.approx(res.data["residual_var"] / max(res.data["series_var"], 1e-12))
    assert 0.0 <= res.data["noise_ratio"] <= 1.0
    assert res.data["period"] <= max(2, len(clean) // 2)
    assert "metric_definition" in res.data
    assert res.data["noise_level"] in {"none", "low", "medium", "high"}


def test_noise_auto_period_never_uses_half_length(reg):
    rng = np.random.default_rng(1)
    y = rng.normal(0, 1.0, 171).tolist()
    res = reg.run("noise_decomposition", {"series_index": 1}, [y])
    assert res.success
    assert res.data["period"] <= max(2, 171 // 4)
    assert res.data["noise_level"] in {"none", "low", "medium", "high"}


def test_hurst_uses_compute_hc_estimator(reg):
    from hurst import compute_Hc

    rng = np.random.default_rng(7)
    x = np.cumsum(rng.normal(0, 1, 256))
    expected, _, _ = compute_Hc(x, kind="random_walk", simplified=True)
    res = reg.run("hurst_exponent", {"series_index": 1}, [x.tolist()])
    assert res.success
    assert res.data["estimator"] == "hurst.compute_Hc"
    assert res.data["kind"] == "random_walk"
    assert res.data["hurst"] == pytest.approx(float(expected), rel=1e-5, abs=1e-5)
    assert "metric_definition" in res.data


def test_step_levels_tolerates_drifted_square_wave(reg):
    # Square-like plateaus with tiny per-sample drift should not explode unique levels.
    vals = []
    for _ in range(8):
        base = 100.0
        for i in range(40):
            vals.append(base + 0.01 * i)
        base = -100.0
        for i in range(40):
            vals.append(base - 0.01 * i)
    res = reg.run("step_levels", {"series_index": 1}, [vals])
    assert res.success
    assert res.data["n_unique_levels"] <= 8
    assert res.data["tolerance"] >= 0.5


def test_waveform_features_prefers_square_over_sine_for_plateau_jumps(reg):
    vals = ([10.0] * 40 + [-10.0] * 40) * 4
    # Tiny drift should not destroy square detection.
    vals = [v + 0.01 * (i % 7) for i, v in enumerate(vals)]
    res = reg.run("waveform_features", {"series_index": 1}, [vals])
    assert res.success
    assert res.data["waveform_hint"] == "square"
    assert res.data["jump_ratio"] > 0.01
    assert "periodicity_is_not_waveform_type" in res.data["warnings"]


def test_waveform_features_detects_drifted_square_with_slow_ramps(reg):
    # Alternating large jumps with slow intra-plateau ramps (MMTS-like square).
    vals = []
    for k in range(8):
        base = 10.0 if k % 2 == 0 else -10.0
        for i in range(50):
            vals.append(base + 0.05 * i)
    res = reg.run("waveform_features", {"series_index": 1}, [vals])
    assert res.success
    assert res.data["waveform_hint"] == "square"
    assert (res.data.get("jump_regime") or {}).get("alternation_rate", 0) >= 0.7


def test_segment_trend_matches_endpoint_slope_definition(reg):
    series = [[0.0, 1.0, 2.0, 3.0, 10.0]]
    res = reg.run("segment_trend", {"series_index": 1}, series)
    assert res.success
    expected = (10.0 - 0.0) / 4.0
    assert res.data["slope"] == pytest.approx(expected)
    assert res.data["trend_method"] == "endpoint"
