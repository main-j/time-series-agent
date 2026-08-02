from __future__ import annotations

import json
import re
from typing import Any, Dict, List, Optional, Sequence, Tuple

from ts_agent.core.llm import LLMProvider
from ts_agent.core.utils import extract_final_answer_letter, extract_numerical_answer, parse_model
from ts_agent.prompts.library import PromptLibrary
from ts_agent.schemas.models import (
    AgentPlan,
    ExecutedToolEvidence,
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


def _plan_text(plan: Optional[AgentPlan]) -> str:
    if plan is None:
        return "(none)"
    return plan.model_dump_json()


def _prior_evidence_text(evidences: Optional[Sequence[TaskEvidence]]) -> str:
    if not evidences:
        return "(none)"
    payload = []
    for e in evidences:
        item = e.model_dump()
        summaries = item.get("tool_summaries") or []
        if len(summaries) > 6:
            item["tool_summaries"] = summaries[:6] + [f"... ({len(summaries) - 6} more)"]
        payload.append(item)
    return json.dumps(payload, ensure_ascii=False, indent=2)


def _sample_context(sample: MMTSSample) -> Dict[str, Any]:
    """Structured MMTS context shared across Planner/Homo/Hetero/Integration."""
    md = dict(sample.metadata or {})
    n_series = int(md.get("n_series") or len(sample.series))
    lengths = md.get("series_lengths") or [len(s) for s in sample.series]
    focus = md.get("focus_intervals") or []
    return {
        "subset": sample.subset.value,
        "local_overall": sample.local_overall,
        "task_type": sample.task_type,
        "domain": sample.domain,
        "is_univariate": sample.is_univariate if sample.is_univariate is not None else (n_series <= 1),
        "qa_type": sample.qa_type,
        "question_type": sample.question_type,
        "n_series": n_series,
        "series_lengths": lengths,
        "index_base": md.get("index_base", 0),
        "series_truncated": bool(md.get("series_truncated", False)),
        "focus_intervals": focus,
        "query_series_index": md.get("query_series_index"),
        "candidate_series_indices": md.get("candidate_series_indices") or [],
        "align_direction": md.get("align_direction"),
        "option_to_series": md.get("option_to_series") or {},
    }


def _context_metadata_text(sample: MMTSSample) -> str:
    ctx = _sample_context(sample)
    parts = [
        f"subset={ctx['subset']}",
        f"local_overall={ctx['local_overall']}",
        f"task_type={ctx['task_type']}",
        f"domain={ctx['domain']}",
        f"qa_type={ctx['qa_type']}",
        f"question_type={ctx['question_type']}",
        f"is_univariate={ctx['is_univariate']}",
        f"n_series={ctx['n_series']}",
        f"series_lengths={ctx['series_lengths']}",
        f"index_base={ctx['index_base']}",
        f"series_truncated={ctx['series_truncated']}",
        f"focus_intervals={ctx['focus_intervals']}",
        f"query_series_index={ctx['query_series_index']}",
        f"candidate_series_indices={ctx['candidate_series_indices']}",
        f"align_direction={ctx['align_direction']}",
        f"option_to_series={ctx['option_to_series']}",
    ]
    return "; ".join(parts)


def _preference_vote_text(evidences: Sequence[TaskEvidence]) -> str:
    rows = []
    for e in evidences:
        verified_call_ids = _verified_tool_call_ids(e)
        tool_backed = bool(verified_call_ids)
        rows.append(
            {
                "role": e.role.value if hasattr(e.role, "value") else str(e.role),
                "candidate_preference": e.candidate_preference,
                "confidence": e.confidence,
                "tool_backed": tool_backed,
                "verified_tool_call_ids": sorted(verified_call_ids),
            }
        )
    return json.dumps(rows, ensure_ascii=False, indent=2)


def _verified_tool_call_ids(evidence: TaskEvidence) -> set[str]:
    successful = {record.call_id for record in evidence.executed_tools if record.success}
    return successful.intersection(evidence.cited_tool_call_ids or [])


def _tool_backed_majority(evidences: Sequence[TaskEvidence]) -> Optional[str]:
    """Prefer preferences citing successful system-executed tools."""
    scored: Dict[str, float] = {}
    counted_call_ids: set[str] = set()
    for e in evidences:
        pref = (e.candidate_preference or "").strip().upper()[:1]
        verified_call_ids = _verified_tool_call_ids(e) - counted_call_ids
        if pref not in {"A", "B", "C", "D"} or not verified_call_ids:
            continue
        scored[pref] = scored.get(pref, 0.0) + float(e.confidence or 0.0) + 1.0
        counted_call_ids.update(verified_call_ids)
    if not scored:
        return None
    return max(scored.items(), key=lambda kv: kv[1])[0]


def _maybe_fix_true_false(sample: MMTSSample, ans: FinalAnswer) -> FinalAnswer:
    """If reasoning asserts the statement is true/false, align letter with options."""
    if sample.question_type != "choice" or not sample.option:
        return ans
    opts = sample.option.lower()
    if "true" not in opts or "false" not in opts:
        return ans
    text = f"{ans.reasoning} {ans.explanation}".lower()
    letter = (ans.answer or "").strip().upper()[:1]
    # Find which option letter is True/False
    true_letter = false_letter = None
    for line in (sample.option or "").splitlines():
        s = line.strip()
        m = re.match(r"^([A-D])[\).:\s]", s, flags=re.I)
        if not m:
            continue
        L = m.group(1).upper()
        low = s.lower()
        if re.search(r"\btrue\b", low):
            true_letter = L
        if re.search(r"\bfalse\b", low):
            false_letter = L
    if not true_letter or not false_letter:
        return ans
    says_true = bool(re.search(r"\b(statement is true|conclusion is true|is true|more step|contains more)\b", text))
    says_false = bool(re.search(r"\b(statement is false|conclusion is false|is false)\b", text))
    if says_true and not says_false and letter == false_letter:
        ans.answer = true_letter
        ans.conflicts = list(ans.conflicts or []) + ["auto_fixed_true_false_mapping"]
    elif says_false and not says_true and letter == true_letter:
        ans.answer = false_letter
        ans.conflicts = list(ans.conflicts or []) + ["auto_fixed_true_false_mapping"]
    return ans



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
            metadata=_context_metadata_text(sample),
        )
        messages = [
            {"role": "system", "content": rendered["system"]},
            {"role": "user", "content": rendered["user"]},
        ]
        resp = self.llm.generate(messages, call_tag="planner")
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
    def run(
        self,
        sample: MMTSSample,
        scale: ScaleName,
        plan: Optional[AgentPlan] = None,
    ) -> Tuple[ScaleObservation, int]:
        tool_results: List[ToolResult] = []
        tool_count = 0
        obs: Optional[ScaleObservation] = None
        for _ in range(self.max_tool_rounds):
            rendered = self.prompts.render(
                "homogeneous_v1",
                scale=scale.value,
                question=sample.question,
                candidates=_candidates(sample),
                series_text=sample.series_text,
                plan=_plan_text(plan),
                metadata=_context_metadata_text(sample),
                tool_catalog=self.tools.catalog_text([scale.value]),
                tool_results=self._tool_results_text(tool_results),
            )
            messages = [
                {"role": "system", "content": rendered["system"]},
                {"role": "user", "content": rendered["user"]},
            ]
            resp = self.llm.generate(messages, call_tag=f"homogeneous:{scale.value}:round{_ + 1}")
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
            # Keep cumulative tool evidence visible to the next round.
            obs.tool_summaries = [json.dumps(r.__dict__, ensure_ascii=False) for r in tool_results]
            continue
        assert obs is not None
        # Always hand off full accumulated tool JSON to TemporalProfile / downstream.
        if tool_results:
            obs.tool_summaries = [json.dumps(r.__dict__, ensure_ascii=False) for r in tool_results]
        return obs, tool_count


