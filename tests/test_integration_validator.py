"""IntegrationValidator cite trust, mapping, and post override."""
from __future__ import annotations

import json

from ts_agent.agents.integration_validator import (
    build_execution_metadata,
    collect_homo_success_call_ids,
    invert_option_mapping,
    post_validate_answer,
    pre_validate_role,
)
from ts_agent.agents.integration_view import assemble_integration_bundle
from ts_agent.schemas.models import (
    AgentPlan,
    ExecutedStep,
    ExecutedToolEvidence,
    ExecutionMetadata,
    FinalAnswer,
    HeterogeneousRole,
    HeterRoleReasoning,
    MMTSSample,
    ScaleName,
    ScaleObservation,
    SubsetName,
    TaskEvidence,
    TemporalProfile,
)
from ts_agent.agents.roles import IntegrationAgent, build_temporal_profile
from ts_agent.core.llm import LLMProvider, LLMResponse
from ts_agent.prompts.library import PromptLibrary
from pathlib import Path

PROMPTS = Path(__file__).resolve().parents[1] / "prompts"


def _sample():
    return MMTSSample(
        sample_id="int:val:0",
        source_file="sim.csv",
        row_index=0,
        subset=SubsetName.BASE,
        question_type="choice",
        question="Trend?",
        option="A. up\nB. down\nC. flat\nD. seasonal",
        answer="A",
        series=[[1.0, 2.0, 3.0]],
        series_text="ts",
        metadata={"option_to_series": {"A": 2, "B": 3}},
    )


def test_forged_cite_not_grounded():
    ev = TaskEvidence(
        reasoning="forge",
        role=HeterogeneousRole.STRUCTURE,
        evidence=["pretend"],
        candidate_preference="D",
        cited_tool_call_ids=["structure:call99"],
        tool_summaries=['{"success":true}'],
    )
    view, warnings = pre_validate_role(ev, homo_success_ids=set())
    assert view.grounded is False
    assert any("unverified_cite" in w for w in warnings)


def test_upstream_homo_cite_grounded():
    homo_ids = {"medium:step2"}
    ev = TaskEvidence(
        reasoning="use homo",
        role=HeterogeneousRole.STRUCTURE,
        evidence=["strength"],
        candidate_preference="B",
        cited_tool_call_ids=["medium:step2"],
    )
    view, _ = pre_validate_role(ev, homo_success_ids=homo_ids)
    assert view.grounded is True


def test_invert_option_mapping():
    assert invert_option_mapping({"A": 2, "B": 3}, 3) == "B"
    assert invert_option_mapping({"A": 2}, 9) is None


def test_waveform_hint_maps_to_verified_preference():
    sample = _sample().model_copy(
        update={
            "question": "What type of waveform does the Time Series 1 most resemble?",
            "option": "A) Sine.\nB) Square.\nC) Triangle.\nD) Sawtooth.",
        }
    )
    profile = TemporalProfile(
        long=ScaleObservation(
            reasoning="shape",
            scale=ScaleName.LONG,
            observations=["square-like"],
            executed_steps=[
                ExecutedStep(
                    call_id="long:step1",
                    step=1,
                    tool_name="waveform_features",
                    success=True,
                    data={"waveform_hint": "square", "jump_ratio": 0.05},
                )
            ],
        )
    )
    meta = build_execution_metadata(sample, profile, [], [])
    assert meta.verified_preference == "B"
    assert any("waveform_hint_mapped" in w for w in (meta.warnings or []))


def test_post_override_with_verified_preference():
    sample = _sample()
    meta = build_execution_metadata(
        sample,
        TemporalProfile(),
        [
            TaskEvidence(
                reasoning="tools",
                role=HeterogeneousRole.STRUCTURE,
                evidence=["ok"],
                candidate_preference="D",
                confidence=0.9,
                cited_tool_call_ids=["structure:call1"],
                executed_tools=[
                    ExecutedToolEvidence(
                        call_id="structure:call1",
                        tool_name="lag_corr",
                        success=True,
                        data={},
                        executor_role=HeterogeneousRole.STRUCTURE,
                    )
                ],
            )
        ],
        [
            HeterRoleReasoning(
                role="structure",
                candidate_preference="D",
                grounded=True,
                confidence=0.9,
            )
        ],
    )
    assert meta.verified_preference == "D"
    ans = FinalAnswer(reasoning="follow B", answer="B", explanation="x")
    roles = [HeterRoleReasoning(role="structure", candidate_preference="D", grounded=True)]
    out = post_validate_answer(sample, ans, meta, roles)
    assert out.answer == "D"
    assert any("tool_backed" in c for c in (out.conflicts or []))


