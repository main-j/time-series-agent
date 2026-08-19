"""Goal-driven tool contracts and planner assignment sanitization."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from ts_agent.agents.roles import PlannerAgent
from ts_agent.core.llm import LLMProvider, LLMResponse
from ts_agent.prompts.library import PromptLibrary
from ts_agent.schemas.models import HeterogeneousRole, MMTSSample, ScaleName, SubsetName
from ts_agent.tools.registry import build_default_registry


ROOT = Path(__file__).resolve().parents[1]


class ScriptedLLM(LLMProvider):
    def __init__(self, scripts: List[str]):
        self.scripts = list(scripts)
        self.calls: List[List[Dict[str, str]]] = []
        self.idx = 0

    def generate(self, messages: List[Dict[str, str]], **kwargs: Any) -> LLMResponse:
        self.calls.append(messages)
        text = self.scripts[self.idx]
        self.idx += 1
        return LLMResponse(text=text, raw={"scripted": True})


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


def test_catalog_exposes_complete_contracts_without_keyword_binding():
    reg = build_default_registry()
    catalog = reg.catalog_text(["structure"])
    assert "returns:" in catalog
    assert "use_when:" in catalog
    assert "avoid_when:" in catalog
    assert "limitations:" in catalog
    assert "Select tools by matching your required measurements" in catalog
    for spec in reg.list_for_roles(["short", "medium", "long", "structure", "matching", "alignment"]):
        assert spec.description
        assert spec.input_schema
        assert spec.output_schema
        assert spec.use_when
        assert spec.avoid_when
        assert spec.limitations


def test_planner_preserves_assignments_and_strips_tool_name_notes():
    prompts = PromptLibrary(ROOT / "prompts")
    sample = _sample_univariate()
    plan_json = json.dumps(
        {
            "reasoning": "Need seasonal period evidence.",
            "task_summary": "Measure seasonal period length.",
            "target_output": "Return one numerical period.",
            "answer_type": "numerical",
            "capability": "feature_analysis",
            "scope": "overall",
            "univariate": True,
            "homo_assignments": [
                {
                    "scale": "medium",
                    "objective": "Estimate mid-scale periodicity.",
                    "required_measurements": ["seasonal_period"],
                    "validation_requirements": ["Reject period equal to series length without validation."],
                }
            ],
            "hetero_assignments": [
                {
                    "role": "structure",
                    "objective": "Reconcile period estimates.",
                    "required_measurements": ["seasonal_period", "seasonal_strength"],
                    "validation_requirements": ["Cross-check weak spectral peaks."],
                }
            ],
            "notes": "use fft_period on the full series.",
        }
    )
    plan = PlannerAgent(ScriptedLLM([plan_json]), prompts).run(sample)
    assert plan.scales == [ScaleName.MEDIUM]
    assert plan.heterogeneous_agents == [HeterogeneousRole.STRUCTURE]
    assert plan.homo_assignments[0].required_measurements == ["seasonal_period"]
    assert "fft_period" not in (plan.notes or "")
    assert "tool_names_stripped_from_notes" in plan.notes


def test_planner_inherits_homo_measurements_when_hetero_empty():
    prompts = PromptLibrary(ROOT / "prompts")
    sample = _sample_univariate()
    plan_json = json.dumps(
        {
            "reasoning": "Mid-scale periodicity is enough for homo; hetero must reconcile.",
            "task_summary": "Measure seasonal period length of Time Series 1.",
            "target_output": "Return one numerical period.",
            "answer_type": "numerical",
            "capability": "feature_analysis",
            "scope": "overall",
            "univariate": True,
            "homo_assignments": [
                {
                    "scale": "medium",
                    "objective": "Estimate mid-scale periodicity.",
                    "required_measurements": ["seasonal_period"],
                    "validation_requirements": ["Reject period equal to series length without validation."],
                }
            ],
            "hetero_assignments": [],
            "success_criteria": ["Cover seasonal_period with tool evidence."],
        }
    )
    plan = PlannerAgent(ScriptedLLM([plan_json]), prompts).run(sample)
    assert plan.scales == [ScaleName.MEDIUM]
    assert len(plan.hetero_assignments) == 1
    assert plan.hetero_assignments[0].role == HeterogeneousRole.STRUCTURE
    assert plan.hetero_assignments[0].required_measurements == ["seasonal_period"]
    assert "task_relevant_evidence" not in plan.hetero_assignments[0].required_measurements
    assert plan.hetero_assignments[0].objective == "Return one numerical period."
    assert any("series length" in req.lower() for req in plan.hetero_assignments[0].validation_requirements)


def test_planner_replaces_generic_hetero_measurements_with_homo():
    prompts = PromptLibrary(ROOT / "prompts")
    sample = _sample_univariate()
    plan_json = json.dumps(
        {
            "reasoning": "Need seasonal period evidence.",
            "task_summary": "Measure seasonal period length.",
            "target_output": "Return one numerical period.",
            "answer_type": "numerical",
            "capability": "feature_analysis",
            "scope": "overall",
            "univariate": True,
            "homo_assignments": [
                {
                    "scale": "medium",
                    "objective": "Estimate mid-scale periodicity.",
                    "required_measurements": ["seasonal_period"],
                    "validation_requirements": ["Cross-check weak spectral peaks."],
                }
            ],
            "hetero_assignments": [
                {
                    "role": "structure",
                    "objective": "Reconcile period estimates.",
                    "required_measurements": ["task_relevant_evidence"],
                    "validation_requirements": [],
                }
            ],
        }
    )
    plan = PlannerAgent(ScriptedLLM([plan_json]), prompts).run(sample)
    assert plan.hetero_assignments[0].required_measurements == ["seasonal_period"]
