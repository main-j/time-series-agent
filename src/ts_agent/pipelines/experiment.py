from __future__ import annotations

import time
from typing import Any, Dict, List

from ts_agent.agents.roles import (
    BaselineAgent,
    HeterogeneousAgent,
    HomogeneousAgent,
    IntegrationAgent,
    PlannerAgent,
    build_temporal_profile,
)
from ts_agent.core.llm import LLMProvider
from ts_agent.prompts.library import PromptLibrary
from ts_agent.schemas.models import HeterogeneousRole, MMTSSample, RunTrace, ScaleName
from ts_agent.tools.registry import ToolRegistry, build_default_registry


class ExperimentPipeline:
    def __init__(self, llm: LLMProvider, prompt_dir: str, max_tool_rounds: int = 3):
        self.llm = llm
        self.prompts = PromptLibrary(prompt_dir)
        self.tools: ToolRegistry = build_default_registry()
        self.planner = PlannerAgent(llm, self.prompts)
        self.homo = HomogeneousAgent(llm, self.prompts, self.tools, max_tool_rounds=max_tool_rounds)
        self.hetero = HeterogeneousAgent(llm, self.prompts, self.tools, max_tool_rounds=max_tool_rounds)
        self.integration = IntegrationAgent(llm, self.prompts)
        self.baseline = BaselineAgent(llm, self.prompts)

    def run_baseline(self, sample: MMTSSample) -> RunTrace:
        self.llm.reset_stats()
        t0 = time.time()
        try:
            pred, raw = self.baseline.run(sample)
            return RunTrace(
                sample_id=sample.sample_id,
                experiment="baseline",
                success=bool(pred),
                predicted_answer=pred,
                ground_truth=sample.answer,
                question_type=sample.question_type,
                latency_sec=time.time() - t0,
                model_calls=self.llm.call_count,
                tool_calls=0,
                prompt_tokens=self.llm.total_prompt_tokens,
                completion_tokens=self.llm.total_completion_tokens,
                details={"raw": raw, "subset": sample.subset.value, "task_type": sample.task_type},
            )
        except Exception as e:  # noqa: BLE001
            return RunTrace(
                sample_id=sample.sample_id,
                experiment="baseline",
                success=False,
                ground_truth=sample.answer,
                question_type=sample.question_type,
                latency_sec=time.time() - t0,
                error=str(e),
            )

    def run_architecture(self, sample: MMTSSample) -> RunTrace:
        self.llm.reset_stats()
        t0 = time.time()
        tool_calls = 0
        try:
            plan = self.planner.run(sample)
            scales = plan.scales or [ScaleName.SHORT, ScaleName.MEDIUM, ScaleName.LONG]
            observations = []
            for scale in scales:
                obs, c = self.homo.run(sample, scale)
                observations.append(obs)
                tool_calls += c
            profile = build_temporal_profile(observations)
            roles = plan.heterogeneous_agents or [HeterogeneousRole.STRUCTURE]
            evidences = []
            for role in roles:
                ev, c = self.hetero.run(sample, role, profile)
                evidences.append(ev)
                tool_calls += c
            final = self.integration.run(sample, plan, profile, evidences)
            return RunTrace(
                sample_id=sample.sample_id,
                experiment="architecture",
                success=bool(final.answer),
                predicted_answer=str(final.answer),
                ground_truth=sample.answer,
                question_type=sample.question_type,
                latency_sec=time.time() - t0,
                model_calls=self.llm.call_count,
                tool_calls=tool_calls,
                prompt_tokens=self.llm.total_prompt_tokens,
                completion_tokens=self.llm.total_completion_tokens,
                details={
                    "plan": plan.model_dump(),
                    "temporal_profile": profile.model_dump(),
                    "evidences": [e.model_dump() for e in evidences],
                    "final": final.model_dump(),
                    "subset": sample.subset.value,
                    "task_type": sample.task_type,
                    "prompt_versions": self.prompts.versions(),
                },
            )
        except Exception as e:  # noqa: BLE001
            return RunTrace(
                sample_id=sample.sample_id,
                experiment="architecture",
                success=False,
                ground_truth=sample.answer,
                question_type=sample.question_type,
                latency_sec=time.time() - t0,
                model_calls=self.llm.call_count,
                tool_calls=tool_calls,
                prompt_tokens=self.llm.total_prompt_tokens,
                completion_tokens=self.llm.total_completion_tokens,
                error=str(e),
            )
