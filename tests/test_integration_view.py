"""IntegrationAssembler projection and cleanliness gates."""
from __future__ import annotations

import json

from ts_agent.agents.integration_view import assert_bundle_clean, assemble_integration_bundle
from ts_agent.schemas.models import (
    AgentPlan,
    ClaimObservation,
    EvidenceItem,
    ExecutedStep,
    HeterogeneousRole,
    MMTSSample,
    ScaleName,
    ScaleObservation,
    SubsetName,
    TaskEvidence,
    TemporalProfile,
)
from ts_agent.agents.roles import build_temporal_profile


def _sample():
    return MMTSSample(
        sample_id="int:view:0",
        source_file="sim.csv",
        row_index=0,
        subset=SubsetName.MATCH,
        question_type="choice",
        question="Which candidate matches?",
        option="A. TS2\nB. TS3\nC. TS4\nD. TS5",
        answer="A",
        series=[[1.0, 2.0], [2.0, 3.0]],
        series_text="Given Time Series 1: [1, 2]",
        metadata={
            "n_series": 2,
            "option_to_series": {"A": 2, "B": 3, "C": 4, "D": 5},
        },
    )


def test_assembler_strips_tool_dumps_and_maps_option():
    sample = _sample()
    plan = AgentPlan(
        reasoning="r",
        task_summary="match series",
        target_output="option letter",
        answer_type="choice",
        success_criteria=["map via option_to_series"],
        scales=[ScaleName.MEDIUM],
        heterogeneous_agents=[HeterogeneousRole.MATCHING],
    )
    obs = ScaleObservation(
        reasoning="r",
        scale=ScaleName.MEDIUM,
        observations=["seasonal_strength=0.62"],
        structured_observations=[
            ClaimObservation(
                claim="moderate seasonality",
                evidence=[
                    EvidenceItem(
                        type="seasonal_strength",
                        value=0.62,
                        call_id="medium:step2",
                        provenance="tool",
                        series_index=1,
                        args_fingerprint="abc",
                    )
                ],
                confidence="tool_supported",
                maps_to_measurement="seasonal_strength",
            )
        ],
        executed_steps=[
            ExecutedStep(
                call_id="medium:step2",
                step=2,
                tool_name="stl_strength",
                success=True,
                data={"series": [{"seasonal_strength": 0.62}]},
            )
        ],
    )
    profile = build_temporal_profile([obs])
    evidences = [
        TaskEvidence(
            reasoning="r",
            role=HeterogeneousRole.MATCHING,
            evidence=["nearest is series 2"],
            hypothesis="series 2 wins",
            candidate_preference="A",
            cited_tool_call_ids=["medium:step2"],
            tool_summaries=['{"name":"stl_strength","success":true}'],
            executed_tools=[],
        )
    ]
    bundle = assemble_integration_bundle(sample, plan, profile, evidences)
    assert_bundle_clean(bundle)
    raw = json.dumps(bundle.model_dump())
    assert "executed_tools" not in raw
    assert "tool_summaries" not in raw
    assert "args_fingerprint" not in raw
    assert bundle.execution_metadata.option_mapping["A"] == 2
    assert bundle.homo_perception.by_scale["medium"].states
    assert bundle.homo_perception.by_scale["medium"].states[0].type == "seasonal_strength"
    assert "call_id" not in json.dumps(bundle.homo_perception.model_dump())
    assert bundle.heter_reasoning.roles[0].grounded is True
    assert bundle.execution_metadata.verified_preference == "A"


def test_assembler_fallback_notes_when_no_structured():
    sample = _sample()
    plan = AgentPlan(reasoning="r", task_summary="t", scales=[ScaleName.SHORT])
    profile = build_temporal_profile(
        [ScaleObservation(reasoning="r", scale=ScaleName.SHORT, observations=["local rise"])]
    )
    bundle = assemble_integration_bundle(sample, plan, profile, [])
    assert bundle.homo_perception.by_scale["short"].states[0].type == "note"
    assert bundle.homo_perception.by_scale["short"].states[0].trusted is False
