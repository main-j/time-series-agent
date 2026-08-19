"""Stage schema parse and no-tool decision validation."""
from __future__ import annotations

import json
from pathlib import Path

from ts_agent.agents.roles import HomogeneousAgent, HeterogeneousAgent, build_temporal_profile
from ts_agent.core.llm import LLMProvider, LLMResponse
from ts_agent.prompts.library import PromptLibrary
from ts_agent.schemas.models import (
    CapabilitySelection,
    EvidenceCapabilityPlan,
    EvidencePlan,
    HeterogeneousRole,
    MMTSSample,
    NoToolDecision,
    ScaleName,
    ScaleObservation,
    SubsetName,
    TemporalProfile,
)
from ts_agent.tools.registry import build_default_registry

PROMPTS = Path(__file__).resolve().parents[1] / "prompts"


class ScriptedLLM(LLMProvider):
    def __init__(self, scripts):
        self.scripts = list(scripts)
        self.idx = 0
        self.calls = []

    def generate(self, messages, **kwargs):
        self.calls.append({"tag": kwargs.get("call_tag"), "messages": messages})
        text = self.scripts[min(self.idx, len(self.scripts) - 1)]
        self.idx += 1
        return LLMResponse(text=text, raw={"scripted": True})


def _sample():
    series = [[float(i % 8) for i in range(48)]]
    return MMTSSample(
        sample_id="sim:stage:0",
        source_file="sim.csv",
        row_index=0,
        subset=SubsetName.BASE,
        question_type="choice",
        question="How strong is seasonality?",
        option="A. strong\nB. moderate\nC. weak",
        answer="B",
        series=series,
        series_text=f"Given Time Series 1: {series[0]}",
        metadata={"n_series": 1, "series_lengths": [48], "index_base": 0, "focus_intervals": []},
    )


def test_evidence_capability_plan_roundtrip():
    payload = {
        "reasoning": "need period and strength",
        "evidence_plan": {
            "objective": "seasonality",
            "claims_to_support": [{"claim": "has seasonality", "required_evidence": ["seasonal_strength"]}],
            "analysis_scope": {"target_series": [1]},
        },
        "capability_selection": {
            "selected_tools": [{"tool": "stl_strength", "reason": "need strength", "supports_evidence": ["seasonal_strength"]}],
            "no_tool_decision": None,
        },
    }
    plan = EvidenceCapabilityPlan.model_validate(payload)
    assert plan.capability_selection.selected_tools[0].tool == "stl_strength"


def test_stage_no_tool_heter_skips_s3_s4():
    s1s2 = json.dumps(
        {
            "reasoning": "homo already measured strength",
            "evidence_plan": {
                "objective": "map strength to option",
                "claims_to_support": [{"claim": "moderate", "required_evidence": ["seasonal_strength"]}],
            },
            "capability_selection": {
                "selected_tools": [],
                "no_tool_decision": {
                    "skip_tools": True,
                    "reason": "temporal_profile already has seasonal_strength",
                    "evidence_sources": [{"type": "upstream_observation", "ref": "medium:step2", "field": "seasonal_strength"}],
                },
            },
        }
    )
    s5 = json.dumps(
        {
            "reasoning": "use upstream",
            "role": "structure",
            "hypothesis": "moderate",
            "evidence": ["seasonal_strength=0.62"],
            "candidate_preference": "B",
            "confidence": 0.8,
            "tool_calls": [],
            "cited_tool_call_ids": ["medium:step2"],
            "executed_tools": [],
            "tool_summaries": [],
            "reasoning_claims": [
                {
                    "claim": "moderate",
                    "evidence": [
                        {
                            "type": "seasonal_strength",
                            "value": 0.62,
                            "provenance": "upstream",
                            "ref": "medium:step2",
                            "call_id": "medium:step2",
                        }
                    ],
                    "confidence": "context_supported",
                }
            ],
            "coverage": {"seasonal_strength": "context_supported"},
            "unresolved_claims": [],
        }
    )
    llm = ScriptedLLM([s1s2, s5])
    agent = HeterogeneousAgent(llm, PromptLibrary(PROMPTS), build_default_registry())
    profile = TemporalProfile(
        medium=ScaleObservation(
            reasoning="ok",
            scale=ScaleName.MEDIUM,
            observations=["seasonal_strength=0.62"],
            structured_observations=[
                {
                    "claim": "seasonal",
                    "evidence": [{"type": "seasonal_strength", "value": 0.62, "call_id": "medium:step2", "provenance": "tool"}],
                    "confidence": "tool_supported",
                }
            ],
        ),
        summary="seasonal_strength=0.62",
    )
    ev, n_tools = agent.run(_sample(), HeterogeneousRole.STRUCTURE, profile)
    assert n_tools == 0
    assert ev.skipped_stages == ["S3", "S4"]
    assert ev.candidate_preference == "B"
    assert "medium:step2" in ev.cited_tool_call_ids
    tags = [c["tag"] for c in llm.calls]
    assert any("s1s2" in t for t in tags)
    assert not any(":s3:" in t for t in tags)
    assert not any(":s4:" in t for t in tags)
    assert any("s5" in t for t in tags)


