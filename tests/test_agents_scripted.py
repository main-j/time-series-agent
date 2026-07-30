"""Simulate each agent's input with a scripted LLM and verify expected behavior."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

import pytest

from ts_agent.agents.roles import (
    BaselineAgent,
    HeterogeneousAgent,
    HomogeneousAgent,
    IntegrationAgent,
    PlannerAgent,
    build_temporal_profile,
)
from ts_agent.core.llm import LLMProvider, LLMResponse
from ts_agent.prompts.library import PromptLibrary
from ts_agent.schemas.models import (
    HeterogeneousRole,
    MMTSSample,
    ScaleName,
    SubsetName,
    TemporalProfile,
)
from ts_agent.tools.registry import build_default_registry

PROMPTS = Path(__file__).resolve().parents[1] / "prompts"


def _sample_univariate() -> MMTSSample:
    series = [[float(i % 12) + 0.1 * i for i in range(48)]]
    return MMTSSample(
        sample_id="sim:uni:0",
        source_file="sim.csv",
        row_index=0,
        subset=SubsetName.BASE,
        qa_type="a multiple choice question",
        question_type="choice",
        local_overall="overall",
        task_type="['trend analysis']",
        question="Based on Time Series 1, which option best describes the trend?",
        option="A. upward\nB. downward\nC. flat\nD. seasonal only",
        answer="A",
        domain="synthetic",
        is_univariate=True,
        series=series,
        series_text=f"Given Time Series 1: {series[0]}",
    )


def _sample_multivariate() -> MMTSSample:
    q = [float(i) for i in range(24)]
    cands = [
        [float(i) + 0.1 for i in range(24)],
        [float(23 - i) for i in range(24)],
        [0.0] * 24,
        [float(i * i) for i in range(24)],
    ]
    series = [q] + cands
    return MMTSSample(
        sample_id="sim:multi:0",
        source_file="sim_match.csv",
        row_index=0,
        subset=SubsetName.MATCH,
        qa_type="a multiple choice question",
        question_type="choice",
        local_overall="overall",
        task_type="['choose it']",
        question="Which candidate sequence is most similar to Time Series 1?",
        option="A. TS2\nB. TS3\nC. TS4\nD. TS5",
        answer="A",
        domain="traffic",
        is_univariate=False,
        series=series,
        series_text="\n".join(f"Given Time Series {i+1}: {s}" for i, s in enumerate(series)),
    )


class ScriptedLLM(LLMProvider):
    """Returns pre-scripted JSON/text per call; records every prompt for assertions."""

    def __init__(self, scripts: List[str]):
        self.scripts = list(scripts)
        self.calls: List[List[Dict[str, str]]] = []
        self.idx = 0

    def generate(self, messages: List[Dict[str, str]], **kwargs: Any) -> LLMResponse:
        self.calls.append(messages)
        if self.idx >= len(self.scripts):
            raise AssertionError(f"ScriptedLLM exhausted after {len(self.scripts)} calls; got extra: {messages[0]['content'][:80]}")
        text = self.scripts[self.idx]
        self.idx += 1
        return LLMResponse(text=text, raw={"scripted": True})

    def assert_consumed(self) -> None:
        assert self.idx == len(self.scripts), f"unused scripts: {len(self.scripts) - self.idx}"


def _joined(messages: List[Dict[str, str]]) -> str:
    return "\n".join(m["content"] for m in messages)


def _has_tags(text: str, tags: List[str]) -> None:
    for t in tags:
        assert f"<{t}>" in text and f"</{t}>" in text, f"missing delimiters <{t}>"


@pytest.fixture
def prompts() -> PromptLibrary:
    return PromptLibrary(str(PROMPTS))


@pytest.fixture
def tools():
    return build_default_registry()


def test_planner_agent_expected_plan(prompts):
    sample = _sample_univariate()
    plan_json = json.dumps(
        {
            "reasoning": "Trend analysis overall univariate -> all scales + structure/reasoning.",
            "capability": "feature_analysis",
            "scope": "overall",
            "univariate": True,
            "scales": ["short", "medium", "long"],
            "heterogeneous_agents": ["structure", "reasoning"],
            "notes": "simulated",
        }
    )
    llm = ScriptedLLM([plan_json])
    agent = PlannerAgent(llm, prompts)
    plan = agent.run(sample)

    assert plan.capability == "feature_analysis"
    assert plan.scope == "overall"
    assert plan.univariate is True
    assert plan.scales == [ScaleName.SHORT, ScaleName.MEDIUM, ScaleName.LONG]
    assert HeterogeneousRole.STRUCTURE in plan.heterogeneous_agents
    assert HeterogeneousRole.REASONING in plan.heterogeneous_agents

    text = _joined(llm.calls[0])
    _has_tags(text, ["question", "candidates", "metadata"])
    assert "do NOT call tools" in text or "do NOT call tools" in prompts.render("planner_v1")["system"]
    llm.assert_consumed()


def test_homogeneous_short_tool_loop_then_observe(prompts, tools):
    sample = _sample_univariate()
    # Round1: request whitelist tool; Round2: interpret with empty tool_calls
    round1 = json.dumps(
        {
            "reasoning": "Need local volatility evidence.",
            "scale": "short",
            "observations": ["pending tools"],
            "evidence_intervals": [],
            "confidence": 0.4,
            "tool_calls": [{"name": "sliding_stats", "arguments": {"window": 5}}],
            "tool_summaries": [],
        }
    )
    round2 = json.dumps(
        {
            "reasoning": "Interpreted sliding_stats.",
            "scale": "short",
            "observations": ["Local volatility present from tool evidence."],
            "evidence_intervals": ["0:48"],
            "confidence": 0.7,
            "tool_calls": [],
            "tool_summaries": [],
        }
    )
    llm = ScriptedLLM([round1, round2])
    agent = HomogeneousAgent(llm, prompts, tools, max_tool_rounds=3)
    obs, n_tools = agent.run(sample, ScaleName.SHORT)

    assert n_tools == 1
    assert obs.scale == ScaleName.SHORT
    assert "Local volatility" in obs.observations[0]
    assert obs.tool_calls == []
    assert obs.tool_summaries  # filled from tool results
    assert '"success": true' in obs.tool_summaries[0] or '"success": True' in obs.tool_summaries[0] or "success" in obs.tool_summaries[0]

    # prompt wiring
    text1 = _joined(llm.calls[0])
    _has_tags(text1, ["question", "timeseries", "metadata", "tool_catalog", "tool_results"])
    assert "sliding_stats" in text1  # whitelist catalog for short
    assert "pairwise_distance" not in text1  # not in short whitelist
    text2 = _joined(llm.calls[1])
    assert "(none)" not in text2.split("<tool_results>")[1][:20] or "sliding_stats" in text2
    llm.assert_consumed()


def test_homogeneous_rejects_out_of_whitelist_tool(prompts, tools):
    sample = _sample_univariate()
    round1 = json.dumps(
        {
            "reasoning": "Wrongly request matching tool.",
            "scale": "short",
            "observations": ["pending"],
            "confidence": 0.3,
            "tool_calls": [{"name": "pairwise_distance", "arguments": {}}],
            "tool_summaries": [],
        }
    )
    round2 = json.dumps(
        {
            "reasoning": "Saw rejection; finish without tools.",
            "scale": "short",
            "observations": ["No valid tool evidence."],
            "confidence": 0.2,
            "tool_calls": [],
            "tool_summaries": [],
        }
    )
    llm = ScriptedLLM([round1, round2])
    agent = HomogeneousAgent(llm, prompts, tools, max_tool_rounds=3)
    obs, n_tools = agent.run(sample, ScaleName.SHORT)
    # rejected tools are not counted as successful runs in _run_tools count... looking at code:
    # count increments only when name in allowed; rejected appends error but continue without count+=1
    assert n_tools == 0
    assert any("not allowed" in s.lower() or "Tool not allowed" in s for s in obs.tool_summaries)
    llm.assert_consumed()


@pytest.mark.parametrize(
    "scale,tool_name,args",
    [
        (ScaleName.MEDIUM, "fft_period", {}),
        (ScaleName.LONG, "adf_stationarity", {}),
    ],
)
def test_homogeneous_medium_long_tools(prompts, tools, scale, tool_name, args):
    sample = _sample_univariate()
    round1 = json.dumps(
        {
            "reasoning": f"Need {tool_name}",
            "scale": scale.value,
            "observations": ["pending"],
            "confidence": 0.4,
            "tool_calls": [{"name": tool_name, "arguments": args}],
            "tool_summaries": [],
        }
    )
    round2 = json.dumps(
        {
            "reasoning": "done",
            "scale": scale.value,
            "observations": [f"{scale.value} observation"],
            "confidence": 0.6,
            "tool_calls": [],
            "tool_summaries": [],
        }
    )
    llm = ScriptedLLM([round1, round2])
    agent = HomogeneousAgent(llm, prompts, tools, max_tool_rounds=3)
    obs, n_tools = agent.run(sample, scale)
    assert n_tools == 1
    assert obs.scale == scale
    assert tool_name in obs.tool_summaries[0]
    catalog = _joined(llm.calls[0])
    assert tool_name in catalog
    llm.assert_consumed()


def test_heterogeneous_matching_uses_distance_tool(prompts, tools):
    sample = _sample_multivariate()
    profile = TemporalProfile(summary="short: local var; medium: period~12; long: mild trend")
    round1 = json.dumps(
        {
            "reasoning": "Compare candidates with pairwise distance.",
            "role": "matching",
            "evidence": ["pending"],
            "candidate_preference": "A",
            "confidence": 0.4,
            "tool_calls": [{"name": "pairwise_distance", "arguments": {"method": "euclidean"}}],
            "tool_summaries": [],
        }
    )
    round2 = json.dumps(
        {
            "reasoning": "Nearest is series 2 -> option A.",
            "role": "matching",
            "evidence": ["euclidean nearest points to TS2"],
            "candidate_preference": "A",
            "confidence": 0.8,
            "tool_calls": [],
            "tool_summaries": [],
        }
    )
    llm = ScriptedLLM([round1, round2])
    agent = HeterogeneousAgent(llm, prompts, tools, max_tool_rounds=3)
    ev, n_tools = agent.run(sample, HeterogeneousRole.MATCHING, profile)
    assert n_tools == 1
    assert ev.role == HeterogeneousRole.MATCHING
    assert ev.candidate_preference == "A"
    assert "pairwise_distance" in ev.tool_summaries[0]
    text = _joined(llm.calls[0])
    _has_tags(text, ["question", "candidates", "timeseries", "temporal_profile", "tool_catalog", "tool_results"])
    assert "pairwise_distance" in text
    llm.assert_consumed()


@pytest.mark.parametrize(
    "role,tool_name",
    [
        (HeterogeneousRole.STRUCTURE, "describe_series"),
        (HeterogeneousRole.REASONING, "interval_compare"),
        (HeterogeneousRole.ALIGNMENT, "describe_series"),
    ],
)
def test_heterogeneous_other_roles(prompts, tools, role, tool_name):
    sample = _sample_univariate()
    profile = TemporalProfile(summary="profile")
    round1 = json.dumps(
        {
            "reasoning": f"call {tool_name}",
            "role": role.value,
            "evidence": ["pending"],
            "candidate_preference": "A",
            "confidence": 0.5,
            "tool_calls": [{"name": tool_name, "arguments": {}}],
            "tool_summaries": [],
        }
    )
    round2 = json.dumps(
        {
            "reasoning": "done",
            "role": role.value,
            "evidence": [f"{role.value} evidence"],
            "candidate_preference": "A",
            "confidence": 0.7,
            "tool_calls": [],
            "tool_summaries": [],
        }
    )
    llm = ScriptedLLM([round1, round2])
    agent = HeterogeneousAgent(llm, prompts, tools, max_tool_rounds=3)
    ev, n = agent.run(sample, role, profile)
    assert n == 1
    assert ev.role == role
    assert tool_name in ev.tool_summaries[0]
    llm.assert_consumed()


def test_integration_no_tools_final_answer(prompts):
    sample = _sample_univariate()
    # Build fake upstream
    from ts_agent.schemas.models import AgentPlan, ScaleObservation, TaskEvidence

    plan = AgentPlan(
        reasoning="r",
        capability="feature_analysis",
        scope="overall",
        univariate=True,
        scales=[ScaleName.SHORT],
        heterogeneous_agents=[HeterogeneousRole.STRUCTURE],
    )
    profile = build_temporal_profile(
        [
            ScaleObservation(
                reasoning="r",
                scale=ScaleName.SHORT,
                observations=["local rise"],
                confidence=0.6,
            )
        ]
    )
    evidences = [
        TaskEvidence(
            reasoning="r",
            role=HeterogeneousRole.STRUCTURE,
            evidence=["upward slope from describe_series"],
            candidate_preference="A",
            confidence=0.75,
        )
    ]
    final = json.dumps(
        {
            "reasoning": "Profile and structure evidence agree on upward trend.",
            "answer": "A",
            "explanation": "Series shows positive slope.",
            "confidence": 0.8,
            "conflicts": [],
            "cited_evidence": ["local rise", "upward slope from describe_series"],
        }
    )
    llm = ScriptedLLM([final])
    agent = IntegrationAgent(llm, prompts)
    ans = agent.run(sample, plan, profile, evidences)
    assert ans.answer == "A"
    assert ans.cited_evidence
    text = _joined(llm.calls[0])
    _has_tags(text, ["question", "candidates", "plan", "temporal_profile", "task_evidence"])
    assert "do NOT call tools" in prompts.get("integration_v1")["system"]
    # Integration must not expose tool catalog
    assert "<tool_catalog>" not in text
    llm.assert_consumed()


def test_baseline_extracts_choice_letter(prompts):
    sample = _sample_univariate()
    raw = (
        "<thinking_process>\nTrend is upward.\n</thinking_process>\n"
        "<final_answer>\nA\n</final_answer>"
    )
    llm = ScriptedLLM([raw])
    agent = BaselineAgent(llm, prompts)
    pred, full = agent.run(sample)
    assert pred == "A"
    assert "final_answer" in full
    text = _joined(llm.calls[0])
    _has_tags(text, ["question", "timeseries", "candidates"])
    llm.assert_consumed()


def test_build_temporal_profile_aggregates_scales():
    from ts_agent.schemas.models import ScaleObservation

    obs = [
        ScaleObservation(reasoning="r", scale=ScaleName.SHORT, observations=["short ok"], confidence=0.5),
        ScaleObservation(reasoning="r", scale=ScaleName.MEDIUM, observations=["medium ok"], confidence=0.5),
        ScaleObservation(reasoning="r", scale=ScaleName.LONG, observations=["long ok"], confidence=0.5),
    ]
    profile = build_temporal_profile(obs)
    assert profile.short is not None and profile.medium is not None and profile.long is not None
    assert "short ok" in profile.summary
    assert profile.conflicts == []
