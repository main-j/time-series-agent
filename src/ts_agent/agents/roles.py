from __future__ import annotations

import json
import re
from typing import Any, Dict, List, Optional, Sequence, Tuple

from ts_agent.core.llm import LLMProvider
from ts_agent.core.utils import extract_final_answer_letter, extract_numerical_answer, parse_model
from ts_agent.prompts.library import PromptLibrary
from ts_agent.schemas.models import (
    AgentPlan,
    CapabilitySelection,
    EvidenceCapabilityPlan,
    EvidencePlan,
    ExecutedStep,
    ExecutedToolEvidence,
    FinalAnswer,
    HeteroAssignment,
    HeterogeneousRole,
    HomoAssignment,
    InvocationPlan,
    MMTSSample,
    NoToolDecision,
    ScaleName,
    ScaleObservation,
    TaskEvidence,
    TemporalProfile,
    ToolWorkflow,
)
from ts_agent.tools.registry import ToolRegistry, ToolResult
from ts_agent.tools.workflow import WorkflowExecutor


def _candidates(sample: MMTSSample) -> str:
    return sample.option or "(numerical question: no options)"


def _usable_scale_observation(obs: Optional[ScaleObservation]) -> bool:
    if obs is None:
        return False
    if obs.structured_observations:
        return True
    texts = [t for t in (obs.observations or []) if t and "Unable to integrate" not in t]
    return bool(texts)


def _usable_task_evidence(ev: Optional[TaskEvidence]) -> bool:
    if ev is None:
        return False
    if (ev.candidate_preference or "").strip():
        return True
    if ev.reasoning_claims:
        return True
    texts = [t for t in (ev.evidence or []) if t and t.lower() != "parse failure"]
    return bool(texts)


def _plan_text(plan: Optional[AgentPlan]) -> str:
    if plan is None:
        return "(none)"
    return plan.model_dump_json()


def _assignment_text(assignment: Optional[Any]) -> str:
    if assignment is None:
        return "(none)"
    if hasattr(assignment, "model_dump_json"):
        return assignment.model_dump_json()
    return json.dumps(assignment, ensure_ascii=False)


def _homo_assignment_for(plan: Optional[AgentPlan], scale: ScaleName) -> Optional[HomoAssignment]:
    if plan is None:
        return None
    for item in plan.homo_assignments or []:
        if item.scale == scale:
            return item
    return None


def _hetero_assignment_for(plan: Optional[AgentPlan], role: HeterogeneousRole) -> Optional[HeteroAssignment]:
    if plan is None:
        return None
    for item in plan.hetero_assignments or []:
        if item.role == role:
            return item
    return None


def _collect_homo_measurements(homo: List[HomoAssignment]) -> List[str]:
    seen: List[str] = []
    for item in homo:
        for measurement in item.required_measurements or []:
            m = str(measurement).strip()
            if m and m not in seen:
                seen.append(m)
    return seen


_GENERIC_MEASUREMENTS = frozenset(
    {"task_relevant_evidence", "scale_specific_structure", "answer_relevant_measurement"}
)


def _hetero_objective_from_plan(plan: AgentPlan) -> str:
    target = (plan.target_output or "").strip()
    if target:
        return target
    summary = (plan.task_summary or "").strip()
    if summary:
        return summary
    return "Reconcile scale observations and produce the evidence needed to answer the question."


def _hetero_validation_from_homo(homo: List[HomoAssignment]) -> List[str]:
    seen: List[str] = []
    for item in homo:
        for req in item.validation_requirements or []:
            r = str(req).strip()
            if r and r not in seen:
                seen.append(r)
    if not seen:
        return [
            "Reject period equal to series length without cross-validation.",
            "Prefer successful tool evidence over unsupported prose.",
        ]
    return seen


def _resolve_hetero_measurements(
    required_measurements: Optional[List[str]],
    inherited_homo_measurements: List[str],
) -> List[str]:
    if not required_measurements:
        return list(inherited_homo_measurements) if inherited_homo_measurements else ["scale_specific_structure"]
    normalized = [str(m).strip() for m in required_measurements if str(m).strip()]
    if set(normalized).issubset(_GENERIC_MEASUREMENTS) and inherited_homo_measurements:
        return list(inherited_homo_measurements)
    return normalized


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


