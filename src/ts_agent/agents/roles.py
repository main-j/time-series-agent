from __future__ import annotations

import json
from typing import Any, Dict, List, Optional, Tuple

from ts_agent.core.llm import LLMProvider
from ts_agent.core.utils import extract_final_answer_letter, extract_numerical_answer, parse_model
from ts_agent.prompts.library import PromptLibrary
from ts_agent.schemas.models import (
    AgentPlan,
    FinalAnswer,
    HeterogeneousRole,
    MMTSSample,
    ScaleName,
    ScaleObservation,
    TaskEvidence,
    TemporalProfile,
)
from ts_agent.tools.registry import ToolRegistry, ToolResult


def _candidates(sample: MMTSSample) -> str:
    return sample.option or "(numerical question: no options)"


class ToolLoopMixin:
    def __init__(self, llm: LLMProvider, prompts: PromptLibrary, tools: ToolRegistry, max_tool_rounds: int = 3):
        self.llm = llm
        self.prompts = prompts
        self.tools = tools
        self.max_tool_rounds = max_tool_rounds

    def _run_tools(self, calls: List[Dict[str, Any]], series: List[List[float]], allowed_roles: List[str]) -> Tuple[List[ToolResult], int]:
        results: List[ToolResult] = []
        allowed = {s.name for s in self.tools.list_for_roles(allowed_roles)}
        count = 0
        for call in calls:
            name = call.get("name")
            if name not in allowed:
                results.append(ToolResult(name=str(name), success=False, data={}, error=f"Tool not allowed for roles {allowed_roles}"))
                continue
            res = self.tools.run(name, call.get("arguments") or {}, series)
            results.append(res)
            count += 1
        return results, count

    @staticmethod
    def _tool_results_text(results: List[ToolResult]) -> str:
        if not results:
            return "(none)"
        return json.dumps([r.__dict__ for r in results], ensure_ascii=False, indent=2)


class PlannerAgent:
    def __init__(self, llm: LLMProvider, prompts: PromptLibrary):
        self.llm = llm
        self.prompts = prompts

    @staticmethod
    def _sanitize_plan(sample: MMTSSample, plan: AgentPlan) -> AgentPlan:
        """Deterministic subset/task routing guards (MMTS labels are trusted)."""
        subset = sample.subset.value
        task = str(sample.task_type or "").lower()
        roles = list(plan.heterogeneous_agents or [])

        def ensure(role: HeterogeneousRole) -> None:
            if role not in roles:
                roles.append(role)

        def drop(role: HeterogeneousRole) -> None:
            while role in roles:
                roles.remove(role)

        if subset == "Align" or "caption" in task:
            plan.capability = "cross_modal_alignment"
            ensure(HeterogeneousRole.ALIGNMENT)
            drop(HeterogeneousRole.MATCHING)
            if not roles:
                roles = [HeterogeneousRole.ALIGNMENT, HeterogeneousRole.STRUCTURE]
        elif subset == "Match" or any(k in task for k in ["choose it", "find it", "reverse", "smooth it"]):
            plan.capability = "sequence_matching"
            ensure(HeterogeneousRole.MATCHING)
            drop(HeterogeneousRole.ALIGNMENT)
            if not roles:
                roles = [HeterogeneousRole.MATCHING]
        elif any(k in task for k in ["causal", "inductive", "deductive", "counterfactual", "analog"]):
            ensure(HeterogeneousRole.REASONING)
            if HeterogeneousRole.STRUCTURE not in roles:
                ensure(HeterogeneousRole.STRUCTURE)

        if not roles:
            roles = [HeterogeneousRole.STRUCTURE, HeterogeneousRole.REASONING]
        if not plan.scales:
            plan.scales = [ScaleName.SHORT, ScaleName.MEDIUM, ScaleName.LONG]

        plan.heterogeneous_agents = roles
        return plan

    def run(self, sample: MMTSSample) -> AgentPlan:
        rendered = self.prompts.render(
            "planner_v1",
            question=sample.question,
            candidates=_candidates(sample),
            subset=sample.subset.value,
            local_overall=sample.local_overall,
            task_type=sample.task_type,
            domain=sample.domain,
            is_univariate=sample.is_univariate,
            qa_type=sample.qa_type,
        )
        messages = [
            {"role": "system", "content": rendered["system"]},
            {"role": "user", "content": rendered["user"]},
        ]
        resp = self.llm.generate(messages)
        try:
            plan = parse_model(resp.text, AgentPlan)
        except Exception:
            # fallback heuristic routing
            text = (sample.question + " " + str(sample.task_type)).lower()
            roles = []
            if sample.subset.value == "Align" or any(k in text for k in ["caption", "description", "semantic", "correspond"]):
                roles.append(HeterogeneousRole.ALIGNMENT)
            elif sample.subset.value == "Match" or any(k in text for k in ["match", "similar", "choose it", "find it", "reverse", "smooth"]):
                roles.append(HeterogeneousRole.MATCHING)
            if any(k in text for k in ["causal", "inductive", "deductive", "counterfactual", "analog"]):
                roles.append(HeterogeneousRole.REASONING)
            if not roles:
                roles = [HeterogeneousRole.STRUCTURE, HeterogeneousRole.REASONING]
            plan = AgentPlan(
                reasoning="Fallback heuristic plan due to parse failure.",
                capability="unknown",
                scope="overall" if sample.local_overall == "overall" else "local",
                univariate=sample.is_univariate,
                scales=[ScaleName.SHORT, ScaleName.MEDIUM, ScaleName.LONG],
                heterogeneous_agents=roles,
                notes=f"parse_error_raw={resp.text[:200]}",
            )
        return self._sanitize_plan(sample, plan)


