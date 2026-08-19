"""Tests for WorkflowExecutor $ref resolution and stl null period handling."""
from __future__ import annotations

from ts_agent.schemas.models import InvocationPlan, ToolWorkflow
from ts_agent.tools.registry import build_default_registry
from ts_agent.tools.workflow import WorkflowExecutor, resolve_arg_value


def _series(n: int = 64, period: int = 8):
    return [[float((i % period) - period / 2) for i in range(n)]]


def test_resolve_step_ref_and_tool_alias():
    from ts_agent.schemas.models import ExecutedStep

    prior = {
        1: ExecutedStep(
            call_id="medium:step1",
            step=1,
            tool_name="fft_period",
            success=True,
            data={"series": [{"dominant_period": 8, "spectral_strength": 0.5}]},
        )
    }
    tool_to_step = {"fft_period": 1}
    assert resolve_arg_value("$step1.dominant_period", prior, tool_to_step) == 8
    assert resolve_arg_value("$fft_period.dominant_period", prior, tool_to_step) == 8


def test_workflow_fft_then_stl_with_ref():
    reg = build_default_registry()
    ex = WorkflowExecutor(reg)
    series = _series()
    workflow = ToolWorkflow(
        workflow=[
            {"step": 1, "tool": "fft_period", "output_key": "p", "input_binding": {}},
            {
                "step": 2,
                "tool": "stl_strength",
                "output_key": "s",
                "input_binding": {"period": "$step1.dominant_period"},
            },
        ]
    )
    calls = InvocationPlan(
        calls=[
            {"step": 1, "tool": "fft_period", "args": {"series_index": 1}},
            {"step": 2, "tool": "stl_strength", "args": {"series_index": 1, "period": "$step1.dominant_period"}},
        ]
    )
    steps = ex.execute(workflow, calls, series, ["medium"], "medium")
    assert len(steps) == 2
    assert steps[0].success, steps[0].error
    assert steps[1].success, steps[1].error
    assert "period" in (steps[1].resolved_arguments or {})
    assert isinstance(steps[1].resolved_arguments["period"], (int, float))
    assert steps[1].call_id == "medium:step2"


def test_stl_period_null_omitted_and_invalid_string():
    reg = build_default_registry()
    series = _series()
    ok = reg.run("stl_strength", {"series_index": 1, "period": None}, series)
    assert ok.success, ok.error
    bad = reg.run("stl_strength", {"series_index": 1, "period": "from_fft_period_tool"}, series)
    assert not bad.success
    assert "period" in (bad.error or "").lower()


def test_unresolved_optional_period_soft_omitted():
    """Missing optional $ref for period should omit the key and still run (auto period)."""
    reg = build_default_registry()
    ex = WorkflowExecutor(reg)
    workflow = ToolWorkflow(
        workflow=[{"step": 1, "tool": "stl_strength", "output_key": "s", "input_binding": {}}]
    )
    calls = InvocationPlan(
        calls=[{"step": 1, "tool": "stl_strength", "args": {"series_index": 1, "period": "$step9.dominant_period"}}]
    )
    steps = ex.execute(workflow, calls, _series(), ["medium"], "medium")
    assert len(steps) == 1
    assert steps[0].success, steps[0].error
    assert "period" not in (steps[0].resolved_arguments or {}) or isinstance(
        steps[0].resolved_arguments.get("period"), (int, float)
    )


def test_unresolved_required_ref_still_fails_when_not_optional():
    """Non-optional invalid $ refs (not soft keys) still fail the step."""
    from ts_agent.tools.workflow import resolve_arg_value

    try:
        resolve_arg_value("$not_a_valid_ref", {}, {}, soft_omit=False)
        assert False, "expected ValueError"
    except ValueError as e:
        assert "invalid reference" in str(e).lower()


def test_drops_hallucinated_tool_series_when_series_index_present():
    """S3 often emits series=$tool.series; S4 has series_index — must still run."""
    reg = build_default_registry()
    ex = WorkflowExecutor(reg)
    series = _series()
    workflow = ToolWorkflow(
        workflow=[
            {
                "step": 1,
                "tool": "fft_period",
                "output_key": "dominant_period",
                "input_binding": {"series": "$tool.series"},
            },
            {
                "step": 2,
                "tool": "stl_strength",
                "output_key": "seasonal_strength",
                "input_binding": {"series": "$tool.series", "period": "$step1.dominant_period"},
            },
        ]
    )
    calls = InvocationPlan(
        calls=[
            {"step": 1, "tool": "fft_period", "args": {"series_index": 1}},
            {
                "step": 2,
                "tool": "stl_strength",
                "args": {"series_index": 1, "period": "$step1.dominant_period"},
            },
        ]
    )
    steps = ex.execute(workflow, calls, series, ["medium"], "medium")
    assert steps[0].success, steps[0].error
    assert "series" not in (steps[0].arguments or {})
    assert steps[0].arguments.get("series_index") == 1
    assert steps[1].success, steps[1].error
    assert "series" not in (steps[1].arguments or {})