def test_stage_no_tool_invalid_homo_forces_describe():
    s1s2 = json.dumps(
        {
            "reasoning": "skip without reason",
            "evidence_plan": {"objective": "x", "claims_to_support": []},
            "capability_selection": {"selected_tools": [], "no_tool_decision": None},
        }
    )
    # After invalid no-tool, agent selects describe_series and needs S3/S4/S5
    s3 = json.dumps(
        {
            "reasoning": "run describe",
            "workflow": [{"step": 1, "tool": "describe_series", "output_key": "d", "input_binding": {}}],
        }
    )
    s4 = json.dumps({"reasoning": "args", "calls": [{"step": 1, "tool": "describe_series", "args": {}}]})
    s5 = json.dumps(
        {
            "reasoning": "done",
            "scale": "short",
            "observations": ["described"],
            "confidence": 0.5,
            "tool_calls": [],
            "structured_observations": [],
            "coverage": {},
            "unresolved_claims": [],
        }
    )
    llm = ScriptedLLM([s1s2, s3, s4, s5])
    agent = HomogeneousAgent(llm, PromptLibrary(PROMPTS), build_default_registry())
    obs, n_tools = agent.run(_sample(), ScaleName.SHORT)
    assert n_tools >= 1
    assert "S3" not in obs.skipped_stages
    assert any(s.tool_name == "describe_series" for s in obs.executed_steps)


def test_homo_four_stage_happy_path():
    s1s2 = json.dumps(
        {
            "reasoning": "need fft and stl",
            "evidence_plan": {
                "objective": "seasonality",
                "claims_to_support": [
                    {"claim": "period", "required_evidence": ["dominant period"]},
                    {"claim": "strength", "required_evidence": ["seasonal_strength"]},
                ],
            },
            "capability_selection": {
                "selected_tools": [
                    {"tool": "fft_period", "reason": "period", "supports_evidence": ["dominant period"]},
                    {"tool": "stl_strength", "reason": "strength", "supports_evidence": ["seasonal_strength"]},
                ]
            },
        }
    )
    s3 = json.dumps(
        {
            "reasoning": "chain",
            "workflow": [
                {"step": 1, "tool": "fft_period", "output_key": "p", "input_binding": {}},
                {"step": 2, "tool": "stl_strength", "output_key": "s", "input_binding": {"period": "$step1.dominant_period"}},
            ],
        }
    )
    s4 = json.dumps(
        {
            "reasoning": "args",
            "calls": [
                {"step": 1, "tool": "fft_period", "args": {"series_index": 1}},
                {"step": 2, "tool": "stl_strength", "args": {"series_index": 1, "period": "$step1.dominant_period"}},
            ],
        }
    )
    s5 = json.dumps(
        {
            "reasoning": "ok",
            "scale": "medium",
            "observations": ["seasonal_strength measured"],
            "confidence": 0.8,
            "tool_calls": [],
            "structured_observations": [
                {
                    "claim": "strength",
                    "evidence": [{"type": "seasonal_strength", "value": 0.5, "call_id": "medium:step2", "provenance": "tool"}],
                    "confidence": "tool_supported",
                    "maps_to_measurement": "seasonal_strength",
                }
            ],
            "coverage": {"seasonal_strength": "tool_supported"},
            "unresolved_claims": [],
        }
    )
    llm = ScriptedLLM([s1s2, s3, s4, s5])
    agent = HomogeneousAgent(llm, PromptLibrary(PROMPTS), build_default_registry())
    obs, n_tools = agent.run(_sample(), ScaleName.MEDIUM)
    assert n_tools == 2
    assert len(obs.executed_steps) == 2
    assert obs.executed_steps[0].success
    assert obs.executed_steps[1].success
    profile = build_temporal_profile([obs])
    assert "medium" in profile.structured_by_scale