class HomogeneousAgent(ToolLoopMixin):
    def run(self, sample: MMTSSample, scale: ScaleName) -> Tuple[ScaleObservation, int]:
        tool_results: List[ToolResult] = []
        tool_count = 0
        obs: Optional[ScaleObservation] = None
        for _ in range(self.max_tool_rounds):
            rendered = self.prompts.render(
                "homogeneous_v1",
                scale=scale.value,
                question=sample.question,
                series_text=sample.series_text,
                subset=sample.subset.value,
                local_overall=sample.local_overall,
                task_type=sample.task_type,
                domain=sample.domain,
                tool_catalog=self.tools.catalog_text([scale.value]),
                tool_results=self._tool_results_text(tool_results),
            )
            messages = [
                {"role": "system", "content": rendered["system"]},
                {"role": "user", "content": rendered["user"]},
            ]
            resp = self.llm.generate(messages)
            try:
                obs = parse_model(resp.text, ScaleObservation)
            except Exception:
                obs = ScaleObservation(
                    reasoning="Parse failure; using describe_series fallback.",
                    scale=scale,
                    observations=["Unable to parse model observation."],
                    tool_calls=[{"name": "describe_series", "arguments": {}}],
                )
            obs.scale = scale
            if not obs.tool_calls:
                break
            calls = [c.model_dump() if hasattr(c, "model_dump") else c for c in obs.tool_calls]
            new_results, c = self._run_tools(calls, sample.series, [scale.value])
            tool_results.extend(new_results)
            tool_count += c
            obs.tool_summaries = [json.dumps(r.__dict__, ensure_ascii=False) for r in new_results]
            # Continue so the model can interpret newly obtained tool evidence.
            continue
        assert obs is not None
        if not obs.tool_summaries and tool_results:
            obs.tool_summaries = [json.dumps(r.__dict__, ensure_ascii=False) for r in tool_results]
        return obs, tool_count