def test_drops_self_referential_series_binding():
    reg = build_default_registry()
    ex = WorkflowExecutor(reg)
    workflow = ToolWorkflow(
        workflow=[
            {
                "step": 1,
                "tool": "fft_period",
                "output_key": "dominant_period",
                "input_binding": {"series": "$step1.series"},
            }
        ]
    )
    calls = InvocationPlan(calls=[{"step": 1, "tool": "fft_period", "args": {"series_index": 1}}])
    steps = ex.execute(workflow, calls, _series(), ["medium"], "medium")
    assert steps[0].success, steps[0].error
    assert steps[0].arguments == {"series_index": 1}


def test_mismatched_s4_step_tools_do_not_poison_workflow():
    """S4 often emits fft/stl while S3 planned describe→hurst; do not apply stl args to hurst."""
    reg = build_default_registry()
    ex = WorkflowExecutor(reg)
    series = _series()
    workflow = ToolWorkflow(
        workflow=[
            {"step": 1, "tool": "describe_series", "output_key": "desc", "input_binding": {}},
            {"step": 2, "tool": "hurst_exponent", "output_key": "h", "input_binding": {}},
            {"step": 3, "tool": "fft_period", "output_key": "p", "input_binding": {}},
            {
                "step": 4,
                "tool": "noise_decomposition",
                "output_key": "n",
                "input_binding": {"period": "$step1.dominant_period"},
            },
        ]
    )
    # Deliberately wrong S4 plan (different tools / step meaning)
    calls = InvocationPlan(
        calls=[
            {"step": 1, "tool": "fft_period", "args": {"series_index": 1}},
            {"step": 2, "tool": "stl_strength", "args": {"series_index": 1, "period": "$step1.dominant_period"}},
        ]
    )
    steps = ex.execute(workflow, calls, series, ["long", "medium", "structure"], "long")
    by_tool = {s.tool_name: s for s in steps}
    assert by_tool["describe_series"].success, by_tool["describe_series"].error
    assert by_tool["hurst_exponent"].success, by_tool["hurst_exponent"].error
    assert "period" not in (by_tool["hurst_exponent"].resolved_arguments or {})
    assert by_tool["fft_period"].success, by_tool["fft_period"].error
    # Bad period ref soft-omitted; noise_decomposition still runs with auto period
    assert by_tool["noise_decomposition"].success, by_tool["noise_decomposition"].error
    assert "period" not in (by_tool["noise_decomposition"].resolved_arguments or {})


def test_soft_omit_missing_optional_path_and_invalid_series_dollar():
    reg = build_default_registry()
    ex = WorkflowExecutor(reg)
    series = [[float(i) for i in range(32)] for _ in range(3)]
    workflow = ToolWorkflow(
        workflow=[
            {"step": 1, "tool": "change_points", "output_key": "cp", "input_binding": {}},
            {
                "step": 2,
                "tool": "segment_trend",
                "output_key": "tr",
                "input_binding": {"start": "$step1.start", "end": "$step1.end"},
            },
            {
                "step": 3,
                "tool": "reverse_match",
                "output_key": "rm",
                "input_binding": {
                    "query_series_index": 1,
                    "candidate_series_indices": ["$candidate_series_indices[1]"],
                },
            },
        ]
    )
    calls = InvocationPlan(
        calls=[
            {"step": 1, "tool": "change_points", "args": {"series_index": 1}},
            {"step": 2, "tool": "segment_trend", "args": {"series_index": 1}},
            {
                "step": 3,
                "tool": "reverse_match",
                "args": {
                    "query_series_index": 1,
                    "candidate_series_indices": ["$candidate_series_indices[1]", 2, 3],
                },
            },
        ]
    )
    steps = ex.execute(workflow, calls, series, ["short", "medium", "matching", "reasoning"], "medium")
    assert steps[0].success, steps[0].error
    assert steps[1].success, steps[1].error
    assert "start" not in (steps[1].resolved_arguments or {})
    assert steps[2].success, steps[2].error
    # Invalid $ element dropped; literal candidates kept
    assert steps[2].resolved_arguments.get("candidate_series_indices") == [2, 3]
