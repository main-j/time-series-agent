"""Assemble clean four-layer Integration inputs from Planner/Homo/Heter artifacts."""
from __future__ import annotations

import json
import re
from typing import Any, Dict, List, Optional, Sequence

from ts_agent.agents.integration_validator import (
    build_execution_metadata,
    collect_homo_success_call_ids,
    pre_validate_role,
)
from ts_agent.schemas.models import (
    AgentPlan,
    ClaimObservation,
    HomoPerceptionView,
    IntegrationBundle,
    MMTSSample,
    PerceptionStateItem,
    PlannerIntent,
    ScaleName,
    ScaleObservation,
    ScalePerceptionSlice,
    TaskEvidence,
    TemporalProfile,
    HeterReasoningView,
)


def _candidates_text(sample: MMTSSample) -> str:
    return sample.option or "(numerical question: no options)"


def _assignment_brief(plan: AgentPlan) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for item in plan.homo_assignments or []:
        rows.append(
            {
                "agent": f"homo:{item.scale.value}",
                "objective": (item.objective or "")[:200],
                "required_measurements": list(item.required_measurements or [])[:8],
            }
        )
    for item in plan.hetero_assignments or []:
        rows.append(
            {
                "agent": f"hetero:{item.role.value}",
                "objective": (item.objective or "")[:200],
                "required_measurements": list(item.required_measurements or [])[:8],
            }
        )
    return rows[:12]


def build_planner_intent(sample: MMTSSample, plan: AgentPlan) -> PlannerIntent:
    return PlannerIntent(
        goal=str(plan.task_summary or sample.question or "").strip()[:400],
        question_type=str(plan.answer_type or sample.question_type or "unknown"),
        required_output=str(plan.target_output or "").strip()[:400],
        success_criteria=list(plan.success_criteria or [])[:8],
        assignments_brief=_assignment_brief(plan),
    )


def _states_from_claims(claims: List[ClaimObservation], *, trusted_default: bool) -> List[PerceptionStateItem]:
    states: List[PerceptionStateItem] = []
    for claim in claims or []:
        trusted = trusted_default or claim.confidence in {"tool_supported", "context_supported", "qualified"}
        if claim.evidence:
            for ev in claim.evidence:
                states.append(
                    PerceptionStateItem(
                        series_index=ev.series_index,
                        type=str(ev.type or claim.maps_to_measurement or "state"),
                        value=ev.value,
                        trusted=trusted and ev.provenance in {"tool", "upstream", "context", "unresolved"}
                        and (ev.provenance != "unresolved"),
                    )
                )
        else:
            states.append(
                PerceptionStateItem(
                    series_index=None,
                    type=str(claim.maps_to_measurement or "claim"),
                    value=claim.claim,
                    trusted=False,
                )
            )
    return states


def _states_from_observation_notes(obs: ScaleObservation) -> List[PerceptionStateItem]:
    states: List[PerceptionStateItem] = []
    for note in (obs.observations or [])[:8]:
        text = str(note).strip()
        if not text:
            continue
        states.append(PerceptionStateItem(type="note", value=text[:300], trusted=False))
    return states


def build_homo_perception(profile: TemporalProfile) -> HomoPerceptionView:
    by_scale: Dict[str, ScalePerceptionSlice] = {}
    homo_ids = collect_homo_success_call_ids(profile)

    def _slice_for(scale_key: str, obs: Optional[ScaleObservation]) -> None:
        if obs is None:
            return
        claims = list(obs.structured_observations or [])
        if not claims and scale_key in (profile.structured_by_scale or {}):
            claims = list(profile.structured_by_scale.get(scale_key) or [])
        if claims:
            states = _states_from_claims(claims, trusted_default=bool(homo_ids or obs.executed_steps))
            # Mark trusted when claim confidence is tool/context supported
            for i, st in enumerate(states):
                if st.type == "note":
                    st.trusted = False
                elif i < len(claims) or st.type:
                    matching = [c for c in claims if c.maps_to_measurement == st.type or any(
                        (e.type == st.type) for e in (c.evidence or [])
                    )]
                    if matching and matching[0].confidence in {"tool_supported", "context_supported", "qualified"}:
                        st.trusted = True
        else:
            states = _states_from_observation_notes(obs)
        by_scale[scale_key] = ScalePerceptionSlice(
            states=states,
            coverage=dict(obs.coverage or {}),
            summary=" | ".join(obs.observations or [])[:400],
        )

    _slice_for("short", profile.short)
    _slice_for("medium", profile.medium)
    _slice_for("long", profile.long)

    return HomoPerceptionView(
        by_scale=by_scale,
        conflicts=list(profile.conflicts or []),
        summary=str(profile.summary or "")[:800],
    )