class HeterogeneousAgent(ToolLoopMixin):
    def run(self, sample: MMTSSample, role: HeterogeneousRole, profile: TemporalProfile) -> Tuple[TaskEvidence, int]:
        tool_results: List[ToolResult] = []
        tool_count = 0
        evidence: Optional[TaskEvidence] = None
        for _ in range(self.max_tool_rounds):
            rendered = self.prompts.render(
                "heterogeneous_v1",
                role=role.value,
                question=sample.question,
                candidates=_candidates(sample),
                series_text=sample.series_text,
                temporal_profile=profile.model_dump_json(),
                tool_catalog=self.tools.catalog_text([role.value]),
                tool_results=self._tool_results_text(tool_results),
            )
            messages = [
                {"role": "system", "content": rendered["system"]},
                {"role": "user", "content": rendered["user"]},
            ]
            resp = self.llm.generate(messages)
            try:
                evidence = parse_model(resp.text, TaskEvidence)
            except Exception:
                evidence = TaskEvidence(
                    reasoning="Parse failure",
                    role=role,
                    evidence=["parse failure"],
                    candidate_preference="A",
                    tool_calls=[],
                )
            evidence.role = role
            if not evidence.tool_calls:
                break
            calls = [c.model_dump() if hasattr(c, "model_dump") else c for c in evidence.tool_calls]
            new_results, c = self._run_tools(calls, sample.series, [role.value])
            tool_results.extend(new_results)
            tool_count += c
            evidence.tool_summaries = [json.dumps(r.__dict__, ensure_ascii=False) for r in new_results]
        assert evidence is not None
        if not evidence.tool_summaries and tool_results:
            evidence.tool_summaries = [json.dumps(r.__dict__, ensure_ascii=False) for r in tool_results]
        return evidence, tool_count


class IntegrationAgent:
    def __init__(self, llm: LLMProvider, prompts: PromptLibrary):
        self.llm = llm
        self.prompts = prompts

    def run(
        self,
        sample: MMTSSample,
        plan: AgentPlan,
        profile: TemporalProfile,
        evidences: List[TaskEvidence],
    ) -> FinalAnswer:
        rendered = self.prompts.render(
            "integration_v1",
            question=sample.question,
            candidates=_candidates(sample),
            question_type=sample.question_type,
            plan=plan.model_dump_json(),
            temporal_profile=profile.model_dump_json(),
            task_evidence=json.dumps([e.model_dump() for e in evidences], ensure_ascii=False),
        )
        messages = [
            {"role": "system", "content": rendered["system"]},
            {"role": "user", "content": rendered["user"]},
        ]
        resp = self.llm.generate(messages)
        try:
            ans = parse_model(resp.text, FinalAnswer)
        except Exception:
            # vote by candidate preferences
            prefs = [e.candidate_preference for e in evidences if e.candidate_preference]
            answer = prefs[0] if prefs else "A"
            ans = FinalAnswer(reasoning="Parse failure; used preference vote.", answer=str(answer), explanation="fallback")
        if sample.question_type == "choice":
            letter = extract_final_answer_letter(ans.answer) or extract_final_answer_letter(ans.explanation)
            if letter:
                ans.answer = letter
            else:
                ans.answer = ans.answer.strip()[:1].upper() if ans.answer else "A"
        return ans


class BaselineAgent:
    def __init__(self, llm: LLMProvider, prompts: PromptLibrary):
        self.llm = llm
        self.prompts = prompts

    def run(self, sample: MMTSSample) -> Tuple[str, str]:
        rendered = self.prompts.render(
            "baseline_v1",
            question=sample.question,
            series_text=sample.series_text,
            candidates=_candidates(sample),
        )
        messages = [
            {"role": "system", "content": rendered["system"]},
            {"role": "user", "content": rendered["user"]},
        ]
        resp = self.llm.generate(messages)
        if sample.question_type == "numerical":
            pred = extract_numerical_answer(resp.text) or ""
        else:
            pred = extract_final_answer_letter(resp.text) or ""
        return pred, resp.text


def build_temporal_profile(observations: List[ScaleObservation]) -> TemporalProfile:
    profile = TemporalProfile()
    by_scale = {o.scale: o for o in observations}
    profile.short = by_scale.get(ScaleName.SHORT)
    profile.medium = by_scale.get(ScaleName.MEDIUM)
    profile.long = by_scale.get(ScaleName.LONG)
    texts = []
    for o in observations:
        texts.extend(o.observations)
    # naive conflict: contradictory stationary statements
    joined = " | ".join(texts).lower()
    conflicts = []
    if "stationary" in joined and "non-stationary" in joined:
        conflicts.append("Conflicting stationarity observations across scales.")
    profile.conflicts = conflicts
    profile.summary = " ".join(texts)[:2000]
    return profile
