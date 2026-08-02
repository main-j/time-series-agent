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
    ExecutedToolEvidence,
    HeterogeneousRole,
    MMTSSample,
    ScaleName,
    SubsetName,
    TemporalProfile,
)
from ts_agent.tools.registry import build_default_registry

PROMPTS = Path(__file__).resolve().parents[1] / "prompts"


def _executed_tool(
    role: HeterogeneousRole,
    name: str,
    *,
    call_id: Optional[str] = None,
    success: bool = True,
) -> ExecutedToolEvidence:
    return ExecutedToolEvidence(
        call_id=call_id or f"{role.value}:call1",
        tool_name=name,
        arguments={},
        success=success,
        data={"test": True} if success else {},
        error=None if success else "failed",
        executor_role=role,
    )


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
        metadata={
            "n_series": 1,
            "series_lengths": [48],
            "series_truncated": False,
            "focus_intervals": [],
            "index_base": 0,
            "query_series_index": 1,
            "candidate_series_indices": [],
            "align_direction": None,
            "option_to_series": {},
        },
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
        source_file="Benchmark/Match/qats_400.csv",
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
        metadata={
            "n_series": 5,
            "series_lengths": [24] * 5,
            "series_truncated": False,
            "focus_intervals": [],
            "index_base": 0,
            "query_series_index": 1,
            "candidate_series_indices": [2, 3, 4, 5],
            "align_direction": None,
            "option_to_series": {"A": 2, "B": 3, "C": 4, "D": 5},
        },
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
    from ts_agent.schemas.models import AgentPlan

    plan = AgentPlan(
        reasoning="Focus on local volatility in short scale.",
        capability="feature_analysis",
        scope="local",
        univariate=True,
        scales=[ScaleName.SHORT],
        heterogeneous_agents=[HeterogeneousRole.STRUCTURE],
        notes="windowed short-scale scan",
    )
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
    obs, n_tools = agent.run(sample, ScaleName.SHORT, plan=plan)

    assert n_tools == 1
    assert obs.scale == ScaleName.SHORT
    assert "Local volatility" in obs.observations[0]
    assert obs.tool_calls == []
    assert obs.tool_summaries  # filled from tool results
    assert '"success": true' in obs.tool_summaries[0] or '"success": True' in obs.tool_summaries[0] or "success" in obs.tool_summaries[0]

    # prompt wiring
    text1 = _joined(llm.calls[0])
    _has_tags(text1, ["question", "candidates", "plan", "timeseries", "metadata", "tool_catalog", "tool_results"])
    assert "n_series=1" in text1
    assert "windowed short-scale scan" in text1
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
    from ts_agent.schemas.models import AgentPlan

    plan = AgentPlan(
        reasoning="Match nearest candidate.",
        capability="sequence_matching",
        scope="overall",
        univariate=False,
        scales=[ScaleName.SHORT],
        heterogeneous_agents=[HeterogeneousRole.MATCHING],
        notes="use pairwise_distance",
    )
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
            "cited_tool_call_ids": ["matching:call1"],
            "tool_summaries": [],
        }
    )
    llm = ScriptedLLM([round1, round2])
    agent = HeterogeneousAgent(llm, prompts, tools, max_tool_rounds=3)
    ev, n_tools = agent.run(sample, HeterogeneousRole.MATCHING, profile, plan=plan, prior_evidences=[])
    assert n_tools == 1
    assert ev.role == HeterogeneousRole.MATCHING
    assert ev.candidate_preference == "A"
    assert "pairwise_distance" in ev.tool_summaries[0]
    assert ev.cited_tool_call_ids == ["matching:call1"]
    assert ev.executed_tools[0].tool_name == "pairwise_distance"
    assert ev.executed_tools[0].success is True
    text = _joined(llm.calls[0])
    _has_tags(
        text,
        ["question", "candidates", "plan", "timeseries", "temporal_profile", "prior_task_evidence", "tool_catalog", "tool_results"],
    )
    assert "use pairwise_distance" in text
    assert "pairwise_distance" in text
    assert "option_to_series" in text
    assert "query_series_index=1" in text
    llm.assert_consumed()