def question_rules_appendix(sample: MMTSSample, plan: AgentPlan) -> str:
    parts: List[str] = []
    q = (sample.question or "").lower()
    subset = sample.subset.value if hasattr(sample.subset, "value") else str(sample.subset)
    qt = sample.question_type

    if qt == "choice" and subset in {"Match", "Align"}:
        parts.append(
            "Match/Align: answer must be one candidate letter. "
            "Trust execution_metadata.option_mapping and verified_preference when present."
        )
    if qt == "numerical":
        parts.append(
            "Numerical: set answer to a numeric JSON string. "
            "Do not invent values absent from homo_perception states."
        )
    if re.search(r"\b(strong|moderate|weak)\b", q) or re.search(r"0\.\d+\s*[-–]\s*0\.\d+", q):
        parts.append(
            "Threshold labels: parse intervals from <question> only. "
            "Compare trusted homo_perception numeric states to those intervals, "
            "fill decision_trace, then choose the matching option letter. "
            "Do not copy Heter qualitative words (strong/weak/low/high) over the numeric comparison; "
            "if they disagree, keep the numeric match and add a conflict."
        )
    if re.search(r"\b(noise level|residual.*(ratio|variation)|virtually no noise)\b", q):
        parts.append(
            "Noise level: use trusted homo noise_ratio / residual ratio against thresholds in the question; "
            "do not infer noise from trend alone."
        )
    if re.search(r"\b(causal|cause|counterfactual|because)\b", q) or "reasoning" in (
        (plan.capability or "").lower()
    ):
        parts.append("Causal: correlation is not causation; prefer hypotheses grounded in homo_perception.")
    if re.search(r"\b(waveform|sine|square|triangle|sawtooth)\b", q) or "waveform" in (
        (plan.capability or "").lower()
    ):
        parts.append(
            "Waveform shape: periodicity ≠ sine. Prefer homo_perception waveform_hint / "
            "jump/plateau evidence over FFT period alone; if uncertain, still pick one letter "
            "and record conflicts (do not mechanically default to A)."
        )
    if not parts:
        return ""
    return "<question_rules>\n" + "\n".join(f"- {p}" for p in parts) + "\n</question_rules>"


def assemble_integration_bundle(
    sample: MMTSSample,
    plan: AgentPlan,
    profile: TemporalProfile,
    evidences: Sequence[TaskEvidence],
) -> IntegrationBundle:
    homo_ids = collect_homo_success_call_ids(profile)
    role_views = []
    for ev in evidences:
        view, _warnings = pre_validate_role(ev, homo_success_ids=homo_ids)
        role_views.append(view)

    execution = build_execution_metadata(sample, profile, evidences, role_views)
    return IntegrationBundle(
        question=sample.question,
        candidates=_candidates_text(sample),
        question_type=sample.question_type,
        planner_intent=build_planner_intent(sample, plan),
        homo_perception=build_homo_perception(profile),
        heter_reasoning=HeterReasoningView(roles=role_views),
        execution_metadata=execution,
        question_rules_appendix=question_rules_appendix(sample, plan),
    )


def bundle_template_vars(bundle: IntegrationBundle) -> Dict[str, str]:
    """Render-ready strings for prompt placeholders (no tool dumps)."""
    return {
        "question": bundle.question,
        "candidates": bundle.candidates,
        "question_type": bundle.question_type,
        "planner_intent": json.dumps(bundle.planner_intent.model_dump(), ensure_ascii=False, indent=2),
        "homo_perception": json.dumps(bundle.homo_perception.model_dump(), ensure_ascii=False, indent=2),
        "heter_reasoning": json.dumps(bundle.heter_reasoning.model_dump(), ensure_ascii=False, indent=2),
        "execution_metadata": json.dumps(bundle.execution_metadata.model_dump(), ensure_ascii=False, indent=2),
        "question_rules_appendix": bundle.question_rules_appendix or "",
    }


def assert_bundle_clean(bundle: IntegrationBundle) -> None:
    """Architecture gate: projection must not leak tool execution dumps."""
    raw = json.dumps(bundle.model_dump(), ensure_ascii=False)
    for banned in ("executed_tools", "tool_summaries", "args_fingerprint"):
        if banned in raw:
            raise AssertionError(f"IntegrationBundle leaked banned key: {banned}")