class HeterogeneousAgent(ToolLoopMixin):
    def _generate_evidence(
        self,
        sample: MMTSSample,
        role: HeterogeneousRole,
        profile: TemporalProfile,
        plan: Optional[AgentPlan],
        prior_evidences: Optional[Sequence[TaskEvidence]],
        tool_results: List[ToolResult],
        executed_tools: List[ExecutedToolEvidence],
        *,
        finalize: bool,
        round_idx: int,
    ) -> TaskEvidence:
        rendered = self.prompts.render(
            "heterogeneous_v1",
            role=role.value,
            question=sample.question,
            candidates=_candidates(sample),
            series_text=sample.series_text,
            plan=_plan_text(plan),
            temporal_profile=profile.model_dump_json(),
            prior_task_evidence=_prior_evidence_text(prior_evidences),
            metadata=_context_metadata_text(sample),
            tool_catalog=self.tools.catalog_text([role.value]),
            tool_results=(
                json.dumps([record.model_dump() for record in executed_tools], ensure_ascii=False, indent=2)
                if executed_tools
                else "(none)"
            ),
            finalize_instruction=(
                "FINALIZE NOW: tool evidence is complete. Set tool_calls to []. "
                "You MUST set candidate_preference to a candidate letter when evidence supports one "
                "(map lag_corr sign/magnitude and trends to options; falsify unsupported options). "
                "Do not leave candidate_preference null if <tool_results> contain successful quantitative facts."
                if finalize
                else ""
            ),
        )
        messages = [
            {"role": "system", "content": rendered["system"]},
            {"role": "user", "content": rendered["user"]},
        ]
        tag = f"heterogeneous:{role.value}:{'finalize' if finalize else f'round{round_idx}'}"
        resp = self.llm.generate(messages, call_tag=tag)
        try:
            evidence = parse_model(resp.text, TaskEvidence)
        except Exception:
            evidence = TaskEvidence(
                reasoning="Parse failure",
                role=role,
                evidence=["parse failure"],
                candidate_preference=None,
                tool_calls=[],
            )
        evidence.role = role
        if finalize:
            evidence.tool_calls = []
        return evidence

    def run(
        self,
        sample: MMTSSample,
        role: HeterogeneousRole,
        profile: TemporalProfile,
        plan: Optional[AgentPlan] = None,
        prior_evidences: Optional[Sequence[TaskEvidence]] = None,
    ) -> Tuple[TaskEvidence, int]:
        tool_results: List[ToolResult] = []
        executed_tools: List[ExecutedToolEvidence] = []
        tool_count = 0
        evidence: Optional[TaskEvidence] = None
        for round_idx in range(self.max_tool_rounds):
            evidence = self._generate_evidence(
                sample,
                role,
                profile,
                plan,
                prior_evidences,
                tool_results,
                executed_tools,
                finalize=False,
                round_idx=round_idx + 1,
            )
            if not evidence.tool_calls:
                break
            calls = [c.model_dump() if hasattr(c, "model_dump") else c for c in evidence.tool_calls]
            new_results, c = self._run_tools(calls, sample.series, [role.value])
            tool_results.extend(new_results)
            for call, result in zip(calls, new_results):
                executed_tools.append(
                    ExecutedToolEvidence(
                        call_id=f"{role.value}:call{len(executed_tools) + 1}",
                        tool_name=result.name,
                        arguments=call.get("arguments") or {},
                        success=result.success,
                        data=result.data,
                        error=result.error,
                        executor_role=role,
                    )
                )
            tool_count += c
            evidence.tool_summaries = [json.dumps(r.__dict__, ensure_ascii=False) for r in tool_results]
            # Last tool round: force an interpretation pass so preference is not left null.
            if round_idx == self.max_tool_rounds - 1:
                evidence = self._generate_evidence(
                    sample,
                    role,
                    profile,
                    plan,
                    prior_evidences,
                    tool_results,
                    executed_tools,
                    finalize=True,
                    round_idx=round_idx + 1,
                )
                break

        assert evidence is not None
        # Successful tools but still no preference (e.g. stopped early with null) -> one finalize.
        if tool_results and not evidence.candidate_preference:
            evidence = self._generate_evidence(
                sample,
                role,
                profile,
                plan,
                prior_evidences,
                tool_results,
                executed_tools,
                finalize=True,
                round_idx=self.max_tool_rounds + 1,
            )
        # Security boundary: model-authored provenance is never trusted. Rebuild it
        # exclusively from tool calls executed by this agent invocation.
        evidence.executed_tools = executed_tools
        evidence.tool_summaries = [json.dumps(r.__dict__, ensure_ascii=False) for r in tool_results]
        successful_call_ids = {record.call_id for record in executed_tools if record.success}
        evidence.cited_tool_call_ids = [
            call_id for call_id in evidence.cited_tool_call_ids if call_id in successful_call_ids
        ]
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
        tool_vote = _tool_backed_majority(evidences)
        rendered = self.prompts.render(
            "integration_v1",
            question=sample.question,
            candidates=_candidates(sample),
            question_type=sample.question_type,
            series_text=sample.series_text,
            plan=plan.model_dump_json(),
            temporal_profile=profile.model_dump_json(),
            task_evidence=json.dumps([e.model_dump() for e in evidences], ensure_ascii=False),
            metadata=_context_metadata_text(sample),
            preference_votes=_preference_vote_text(evidences),
            tool_backed_majority=tool_vote or "(none)",
        )
        messages = [
            {"role": "system", "content": rendered["system"]},
            {"role": "user", "content": rendered["user"]},
        ]
        resp = self.llm.generate(messages, call_tag="integration")
        try:
            ans = parse_model(resp.text, FinalAnswer)
        except Exception:
            if sample.question_type == "numerical":
                answer = extract_numerical_answer(resp.text) or ""
                fallback_reason = "Parse failure; recovered numerical answer from raw response."
                fallback_conflict = "parse_failure_recovered_numerical_answer"
            else:
                answer = tool_vote or next(
                    (e.candidate_preference for e in evidences if e.candidate_preference),
                    "A",
                )
                fallback_reason = "Parse failure; used tool-backed preference vote."
                fallback_conflict = "parse_failure_used_tool_backed_vote"
            ans = FinalAnswer(
                reasoning=fallback_reason,
                answer=str(answer),
                explanation="fallback",
                conflicts=[fallback_conflict],
            )
        if sample.question_type == "numerical":
            numerical_answer = extract_numerical_answer(ans.answer)
            if numerical_answer:
                ans.answer = numerical_answer
            else:
                ans.answer = ""
                ans.conflicts = list(ans.conflicts or []) + ["invalid_numerical_answer"]
        else:
            letter = extract_final_answer_letter(ans.answer) or extract_final_answer_letter(ans.explanation)
            if letter:
                ans.answer = letter
            else:
                ans.answer = ans.answer.strip()[:1].upper() if ans.answer else "A"
            # Conflict arbitration: if LLM picks a letter that no tool-backed role supports,
            # and a clear tool-backed majority exists, prefer the majority.
            if tool_vote:
                tool_prefs = {
                    (e.candidate_preference or "").strip().upper()[:1]
                    for e in evidences
                    if _verified_tool_call_ids(e) and e.candidate_preference
                }
                tool_prefs.discard("")
                chosen = (ans.answer or "").strip().upper()[:1]
                if tool_prefs and chosen not in tool_prefs and chosen != tool_vote:
                    ans.conflicts = list(ans.conflicts or []) + [
                        f"overrode_llm_{chosen}_with_tool_backed_{tool_vote}"
                    ]
                    ans.answer = tool_vote
            ans = _maybe_fix_true_false(sample, ans)
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
        resp = self.llm.generate(messages, call_tag="baseline")
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