def _planner_metadata_text(sample: MMTSSample) -> str:
    """Structural context only; omit category labels that encourage hard routing."""
    ctx = _sample_context(sample)
    parts = [
        f"local_overall={ctx['local_overall']}",
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
    cited = set(evidence.cited_tool_call_ids or [])
    local = successful.intersection(cited)
    # Heter may cite upstream Homo workflow call_ids (context_supported).
    upstream = {
        str(cid)
        for cid in cited
        if re.match(r"^(short|medium|long):step\d+$", str(cid))
    }
    return local | upstream


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
    def __init__(
        self,
        llm: LLMProvider,
        prompts: PromptLibrary,
        tools: ToolRegistry,
        max_tool_rounds: int = 3,
        max_macro_cycles: int = 1,
    ):
        self.llm = llm
        self.prompts = prompts
        self.tools = tools
        self.max_tool_rounds = max_tool_rounds
        self.max_macro_cycles = max(1, int(max_macro_cycles))
        self.workflow_executor = WorkflowExecutor(tools)
        self.last_stage_trace: Dict[str, Any] = {}

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

    def _llm_stage(self, prompt_name: str, call_tag: str, schema: Any, **kwargs: Any) -> Tuple[Any, str]:
        rendered = self.prompts.render(prompt_name, **kwargs)
        messages = [
            {"role": "system", "content": rendered["system"]},
            {"role": "user", "content": rendered["user"]},
        ]
        resp = self.llm.generate(messages, call_tag=call_tag)
        try:
            return parse_model(resp.text, schema), resp.text
        except Exception:
            return None, resp.text

    @staticmethod
    def _validate_no_tool_decision(plan_cap: EvidenceCapabilityPlan, *, allow_empty_reason: bool = False) -> Optional[str]:
        sel = plan_cap.capability_selection or CapabilitySelection()
        if sel.selected_tools:
            return None
        decision = sel.no_tool_decision
        if decision is None:
            return "selected_tools empty but no_tool_decision missing"
        if not allow_empty_reason and not str(decision.reason or "").strip():
            return "no_tool_decision.reason is required when skipping tools"
        return None

    @staticmethod
    def _selected_tool_names(plan_cap: EvidenceCapabilityPlan) -> List[str]:
        sel = plan_cap.capability_selection or CapabilitySelection()
        names: List[str] = []
        for item in sel.selected_tools or []:
            name = str(getattr(item, "tool", "") or "").strip()
            if name and name not in names:
                names.append(name)
        return names

    @staticmethod
    def _executed_steps_text(steps: List[ExecutedStep]) -> str:
        if not steps:
            return "(none)"
        return json.dumps([s.model_dump() for s in steps], ensure_ascii=False, indent=2)

    @staticmethod
    def _candidates_block(sample: MMTSSample, *, include: bool) -> str:
        if not include:
            return ""
        return f"<candidates>\n{_candidates(sample)}\n</candidates>"


class PlannerAgent:
    def __init__(self, llm: LLMProvider, prompts: PromptLibrary):
        self.llm = llm
        self.prompts = prompts

    @staticmethod
    def _sanitize_plan(sample: MMTSSample, plan: AgentPlan) -> AgentPlan:
        """Normalize assignments and derive runtime agent lists. No keyword/tool routing."""
        ctx = _sample_context(sample)
        n_series = int(ctx["n_series"])
        focus = list(ctx.get("focus_intervals") or [])

        # Legacy plans: synthesize assignments from scales/roles if needed.
        if not plan.homo_assignments and plan.scales:
            plan.homo_assignments = [
                HomoAssignment(
                    scale=scale,
                    objective=f"Collect {scale.value}-scale evidence for: {plan.task_summary or sample.question}",
                    required_measurements=["scale_specific_structure"],
                    validation_requirements=["Ground observations in tool evidence."],
                    target_series=list(range(1, n_series + 1)),
                    focus_intervals=focus if isinstance(focus, list) else [],
                )
                for scale in plan.scales
            ]
        if not plan.hetero_assignments and plan.heterogeneous_agents:
            inherited = _collect_homo_measurements(plan.homo_assignments or [])
            plan.hetero_assignments = [
                HeteroAssignment(
                    role=role,
                    objective=_hetero_objective_from_plan(plan),
                    required_measurements=_resolve_hetero_measurements([], inherited),
                    validation_requirements=_hetero_validation_from_homo(plan.homo_assignments or []),
                    target_series=list(range(1, n_series + 1)),
                    focus_intervals=focus if isinstance(focus, list) else [],
                )
                for role in plan.heterogeneous_agents
            ]

        # Deduplicate by scale/role while preserving order.
        seen_scales = set()
        homo: List[HomoAssignment] = []
        for item in plan.homo_assignments or []:
            if item.scale in seen_scales:
                continue
            seen_scales.add(item.scale)
            if not str(item.objective or "").strip():
                item.objective = f"Collect {item.scale.value}-scale evidence for the question."
            if not item.required_measurements:
                item.required_measurements = ["scale_specific_structure"]
            if not item.target_series:
                item.target_series = list(range(1, n_series + 1))
            homo.append(item)
        plan.homo_assignments = homo
        inherited_homo_measurements = _collect_homo_measurements(homo)

        seen_roles = set()
        hetero: List[HeteroAssignment] = []
        for item in plan.hetero_assignments or []:
            if item.role in seen_roles:
                continue
            seen_roles.add(item.role)
            if not str(item.objective or "").strip():
                item.objective = _hetero_objective_from_plan(plan)
            item.required_measurements = _resolve_hetero_measurements(
                item.required_measurements,
                inherited_homo_measurements,
            )
            if not item.validation_requirements:
                item.validation_requirements = _hetero_validation_from_homo(homo)
            if not item.target_series:
                item.target_series = list(range(1, n_series + 1))
            hetero.append(item)
        plan.hetero_assignments = hetero

        if not plan.homo_assignments:
            plan.homo_assignments = [
                HomoAssignment(
                    scale=scale,
                    objective=f"Collect {scale.value}-scale evidence for the question.",
                    required_measurements=["scale_specific_structure"],
                    validation_requirements=["Ground observations in tool evidence."],
                    target_series=list(range(1, n_series + 1)),
                    focus_intervals=focus if isinstance(focus, list) else [],
                )
                for scale in (ScaleName.SHORT, ScaleName.MEDIUM, ScaleName.LONG)
            ]
            inherited_homo_measurements = _collect_homo_measurements(plan.homo_assignments)
        if not plan.hetero_assignments:
            plan.hetero_assignments = [
                HeteroAssignment(
                    role=HeterogeneousRole.STRUCTURE,
                    objective=_hetero_objective_from_plan(plan),
                    required_measurements=_resolve_hetero_measurements([], inherited_homo_measurements),
                    validation_requirements=_hetero_validation_from_homo(plan.homo_assignments),
                    target_series=list(range(1, n_series + 1)),
                    focus_intervals=focus if isinstance(focus, list) else [],
                )
            ]

        plan.scales = list(dict.fromkeys(item.scale for item in plan.homo_assignments))
        plan.heterogeneous_agents = list(dict.fromkeys(item.role for item in plan.hetero_assignments))

        if sample.local_overall in {"local", "overall"}:
            plan.scope = sample.local_overall
        plan.univariate = bool(ctx["is_univariate"])
        plan.task_summary = str(plan.task_summary or sample.question).strip()
        question_type = str(sample.question_type or "unknown").lower()
        if plan.answer_type == "unknown" and question_type in {"choice", "numerical", "binary"}:
            plan.answer_type = question_type  # type: ignore[assignment]
        if not str(plan.target_output or "").strip():
            if plan.answer_type == "numerical":
                plan.target_output = "Return the single numerical quantity requested by the question."
            elif plan.answer_type in {"choice", "binary"}:
                plan.target_output = "Return the option letter whose claim is best supported by evidence."
            else:
                plan.target_output = "Return the answer requested by the question."
        if not plan.success_criteria:
            plan.success_criteria = [
                "Cover every assignment required_measurement with tool-grounded evidence or mark it unresolved.",
                "Do not replace the requested quantity with an unrelated proxy measurement.",
            ]
        if not str(plan.reasoning or "").strip():
            plan.reasoning = f"Route evidence gathering according to: {plan.task_summary}"
        # Strip accidental tool-name directives from notes; planner must not bind tools.
        notes = str(plan.notes or "").strip()
        if re.search(r"\buse\s+[a-z_]+\b", notes, flags=re.I):
            notes = re.sub(r"(?i)\buse\s+[a-z_]+[^.]*\.?", "", notes).strip()
            if notes:
                notes = f"{notes}; tool_names_stripped_from_notes"
            else:
                notes = "tool_names_stripped_from_notes"
        plan.notes = notes
        return plan

    def run(self, sample: MMTSSample) -> AgentPlan:
        rendered = self.prompts.render(
            "planner_v1",
            question=sample.question,
            candidates=_candidates(sample),
            metadata=_planner_metadata_text(sample),
        )
        messages = [
            {"role": "system", "content": rendered["system"]},
            {"role": "user", "content": rendered["user"]},
        ]
        resp = self.llm.generate(messages, call_tag="planner")
        try:
            plan = parse_model(resp.text, AgentPlan)
        except Exception:
            # Conservative schema fallback: no keyword/subset hard routing.
            plan = AgentPlan(
                reasoning="Fallback plan after planner parse failure; use general multi-scale structure analysis.",
                task_summary=sample.question,
                target_output=(
                    "Return the single numerical quantity requested by the question."
                    if sample.question_type == "numerical"
                    else "Return the option letter whose claim is best supported by evidence."
                ),
                answer_type=sample.question_type if sample.question_type in {"choice", "numerical"} else "unknown",
                capability="feature_analysis",
                scope="overall" if sample.local_overall == "overall" else "local",
                univariate=sample.is_univariate,
                homo_assignments=[
                    HomoAssignment(
                        scale=scale,
                        objective=f"Collect {scale.value}-scale evidence for the question.",
                        required_measurements=["scale_specific_structure"],
                        validation_requirements=["Ground observations in tool evidence."],
                    )
                    for scale in (ScaleName.SHORT, ScaleName.MEDIUM, ScaleName.LONG)
                ],
                hetero_assignments=[
                    HeteroAssignment(
                        role=HeterogeneousRole.STRUCTURE,
                        objective="Return the single numerical quantity requested by the question.",
                        required_measurements=["scale_specific_structure"],
                        validation_requirements=[
                            "Reject period equal to series length without cross-validation.",
                            "Prefer successful tool evidence over unsupported prose.",
                        ],
                    )
                ],
                notes=f"planner_parse_failed; raw={resp.text[:200]}",
            )
        return self._sanitize_plan(sample, plan)


class HomogeneousAgent(ToolLoopMixin):
    def run(
        self,
        sample: MMTSSample,
        scale: ScaleName,
        plan: Optional[AgentPlan] = None,
    ) -> Tuple[ScaleObservation, int]:
        assignment = _homo_assignment_for(plan, scale)
        metadata = _context_metadata_text(sample)
        plan_text = _plan_text(plan)
        assignment_text = _assignment_text(assignment)
        tool_count = 0
        stage_trace: Dict[str, Any] = {"scale": scale.value, "macros": []}
        obs: Optional[ScaleObservation] = None
        failure_context = ""

        for macro in range(self.max_macro_cycles + 1):
            macro_trace: Dict[str, Any] = {"macro": macro, "skipped_stages": []}
            plan_cap, _raw = self._llm_stage(
                "homo_s1s2_evidence_capability_v1",
                f"homogeneous:{scale.value}:s1s2:m{macro}",
                EvidenceCapabilityPlan,
                scale=scale.value,
                assignment=assignment_text,
                plan=plan_text,
                metadata=metadata + (f"\nretry_context={failure_context}" if failure_context else ""),
                tool_capabilities=self.tools.capabilities_text([scale.value]),
            )
            if plan_cap is None:
                plan_cap = EvidenceCapabilityPlan(
                    reasoning="Parse failure; fallback to describe_series.",
                    evidence_plan=EvidencePlan(
                        objective="Obtain basic series statistics",
                        claims_to_support=[],
                        analysis_scope={"scale": scale.value},
                    ),
                    capability_selection=CapabilitySelection(
                        selected_tools=[
                            {"tool": "describe_series", "reason": "parse fallback", "supports_evidence": []}
                        ]
                    ),
                )
            macro_trace["s1s2"] = plan_cap.model_dump()

            selected = self._selected_tool_names(plan_cap)
            executed_steps: List[ExecutedStep] = []
            workflow = ToolWorkflow(workflow=[])

            if not selected:
                err = self._validate_no_tool_decision(plan_cap)
                if err:
                    plan_cap.capability_selection = CapabilitySelection(
                        selected_tools=[
                            {
                                "tool": "describe_series",
                                "reason": f"invalid no-tool decision ({err}); gathering baseline stats",
                                "supports_evidence": [],
                            }
                        ]
                    )
                    selected = self._selected_tool_names(plan_cap)
                else:
                    macro_trace["skipped_stages"] = ["S3", "S4"]

            if selected:
                workflow, _ = self._llm_stage(
                    "homo_s3_workflow_v1",
                    f"homogeneous:{scale.value}:s3:m{macro}",
                    ToolWorkflow,
                    scale=scale.value,
                    evidence_capability_plan=plan_cap.model_dump_json(),
                    io_concepts=self.tools.io_concepts_text([scale.value], tools=selected),
                    metadata=metadata,
                )
                if workflow is None:
                    workflow = ToolWorkflow(
                        reasoning="Parse failure; sequential selected tools",
                        workflow=[
                            {"step": i + 1, "tool": name, "output_key": name, "input_binding": {}}
                            for i, name in enumerate(selected)
                        ],
                    )
                macro_trace["s3"] = workflow.model_dump()

                if workflow.workflow:
                    inv, _ = self._llm_stage(
                        "homo_s4_invocation_v1",
                        f"homogeneous:{scale.value}:s4:m{macro}",
                        InvocationPlan,
                        scale=scale.value,
                        workflow=workflow.model_dump_json(),
                        tool_invocation_spec=self.tools.invocation_text([scale.value], tools=selected),
                        metadata=metadata,
                        assignment=assignment_text,
                    )
                    if inv is None:
                        inv = InvocationPlan(
                            reasoning="Parse failure; default empty args",
                            calls=[
                                {"step": st.step, "tool": st.tool, "args": {"series_index": 1}}
                                for st in workflow.workflow
                            ],
                        )
                    macro_trace["s4"] = inv.model_dump()
                    executed_steps = self.workflow_executor.execute(
                        workflow,
                        inv,
                        sample.series,
                        [scale.value],
                        executor_id=scale.value,
                    )
                    tool_count += len(executed_steps)
                    macro_trace["executed_steps"] = [s.model_dump() for s in executed_steps]

            parsed_obs, _ = self._llm_stage(
                "homo_s5_integration_v1",
                f"homogeneous:{scale.value}:s5:m{macro}",
                ScaleObservation,
                scale=scale.value,
                evidence_capability_plan=plan_cap.model_dump_json(),
                executed_steps=self._executed_steps_text(executed_steps),
                assignment=assignment_text,
                metadata=metadata,
            )
            retain_prior = False
            if parsed_obs is None:
                if _usable_scale_observation(obs):
                    retain_prior = True
                    # Keep prior usable observation; refresh tool provenance from this macro.
                    assert obs is not None
                    obs.unresolved_claims = list(
                        dict.fromkeys((obs.unresolved_claims or []) + ["s5_parse_failure_retained_prior"])
                    )
                else:
                    obs = ScaleObservation(
                        reasoning="Parse failure in S5",
                        scale=scale,
                        observations=["Unable to integrate tool evidence."],
                        unresolved_claims=["parse_failure"],
                    )
            else:
                obs = parsed_obs
            obs.scale = scale
            obs.evidence_plan = plan_cap.evidence_plan
            obs.capability_selection = plan_cap.capability_selection
            obs.workflow = workflow
            obs.executed_steps = executed_steps
            obs.skipped_stages = list(macro_trace.get("skipped_stages") or [])
            obs.tool_calls = []
            if executed_steps:
                obs.tool_summaries = [json.dumps(s.model_dump(), ensure_ascii=False) for s in executed_steps]
            for claim in obs.structured_observations or []:
                if claim.confidence == "tool_supported":
                    ok = any(
                        (e.call_id and any(es.call_id == e.call_id and es.success for es in executed_steps))
                        for e in (claim.evidence or [])
                    )
                    if not ok and not executed_steps:
                        claim.confidence = "unresolved"
            macro_trace["s5"] = {
                "coverage": obs.coverage,
                "unresolved_claims": obs.unresolved_claims,
                "n_structured": len(obs.structured_observations or []),
                "retained_prior": retain_prior,
            }
            stage_trace["macros"].append(macro_trace)

            if retain_prior or not obs.unresolved_claims or macro >= self.max_macro_cycles:
                break
            failure_context = f"unresolved_claims={obs.unresolved_claims}; retry capability planning"

        self.last_stage_trace = stage_trace
        assert obs is not None
        return obs, tool_count


class HeterogeneousAgent(ToolLoopMixin):
    def _needs_candidates(self, role: HeterogeneousRole) -> bool:
        return role in {HeterogeneousRole.MATCHING, HeterogeneousRole.ALIGNMENT}

    def run(
        self,
        sample: MMTSSample,
        role: HeterogeneousRole,
        profile: TemporalProfile,
        plan: Optional[AgentPlan] = None,
        prior_evidences: Optional[Sequence[TaskEvidence]] = None,
    ) -> Tuple[TaskEvidence, int]:
        assignment = _hetero_assignment_for(plan, role)
        metadata = _context_metadata_text(sample)
        plan_text = _plan_text(plan)
        assignment_text = _assignment_text(assignment)
        task_summary = (plan.task_summary if plan else "") or ""
        temporal_text = profile.model_dump_json()
        prior_text = _prior_evidence_text(prior_evidences)
        candidates_block = self._candidates_block(sample, include=self._needs_candidates(role))
        tool_count = 0
        stage_trace: Dict[str, Any] = {"role": role.value, "macros": []}
        evidence: Optional[TaskEvidence] = None
        failure_context = ""

        for macro in range(self.max_macro_cycles + 1):
            macro_trace: Dict[str, Any] = {"macro": macro, "skipped_stages": []}
            plan_cap, _ = self._llm_stage(
                "heter_s1s2_evidence_capability_v1",
                f"heterogeneous:{role.value}:s1s2:m{macro}",
                EvidenceCapabilityPlan,
                role=role.value,
                assignment=assignment_text,
                plan=plan_text,
                task_summary=task_summary,
                temporal_profile=temporal_text,
                prior_task_evidence=prior_text,
                metadata=metadata + (f"\nretry_context={failure_context}" if failure_context else ""),
                tool_capabilities=self.tools.capabilities_text([role.value]),
                candidates_block=candidates_block,
            )
            if plan_cap is None:
                plan_cap = EvidenceCapabilityPlan(
                    reasoning="Parse failure; skip tools and use temporal profile.",
                    evidence_plan=EvidencePlan(objective=str(getattr(assignment, "objective", "") or "")),
                    capability_selection=CapabilitySelection(
                        selected_tools=[],
                        no_tool_decision=NoToolDecision(
                            skip_tools=True,
                            reason="Parse failure fallback; use temporal profile context",
                            evidence_sources=[],
                        ),
                    ),
                )
            macro_trace["s1s2"] = plan_cap.model_dump()

            selected = self._selected_tool_names(plan_cap)
            executed_steps: List[ExecutedStep] = []
            workflow = ToolWorkflow(workflow=[])

            if not selected:
                err = self._validate_no_tool_decision(plan_cap, allow_empty_reason=False)
                if err:
                    plan_cap.capability_selection.no_tool_decision = NoToolDecision(
                        skip_tools=True,
                        reason=f"auto-filled after invalid no-tool ({err}); using temporal profile",
                        evidence_sources=[],
                    )
                macro_trace["skipped_stages"] = ["S3", "S4"]
            else:
                workflow, _ = self._llm_stage(
                    "heter_s3_workflow_v1",
                    f"heterogeneous:{role.value}:s3:m{macro}",
                    ToolWorkflow,
                    role=role.value,
                    evidence_capability_plan=plan_cap.model_dump_json(),
                    io_concepts=self.tools.io_concepts_text([role.value], tools=selected),
                    metadata=metadata,
                )
                if workflow is None:
                    workflow = ToolWorkflow(
                        reasoning="Parse failure; sequential selected tools",
                        workflow=[
                            {"step": i + 1, "tool": name, "output_key": name, "input_binding": {}}
                            for i, name in enumerate(selected)
                        ],
                    )
                macro_trace["s3"] = workflow.model_dump()

                if workflow.workflow:
                    inv, _ = self._llm_stage(
                        "heter_s4_invocation_v1",
                        f"heterogeneous:{role.value}:s4:m{macro}",
                        InvocationPlan,
                        role=role.value,
                        workflow=workflow.model_dump_json(),
                        tool_invocation_spec=self.tools.invocation_text([role.value], tools=selected),
                        metadata=metadata,
                        assignment=assignment_text,
                        candidates_block=candidates_block,
                    )
                    if inv is None:
                        inv = InvocationPlan(
                            reasoning="Parse failure; default args",
                            calls=[
                                {"step": st.step, "tool": st.tool, "args": {"series_index": 1}}
                                for st in workflow.workflow
                            ],
                        )
                    macro_trace["s4"] = inv.model_dump()
                    executed_steps = self.workflow_executor.execute(
                        workflow,
                        inv,
                        sample.series,
                        [role.value],
                        executor_id=role.value,
                    )
                    tool_count += len(executed_steps)
                    macro_trace["executed_steps"] = [s.model_dump() for s in executed_steps]

            parsed_evidence, _ = self._llm_stage(
                "heter_s5_integration_v1",
                f"heterogeneous:{role.value}:s5:m{macro}",
                TaskEvidence,
                role=role.value,
                evidence_capability_plan=plan_cap.model_dump_json(),
                executed_steps=self._executed_steps_text(executed_steps),
                temporal_profile=temporal_text,
                assignment=assignment_text,
                metadata=metadata,
                candidates_block=candidates_block,
            )
            retain_prior = False
            if parsed_evidence is None:
                if _usable_task_evidence(evidence):
                    retain_prior = True
                    assert evidence is not None
                    evidence.unresolved_claims = list(
                        dict.fromkeys((evidence.unresolved_claims or []) + ["s5_parse_failure_retained_prior"])
                    )
                else:
                    evidence = TaskEvidence(
                        reasoning="Parse failure in S5",
                        role=role,
                        evidence=["parse failure"],
                        unresolved_claims=["parse_failure"],
                    )
            else:
                evidence = parsed_evidence
            evidence.role = role
            evidence.evidence_plan = plan_cap.evidence_plan
            evidence.capability_selection = plan_cap.capability_selection
            evidence.workflow = workflow
            evidence.executed_steps = executed_steps
            evidence.skipped_stages = list(macro_trace.get("skipped_stages") or [])
            evidence.tool_calls = []

            executed_tools: List[ExecutedToolEvidence] = []
            for step in executed_steps:
                executed_tools.append(
                    ExecutedToolEvidence(
                        call_id=step.call_id,
                        tool_name=step.tool_name,
                        arguments=step.resolved_arguments or step.arguments,
                        success=step.success,
                        data=step.data,
                        error=step.error,
                        executor_role=role,
                    )
                )
            evidence.executed_tools = executed_tools
            evidence.tool_summaries = [json.dumps(s.model_dump(), ensure_ascii=False) for s in executed_steps]
            local_success = {r.call_id for r in executed_tools if r.success}
            filtered_cites: List[str] = []
            for call_id in evidence.cited_tool_call_ids or []:
                cid = str(call_id)
                if cid in local_success:
                    filtered_cites.append(cid)
                elif re.match(r"^(short|medium|long|structure|reasoning|matching|alignment):step\d+$", cid):
                    filtered_cites.append(cid)
            evidence.cited_tool_call_ids = filtered_cites

            macro_trace["s5"] = {
                "candidate_preference": evidence.candidate_preference,
                "coverage": evidence.coverage,
                "unresolved_claims": evidence.unresolved_claims,
                "retained_prior": retain_prior,
            }
            stage_trace["macros"].append(macro_trace)

            if retain_prior or not evidence.unresolved_claims or macro >= self.max_macro_cycles:
                break
            failure_context = f"unresolved_claims={evidence.unresolved_claims}"

        self.last_stage_trace = stage_trace
        assert evidence is not None
        return evidence, tool_count


class IntegrationAgent:
    def __init__(self, llm: LLMProvider, prompts: PromptLibrary):
        self.llm = llm
        self.prompts = prompts
        self.last_bundle: Optional[Any] = None

    def run(
        self,
        sample: MMTSSample,
        plan: AgentPlan,
        profile: TemporalProfile,
        evidences: List[TaskEvidence],
    ) -> FinalAnswer:
        from ts_agent.agents.integration_view import assemble_integration_bundle, bundle_template_vars
        from ts_agent.agents.integration_validator import post_validate_answer

        bundle = assemble_integration_bundle(sample, plan, profile, evidences)
        self.last_bundle = bundle
        rendered = self.prompts.render("integration_v1", **bundle_template_vars(bundle))
        messages = [
            {"role": "system", "content": rendered["system"]},
            {"role": "user", "content": rendered["user"]},
        ]
        resp = self.llm.generate(messages, call_tag="integration")
        try:
            ans = parse_model(resp.text, FinalAnswer)
        except Exception:
            vote = bundle.execution_metadata.verified_preference
            if sample.question_type == "numerical":
                answer = extract_numerical_answer(resp.text) or ""
                fallback_reason = "Parse failure; recovered numerical answer from raw response."
                fallback_conflict = "parse_failure_recovered_numerical_answer"
            else:
                answer = vote or next(
                    (e.candidate_preference for e in evidences if e.candidate_preference),
                    "",
                )
                if answer:
                    fallback_reason = "Parse failure; used verified preference vote."
                    fallback_conflict = "parse_failure_used_tool_backed_vote"
                else:
                    fallback_reason = "Parse failure; no grounded preference available."
                    fallback_conflict = "parse_failure_no_grounded_preference"
            ans = FinalAnswer(
                reasoning=fallback_reason,
                answer=str(answer),
                explanation="fallback",
                conflicts=[fallback_conflict],
            )
        return post_validate_answer(
            sample,
            ans,
            bundle.execution_metadata,
            bundle.heter_reasoning.roles,
        )


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
    structured_by_scale = {}
    for o in observations:
        texts.extend(o.observations)
        if o.structured_observations:
            structured_by_scale[o.scale.value] = list(o.structured_observations)
    profile.structured_by_scale = structured_by_scale
    joined = " | ".join(texts).lower()
    conflicts = []
    if "stationary" in joined and "non-stationary" in joined:
        conflicts.append("Conflicting stationarity observations across scales.")
    profile.conflicts = conflicts
    profile.summary = " ".join(texts)[:2000]
    return profile
