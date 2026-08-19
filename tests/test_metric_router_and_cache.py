"""Tests for autonomous tool contracts and tool execution cache."""
from __future__ import annotations

from pathlib import Path

from ts_agent.prompts.library import PromptLibrary
from ts_agent.tools.call_normalizer import canonicalize_arguments, fingerprint
from ts_agent.tools.execution_cache import ToolExecutionCache
from ts_agent.tools.registry import build_default_registry


ROOT = Path(__file__).resolve().parents[1]


def test_fingerprint_aliases_window_size_and_window():
    a = fingerprint("sliding_stats", {"series_index": 1, "window_size": 8})
    b = fingerprint("sliding_stats", {"series_index": 1, "window": 8})
    assert a == b
    assert canonicalize_arguments("sliding_stats", {"window_size": 8})["window"] == 8


def test_fingerprint_differs_for_different_windows():
    a = fingerprint("hurst_exponent", {"series_index": 1, "start": 0, "end": 10})
    b = fingerprint("hurst_exponent", {"series_index": 1, "start": 0, "end": 20})
    assert a != b


def test_execution_cache_hits_identical_calls():
    reg = build_default_registry()
    cache = ToolExecutionCache()
    series = [[float(i % 7) for i in range(64)]]
    r1 = cache.run(reg, "hurst_exponent", {"series_index": 1}, series)
    r2 = cache.run(reg, "hurst_exponent", {"series_index": 1}, series)
    assert r1.success and r2.success
    assert cache.misses == 1
    assert cache.hits == 1
    assert r1.data.get("evidence_source_id")
    assert r1.data.get("call_fingerprint")
    assert r2.data["call_fingerprint"] == r1.data["call_fingerprint"]


def test_catalog_exposes_complete_contracts_without_metric_binding():
    reg = build_default_registry()
    catalog = reg.catalog_text(["structure"])
    assert "returns:" in catalog
    assert "use_when:" in catalog
    assert "avoid_when:" in catalog
    assert "limitations:" in catalog
    assert "tool_directives" not in catalog
    for spec in reg.list_for_roles(["short", "medium", "long", "structure"]):
        assert spec.description
        assert spec.input_schema
        assert spec.output_schema
        assert spec.use_when
        assert spec.avoid_when
        assert spec.limitations


def test_prompts_no_longer_contain_overfit_once_rules():
    prompts = PromptLibrary(ROOT / "prompts")
    registry = build_default_registry()
    planner = prompts.get("planner_v1")["system"]
    homo = prompts.get("homogeneous_v1")["system"]
    hetero = prompts.get("heterogeneous_v1")["system"]
    integration = prompts.get("integration_v1")["system"]
    tool_catalog = registry.catalog_text(
        ["short", "medium", "long", "structure", "reasoning", "matching", "alignment"]
    )
    banned = [
        "once on full series",
        "prefer scales=[\"long\"] only",
        "MMTS-compatible",
        "MMTS thresholds",
        "mandatory for \"reverse it\"",
        "call the single dedicated tool once",
    ]
    joined = "\n".join([planner, homo, hetero, integration, tool_catalog])
    for phrase in banned:
        assert phrase not in joined, phrase
    assert "call_id" not in integration
    assert "option_to_series" not in integration
    assert len(integration) < 2500