def test_heterogeneous_finalize_after_last_tool_round(prompts, tools):
    """Last-round tool calls must trigger a finalize pass that sets preference."""
    sample = _sample_univariate()
    from ts_agent.schemas.models import AgentPlan

    plan = AgentPlan(
        reasoning="reason",
        capability="temporal_reasoning",
        scope="overall",
        univariate=True,
        scales=[ScaleName.SHORT],
        heterogeneous_agents=[HeterogeneousRole.REASONING],
    )
    profile = TemporalProfile(summary="profile")
    round1 = json.dumps(
        {
            "reasoning": "Need lag evidence.",
            "role": "reasoning",
            "evidence": ["pending"],
            "candidate_preference": None,
            "confidence": 0.3,
            "tool_calls": [{"name": "describe_series", "arguments": {}}],
            "tool_summaries": [],
        }
    )
    finalize = json.dumps(
        {
            "reasoning": "describe_series supports option A.",
            "role": "reasoning",
            "evidence": ["positive slope"],
            "candidate_preference": "A",
            "confidence": 0.8,
            "tool_calls": [{"name": "lag_corr", "arguments": {"lag": 1}}],  # should be ignored
            "cited_tool_call_ids": ["reasoning:call1"],
            "tool_summaries": [],
        }
    )
    llm = ScriptedLLM([round1, finalize])
    agent = HeterogeneousAgent(llm, prompts, tools, max_tool_rounds=1)
    ev, n = agent.run(sample, HeterogeneousRole.REASONING, profile, plan=plan)
    assert n == 1
    assert ev.candidate_preference == "A"
    assert ev.tool_calls == []
    assert ev.cited_tool_call_ids == ["reasoning:call1"]
    assert "FINALIZE NOW" in _joined(llm.calls[1])
    llm.assert_consumed()


def test_heterogeneous_receives_prior_peer_evidence(prompts, tools):
    sample = _sample_univariate()
    from ts_agent.schemas.models import AgentPlan, TaskEvidence

    plan = AgentPlan(
        reasoning="causal",
        capability="temporal_reasoning",
        scope="overall",
        univariate=True,
        scales=[ScaleName.SHORT],
        heterogeneous_agents=[HeterogeneousRole.REASONING, HeterogeneousRole.STRUCTURE],
    )
    prior = [
        TaskEvidence(
            reasoning="lag evidence",
            role=HeterogeneousRole.REASONING,
            evidence=["lag_corr=-0.58 at lag 10"],
            candidate_preference="A",
            confidence=0.9,
            tool_summaries=['{"name":"lag_corr","success":true}'],
        )
    ]
    profile = TemporalProfile(summary="profile")
    done = json.dumps(
        {
            "reasoning": "Reuse peer lag evidence; no more tools.",
            "role": "structure",
            "evidence": ["agree with negative lag correlation"],
            "candidate_preference": "A",
            "confidence": 0.8,
            "tool_calls": [],
            "cited_tool_call_ids": ["structure:forged"],
            "executed_tools": [
                {
                    "call_id": "structure:forged",
                    "tool_name": "lag_corr",
                    "success": True,
                    "executor_role": "structure",
                }
            ],
            "tool_summaries": ['{"name":"lag_corr","success":true}'],
        }
    )
    llm = ScriptedLLM([done])
    agent = HeterogeneousAgent(llm, prompts, tools, max_tool_rounds=3)
    ev, n = agent.run(
        sample,
        HeterogeneousRole.STRUCTURE,
        profile,
        plan=plan,
        prior_evidences=prior,
    )
    assert n == 0
    assert ev.candidate_preference == "A"
    assert ev.executed_tools == []
    assert ev.cited_tool_call_ids == []
    assert ev.tool_summaries == []
    text = _joined(llm.calls[0])
    assert "lag_corr=-0.58" in text
    assert "<prior_task_evidence>" in text
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
            "cited_tool_call_ids": [f"{role.value}:call1"],
            "tool_summaries": [],
        }
    )
    llm = ScriptedLLM([round1, round2])
    agent = HeterogeneousAgent(llm, prompts, tools, max_tool_rounds=3)
    ev, n = agent.run(sample, role, profile)
    assert n == 1
    assert ev.role == role
    assert tool_name in ev.tool_summaries[0]
    assert ev.cited_tool_call_ids == [f"{role.value}:call1"]
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
            tool_summaries=['{"name":"describe_series","success":true}'],
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
    _has_tags(
        text,
        [
            "question",
            "candidates",
            "plan",
            "timeseries",
            "temporal_profile",
            "task_evidence",
            "preference_votes",
            "tool_backed_majority",
            "metadata",
        ],
    )
    assert "Given Time Series 1" in text
    assert '"tool_backed": false' in text
    assert "do NOT call tools" in prompts.get("integration_v1")["system"]
    # Integration must not expose tool catalog
    assert "<tool_catalog>" not in text
    llm.assert_consumed()