def test_integration_prompt_architecture_gates():
    prompts = PromptLibrary(PROMPTS)
    system = prompts.get("integration_v1")["system"]
    assert len(system) < 2500
    assert "call_id" not in system
    assert "option_to_series" not in system
    assert "do NOT call tools" in system
    assert "decision_trace" in system
    assert "qualitative" in system.lower() or "strong/weak" in system
    user = prompts.get("integration_v1")["user"]
    assert "planner_intent" in user
    assert "homo_perception" in user
    assert "heter_reasoning" in user
    assert "execution_metadata" in user
    assert "preference_votes" not in user
    assert "tool_backed_majority" not in user
    assert "timeseries" not in user


def test_final_answer_accepts_decision_trace():
    ans = FinalAnswer(
        reasoning="compare",
        answer="A",
        decision_trace={
            "metric": "seasonal_strength",
            "observed_value": 0.704,
            "intervals_from_question": ["0.5-0.8 moderate", ">0.8 strong"],
            "matched_label": "moderate",
            "matched_letter": "B",
        },
    )
    assert ans.decision_trace is not None
    assert ans.decision_trace.matched_letter == "B"


def test_post_validate_prefers_decision_trace_letter_over_answer():
    sample = _sample().model_copy(
        update={
            "option": "A) strong\nB) moderate\nC) weak\nD) none",
        }
    )
    ans = FinalAnswer(
        reasoning="mis-said strong",
        answer="A",
        decision_trace={
            "metric": "seasonal_strength",
            "observed_value": 0.704,
            "intervals_from_question": ["0.5-0.8 moderate"],
            "matched_label": "moderate",
            "matched_letter": "B",
        },
    )
    meta = ExecutionMetadata(verified_preference=None, verified=False)
    out = post_validate_answer(sample, ans, meta, [])
    assert out.answer == "B"
    assert any("decision_trace" in c for c in (out.conflicts or []))


class ScriptedLLM(LLMProvider):
    def __init__(self, scripts):
        super().__init__()
        self.scripts = list(scripts)
        self.idx = 0
        self.calls = []

    def generate(self, messages, **kwargs):
        self.calls.append(messages)
        text = self.scripts[min(self.idx, len(self.scripts) - 1)]
        self.idx += 1
        return LLMResponse(text=text, raw={})


def test_integration_agent_four_layer_user_tags():
    sample = _sample()
    plan = AgentPlan(reasoning="r", task_summary="trend", scales=[ScaleName.SHORT])
    profile = build_temporal_profile(
        [ScaleObservation(reasoning="r", scale=ScaleName.SHORT, observations=["up"])]
    )
    evidences = [
        TaskEvidence(
            reasoning="r",
            role=HeterogeneousRole.STRUCTURE,
            evidence=["up"],
            candidate_preference="A",
        )
    ]
    final = json.dumps(
        {
            "reasoning": "ok",
            "answer": "A",
            "explanation": "up",
            "confidence": 0.7,
            "conflicts": [],
            "cited_evidence": ["up"],
        }
    )
    llm = ScriptedLLM([final])
    ans = IntegrationAgent(llm, PromptLibrary(PROMPTS)).run(sample, plan, profile, evidences)
    assert ans.answer == "A"
    text = "\n".join(m["content"] for m in llm.calls[0])
    assert "<planner_intent>" in text
    assert "<homo_perception>" in text
    assert "<heter_reasoning>" in text
    assert "<execution_metadata>" in text
    assert "<preference_votes>" not in text
    assert "Given Time Series" not in text