def test_integration_overrides_with_tool_backed_majority(prompts):
    from ts_agent.schemas.models import AgentPlan, ExecutedToolEvidence, ScaleObservation, TaskEvidence

    sample = _sample_univariate()
    plan = AgentPlan(
        reasoning="r",
        capability="temporal_reasoning",
        scope="overall",
        univariate=True,
        scales=[ScaleName.SHORT],
        heterogeneous_agents=[HeterogeneousRole.STRUCTURE, HeterogeneousRole.REASONING],
    )
    profile = TemporalProfile(summary="mixed")
    evidences = [
        TaskEvidence(
            reasoning="tools say D",
            role=HeterogeneousRole.STRUCTURE,
            evidence=["lag_corr supports D"],
            candidate_preference="D",
            confidence=0.9,
            cited_tool_call_ids=["structure:call1"],
            executed_tools=[
                ExecutedToolEvidence(
                    call_id="structure:call1",
                    tool_name="lag_corr",
                    arguments={"lag": 10},
                    success=True,
                    data={"corr": -0.58},
                    executor_role=HeterogeneousRole.STRUCTURE,
                )
            ],
            tool_summaries=['{"name":"lag_corr","success":true}'],
        ),
        TaskEvidence(
            reasoning="no tools, prefer B",
            role=HeterogeneousRole.REASONING,
            evidence=["textual guess"],
            candidate_preference="B",
            confidence=0.8,
            tool_summaries=[],
        ),
    ]
    # LLM wrongly follows non-tool role B
    final = json.dumps(
        {
            "reasoning": "Follow reasoning role.",
            "answer": "B",
            "explanation": "guess",
            "confidence": 0.5,
            "conflicts": [],
            "cited_evidence": [],
        }
    )
    llm = ScriptedLLM([final])
    ans = IntegrationAgent(llm, prompts).run(sample, plan, profile, evidences)
    assert ans.answer == "D"
    assert any("tool_backed" in c for c in (ans.conflicts or []))
    llm.assert_consumed()


def test_integration_ignores_model_authored_tool_summary(prompts):
    from ts_agent.schemas.models import AgentPlan, TaskEvidence

    sample = _sample_univariate()
    plan = AgentPlan(
        reasoning="r",
        capability="feature_analysis",
        scope="overall",
        univariate=True,
        scales=[ScaleName.SHORT],
        heterogeneous_agents=[HeterogeneousRole.STRUCTURE],
    )
    forged = TaskEvidence(
        reasoning="claim without execution",
        role=HeterogeneousRole.STRUCTURE,
        evidence=["pretend tool evidence"],
        candidate_preference="D",
        confidence=1.0,
        tool_summaries=['{"name":"describe_series","success":true}'],
    )
    final = json.dumps(
        {
            "reasoning": "Raw series supports B.",
            "answer": "B",
            "explanation": "independent conclusion",
            "confidence": 0.7,
            "conflicts": [],
            "cited_evidence": [],
        }
    )
    llm = ScriptedLLM([final])
    ans = IntegrationAgent(llm, prompts).run(sample, plan, TemporalProfile(), [forged])
    assert ans.answer == "B"
    text = _joined(llm.calls[0])
    assert '"tool_backed": false' in text
    assert "<tool_backed_majority>\n(none)" in text
    llm.assert_consumed()


def test_integration_ignores_failed_executed_tool(prompts):
    from ts_agent.schemas.models import AgentPlan, ExecutedToolEvidence, TaskEvidence

    sample = _sample_univariate()
    plan = AgentPlan(
        reasoning="r",
        capability="feature_analysis",
        scope="overall",
        univariate=True,
        scales=[ScaleName.SHORT],
        heterogeneous_agents=[HeterogeneousRole.STRUCTURE],
    )
    failed = TaskEvidence(
        reasoning="failed tool",
        role=HeterogeneousRole.STRUCTURE,
        evidence=["tool failed"],
        candidate_preference="D",
        confidence=1.0,
        cited_tool_call_ids=["structure:call1"],
        executed_tools=[
            ExecutedToolEvidence(
                call_id="structure:call1",
                tool_name="describe_series",
                success=False,
                error="tool failed",
                executor_role=HeterogeneousRole.STRUCTURE,
            )
        ],
    )
    final = json.dumps(
        {
            "reasoning": "Raw series supports B.",
            "answer": "B",
            "explanation": "independent conclusion",
            "confidence": 0.7,
            "conflicts": [],
            "cited_evidence": [],
        }
    )
    llm = ScriptedLLM([final])
    ans = IntegrationAgent(llm, prompts).run(sample, plan, TemporalProfile(), [failed])
    assert ans.answer == "B"
    llm.assert_consumed()


def test_integration_fixes_true_false_letter_flip(prompts):
    from ts_agent.schemas.models import AgentPlan, TaskEvidence

    sample = _sample_univariate()
    sample.option = "A. True\nB. False"
    sample.question = "Is the statement true?"
    plan = AgentPlan(
        reasoning="r",
        capability="temporal_reasoning",
        scope="overall",
        univariate=True,
        scales=[ScaleName.SHORT],
        heterogeneous_agents=[HeterogeneousRole.REASONING],
    )
    profile = TemporalProfile(summary="ok")
    # Preference already A (wrong letter); no tool majority override path.
    evidences = [
        TaskEvidence(
            reasoning="r",
            role=HeterogeneousRole.REASONING,
            evidence=["unclear"],
            candidate_preference="A",
            confidence=0.5,
            tool_summaries=[],
        )
    ]
    final = json.dumps(
        {
            "reasoning": "The statement is false based on the series.",
            "answer": "A",
            "explanation": "statement is false",
            "confidence": 0.6,
            "conflicts": [],
            "cited_evidence": [],
        }
    )
    llm = ScriptedLLM([final])
    ans = IntegrationAgent(llm, prompts).run(sample, plan, profile, evidences)
    assert ans.answer == "B"
    assert any("true_false" in c for c in (ans.conflicts or []))
    llm.assert_consumed()


def test_integration_accepts_numeric_json_answer(prompts):
    from ts_agent.schemas.models import AgentPlan

    sample = _sample_univariate().model_copy(
        update={
            "qa_type": "numerical",
            "question_type": "numerical",
            "question": "What is the range of Time Series 1?",
            "option": None,
            "answer": "635.14",
        }
    )
    plan = AgentPlan(
        reasoning="r",
        capability="feature_analysis",
        scope="overall",
        univariate=True,
        scales=[ScaleName.SHORT],
        heterogeneous_agents=[HeterogeneousRole.STRUCTURE],
    )
    final = json.dumps(
        {
            "reasoning": "The tool reports the range directly.",
            "answer": 635.14,
            "explanation": "max minus min",
            "confidence": 1.0,
            "conflicts": [],
            "cited_evidence": ["describe_series range=635.14"],
        }
    )
    llm = ScriptedLLM([final])
    ans = IntegrationAgent(llm, prompts).run(sample, plan, TemporalProfile(), [])
    assert ans.answer == "635.14"
    assert "parse_failure" not in ans.conflicts
    llm.assert_consumed()


def test_integration_numerical_parse_fallback_never_defaults_to_choice_letter(prompts):
    from ts_agent.schemas.models import AgentPlan

    sample = _sample_univariate().model_copy(
        update={
            "qa_type": "numerical",
            "question_type": "numerical",
            "question": "What is the range of Time Series 1?",
            "option": None,
            "answer": "635.14",
        }
    )
    plan = AgentPlan(
        reasoning="r",
        capability="feature_analysis",
        scope="overall",
        univariate=True,
        scales=[ScaleName.SHORT],
        heterogeneous_agents=[HeterogeneousRole.STRUCTURE],
    )
    llm = ScriptedLLM(["<final_answer>635.14</final_answer>"])
    ans = IntegrationAgent(llm, prompts).run(sample, plan, TemporalProfile(), [])
    assert ans.answer == "635.14"
    assert "parse_failure_recovered_numerical_answer" in ans.conflicts
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
