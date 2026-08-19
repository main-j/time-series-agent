"""Integration pre/post validators: cite trust, option mapping, answer enforcement."""
from __future__ import annotations

import re
from collections import Counter
from typing import Any, Dict, List, Optional, Sequence, Set, Tuple

from ts_agent.core.utils import extract_final_answer_letter, extract_numerical_answer
from ts_agent.schemas.models import (
    ClaimObservation,
    ExecutionMetadata,
    FinalAnswer,
    HeterRoleReasoning,
    MMTSSample,
    ScaleObservation,
    TaskEvidence,
    TemporalProfile,
)

_UPSTREAM_CALL_RE = re.compile(r"^(short|medium|long):step\d+$")
_OPTION_LETTER_RE = re.compile(r"^([A-D])[\).:\s]", re.I)


def collect_homo_success_call_ids(profile: TemporalProfile) -> Set[str]:
    ids: Set[str] = set()
    for obs in (profile.short, profile.medium, profile.long):
        if obs is None:
            continue
        for step in obs.executed_steps or []:
            if step.success and step.call_id:
                ids.add(str(step.call_id))
    return ids


def collect_heter_local_success_call_ids(evidence: TaskEvidence) -> Set[str]:
    ids: Set[str] = set()
    for record in evidence.executed_tools or []:
        if record.success and record.call_id:
            ids.add(str(record.call_id))
    for step in evidence.executed_steps or []:
        if step.success and step.call_id:
            ids.add(str(step.call_id))
    return ids


def verified_tool_call_ids(
    evidence: TaskEvidence,
    *,
    homo_success_ids: Optional[Set[str]] = None,
) -> Set[str]:
    """Local successful tools intersect cites, plus upstream Homo step cites that exist."""
    local_success = collect_heter_local_success_call_ids(evidence)
    cited = {str(c) for c in (evidence.cited_tool_call_ids or [])}
    verified = local_success.intersection(cited)
    homo_ids = homo_success_ids or set()
    for cid in cited:
        if _UPSTREAM_CALL_RE.match(cid) and (not homo_ids or cid in homo_ids):
            # If homo_ids empty (no executed_steps recorded), still allow pattern cites
            # only when homo_ids is empty OR cid is present.
            if not homo_ids or cid in homo_ids:
                verified.add(cid)
        elif _UPSTREAM_CALL_RE.match(cid) and not homo_ids:
            verified.add(cid)
    return verified


def tool_backed_majority(
    evidences: Sequence[TaskEvidence],
    *,
    homo_success_ids: Optional[Set[str]] = None,
) -> Optional[str]:
    scored: Dict[str, float] = {}
    counted: Set[str] = set()
    for e in evidences:
        pref = (e.candidate_preference or "").strip().upper()[:1]
        verified = verified_tool_call_ids(e, homo_success_ids=homo_success_ids) - counted
        if pref not in {"A", "B", "C", "D"} or not verified:
            continue
        scored[pref] = scored.get(pref, 0.0) + float(e.confidence or 0.0) + 1.0
        counted.update(verified)
    if not scored:
        return None
    return max(scored.items(), key=lambda kv: kv[1])[0]


def invert_option_mapping(option_to_series: Dict[str, Any], series_index: int) -> Optional[str]:
    for letter, sid in (option_to_series or {}).items():
        try:
            if int(sid) == int(series_index):
                L = str(letter).strip().upper()[:1]
                if L in {"A", "B", "C", "D"}:
                    return L
        except (TypeError, ValueError):
            continue
    return None


_WAVEFORM_LABELS = ("sine", "square", "triangle", "sawtooth")


def letter_for_waveform_hint(sample: MMTSSample, hint: str) -> Optional[str]:
    label = str(hint or "").strip().lower()
    if label not in _WAVEFORM_LABELS:
        return None
    for line in (sample.option or "").splitlines():
        m = _OPTION_LETTER_RE.match(line.strip())
        if not m:
            continue
        if re.search(rf"\b{re.escape(label)}\b", line, re.I):
            return m.group(1).upper()
    return None


def _collect_waveform_hints(profile: TemporalProfile, evidences: Sequence[TaskEvidence]) -> List[str]:
    hints: List[str] = []

    def _from_data(data: Any) -> None:
        if not isinstance(data, dict):
            return
        h = data.get("waveform_hint")
        if isinstance(h, str) and h.strip() and h.strip().lower() != "ambiguous":
            hints.append(h.strip().lower())
        series = data.get("series")
        if isinstance(series, list):
            for item in series:
                if isinstance(item, dict):
                    hh = item.get("waveform_hint")
                    if isinstance(hh, str) and hh.strip() and hh.strip().lower() != "ambiguous":
                        hints.append(hh.strip().lower())

    for obs in (profile.short, profile.medium, profile.long):
        if obs is None:
            continue
        for step in obs.executed_steps or []:
            if step.success and str(step.tool_name) == "waveform_features":
                _from_data(step.data)
    for ev in evidences:
        for step in ev.executed_steps or []:
            if step.success and str(step.tool_name) == "waveform_features":
                _from_data(step.data)
        for tool in ev.executed_tools or []:
            if tool.success and str(tool.tool_name) == "waveform_features":
                _from_data(tool.data)
    return hints


def extract_winning_series_from_evidence(evidence: TaskEvidence) -> Optional[int]:
    """Best-effort series winner from structured claims or executed tool data."""
    for claim in evidence.reasoning_claims or []:
        for item in claim.evidence or []:
            if item.series_index is not None:
                try:
                    return int(item.series_index)
                except (TypeError, ValueError):
                    pass
            if item.type in {"nearest_series", "winning_series", "series_index"} and item.value is not None:
                try:
                    return int(item.value)
                except (TypeError, ValueError):
                    pass
    for step in evidence.executed_steps or []:
        if not step.success:
            continue
        data = step.data or {}
        nearest = data.get("nearest") if isinstance(data, dict) else None
        if isinstance(nearest, dict) and nearest.get("series_index") is not None:
            try:
                return int(nearest["series_index"])
            except (TypeError, ValueError):
                pass
        if isinstance(data, dict) and data.get("series_index") is not None:
            try:
                return int(data["series_index"])
            except (TypeError, ValueError):
                pass
    return None


def grounded_in_keys_from_claims(claims: List[ClaimObservation]) -> List[str]:
    keys: List[str] = []
    for claim in claims or []:
        for item in claim.evidence or []:
            t = str(item.type or claim.maps_to_measurement or "state").strip()
            sid = item.series_index
            key = f"{t}@{sid}" if sid is not None else t
            if key and key not in keys:
                keys.append(key)
    return keys


def pre_validate_role(
    evidence: TaskEvidence,
    *,
    homo_success_ids: Set[str],
) -> Tuple[HeterRoleReasoning, List[str]]:
    local_success = collect_heter_local_success_call_ids(evidence)
    cited = [str(c) for c in (evidence.cited_tool_call_ids or [])]
    verified_cites: List[str] = []
    warnings: List[str] = []
    for cid in cited:
        if cid in local_success:
            verified_cites.append(cid)
        elif _UPSTREAM_CALL_RE.match(cid) and (not homo_success_ids or cid in homo_success_ids):
            verified_cites.append(cid)
        else:
            warnings.append(f"unverified_cite:{cid}")

    if verified_cites or local_success:
        grounded = True
    else:
        # Preference/prose alone (or forged tool_summaries) cannot ground a role.
        grounded = False

    chain: List[str] = []
    if evidence.reasoning_claims:
        for c in evidence.reasoning_claims:
            chain.append(c.claim)
            for ev in c.evidence or []:
                if ev.value is not None:
                    chain.append(f"{ev.type}={ev.value}")
    if not chain:
        chain = list(evidence.evidence or [])

    grounded_in = grounded_in_keys_from_claims(evidence.reasoning_claims or [])
    role = evidence.role.value if hasattr(evidence.role, "value") else str(evidence.role)
    view = HeterRoleReasoning(
        role=role,
        hypothesis=str(evidence.hypothesis or "").strip() or (evidence.reasoning or "")[:240],
        reasoning_chain=chain[:12],
        candidate_preference=(evidence.candidate_preference or None),
        confidence=float(evidence.confidence or 0.5),
        grounded=grounded,
        grounded_in=grounded_in,
        uncertainty="; ".join(warnings) if warnings else "",
    )
    return view, warnings


def build_execution_metadata(
    sample: MMTSSample,
    profile: TemporalProfile,
    evidences: Sequence[TaskEvidence],
    role_views: Sequence[HeterRoleReasoning],
) -> ExecutionMetadata:
    md = dict(sample.metadata or {})
    option_mapping = dict(md.get("option_to_series") or {})
    homo_ids = collect_homo_success_call_ids(profile)
    warnings: List[str] = []

    # Prefer mapped letter from winning series when option_mapping present
    mapped_pref: Optional[str] = None
    for e in evidences:
        win = extract_winning_series_from_evidence(e)
        if win is not None and option_mapping:
            letter = invert_option_mapping(option_mapping, win)
            if letter:
                mapped_pref = letter
                break

    majority = tool_backed_majority(evidences, homo_success_ids=homo_ids)
    grounded_prefs = {
        (r.candidate_preference or "").strip().upper()[:1]
        for r in role_views
        if r.grounded and r.candidate_preference
    }
    grounded_prefs.discard("")

    waveform_pref: Optional[str] = None
    hints = _collect_waveform_hints(profile, evidences)
    if hints:
        # Prefer majority hint among successful waveform_features calls.
        top_hint, _ = Counter(hints).most_common(1)[0]
        waveform_pref = letter_for_waveform_hint(sample, top_hint)
        if waveform_pref:
            warnings.append(f"waveform_hint_mapped:{top_hint}->{waveform_pref}")

    verified_preference = mapped_pref or waveform_pref or majority
    if verified_preference and grounded_prefs and verified_preference not in grounded_prefs and not mapped_pref and not waveform_pref:
        # majority among grounded only
        if majority and majority in grounded_prefs:
            verified_preference = majority
        elif len(grounded_prefs) == 1:
            verified_preference = next(iter(grounded_prefs))

    for r in role_views:
        if r.uncertainty:
            warnings.append(f"{r.role}:{r.uncertainty}")
        if r.candidate_preference and not r.grounded:
            warnings.append(f"ungrounded_preference:{r.role}:{r.candidate_preference}")

    verified = bool(verified_preference) and (
        bool(grounded_prefs) or bool(mapped_pref) or bool(majority) or bool(waveform_pref)
    )
    return ExecutionMetadata(
        option_mapping=option_mapping,
        verified_preference=verified_preference,
        verified=verified,
        warnings=warnings[:20],
    )


def candidate_letters(sample: MMTSSample) -> Set[str]:
    letters: Set[str] = set()
    for line in (sample.option or "").splitlines():
        m = _OPTION_LETTER_RE.match(line.strip())
        if m:
            letters.add(m.group(1).upper())
    return letters or {"A", "B", "C", "D"}


def maybe_fix_true_false(sample: MMTSSample, ans: FinalAnswer) -> FinalAnswer:
    if sample.question_type != "choice" or not sample.option:
        return ans
    opts = sample.option.lower()
    if "true" not in opts or "false" not in opts:
        return ans
    text = f"{ans.reasoning} {ans.explanation}".lower()
    letter = (ans.answer or "").strip().upper()[:1]
    true_letter = false_letter = None
    for line in (sample.option or "").splitlines():
        s = line.strip()
        m = _OPTION_LETTER_RE.match(s)
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


def post_validate_answer(
    sample: MMTSSample,
    ans: FinalAnswer,
    metadata: ExecutionMetadata,
    role_views: Sequence[HeterRoleReasoning],
) -> FinalAnswer:
    if sample.question_type == "numerical":
        numerical = extract_numerical_answer(ans.answer)
        if numerical:
            ans.answer = numerical
        else:
            ans.answer = ""
            ans.conflicts = list(ans.conflicts or []) + ["invalid_numerical_answer"]
        if not str(ans.answer or "").strip():
            ans.conflicts = list(ans.conflicts or []) + ["empty_answer"]
        return ans

    letter = extract_final_answer_letter(ans.answer) or extract_final_answer_letter(ans.explanation)
    if letter:
        ans.answer = letter
    else:
        ans.answer = ans.answer.strip()[:1].upper() if ans.answer else ""

    # Soft consistency with LLM-authored decision_trace (not code-side threshold binning).
    trace = getattr(ans, "decision_trace", None)
    if trace is not None:
        trace_letter = extract_final_answer_letter(str(trace.matched_letter or ""))
        if trace_letter:
            chosen = (ans.answer or "").strip().upper()[:1]
            if not chosen:
                ans.answer = trace_letter
                ans.conflicts = list(ans.conflicts or []) + ["filled_answer_from_decision_trace"]
            elif chosen != trace_letter:
                ans.conflicts = list(ans.conflicts or []) + [
                    f"answer_{chosen}_disagrees_decision_trace_{trace_letter}"
                ]
                # Prefer the explicit comparison the model wrote in decision_trace.
                ans.answer = trace_letter

    allowed = candidate_letters(sample)
    chosen = (ans.answer or "").strip().upper()[:1]
    if chosen not in allowed:
        if metadata.verified_preference and metadata.verified_preference in allowed:
            ans.conflicts = list(ans.conflicts or []) + [
                f"invalid_letter_{chosen or 'empty'}_used_verified_{metadata.verified_preference}"
            ]
            ans.answer = metadata.verified_preference
            chosen = ans.answer
        else:
            ans.conflicts = list(ans.conflicts or []) + ["invalid_or_empty_choice_letter"]
            if not chosen and metadata.verified_preference:
                ans.answer = metadata.verified_preference
                chosen = ans.answer

    grounded_prefs = {
        (r.candidate_preference or "").strip().upper()[:1]
        for r in role_views
        if r.grounded and r.candidate_preference
    }
    grounded_prefs.discard("")
    vote = metadata.verified_preference
    if vote and grounded_prefs and chosen not in grounded_prefs and chosen != vote:
        ans.conflicts = list(ans.conflicts or []) + [f"overrode_llm_{chosen}_with_tool_backed_{vote}"]
        ans.answer = vote

    ans = maybe_fix_true_false(sample, ans)
    if not str(ans.answer or "").strip():
        ans.conflicts = list(ans.conflicts or []) + ["empty_answer"]
    return ans


def mark_perception_trusted(
    states: List[Any],
    *,
    homo_success_ids: Set[str],
    claim_observations: Optional[List[ClaimObservation]] = None,
) -> None:
    """Mutate PerceptionStateItem.trusted from claim provenance when possible."""
    trusted_types: Set[str] = set()
    for claim in claim_observations or []:
        if claim.confidence in {"tool_supported", "context_supported", "qualified"}:
            for ev in claim.evidence or []:
                if ev.provenance in {"tool", "upstream", "context"}:
                    if ev.call_id and _UPSTREAM_CALL_RE.match(str(ev.call_id)):
                        if not homo_success_ids or str(ev.call_id) in homo_success_ids:
                            trusted_types.add(str(ev.type or ""))
                    elif ev.provenance == "tool" and (not ev.call_id or str(ev.call_id) in homo_success_ids or True):
                        trusted_types.add(str(ev.type or ""))
                if claim.confidence == "tool_supported":
                    trusted_types.add(str(ev.type or claim.maps_to_measurement or ""))
    for st in states:
        t = getattr(st, "type", "") or ""
        if t in trusted_types or (t and t != "note" and claim_observations):
            # structured states from tool_supported claims are trusted; note fallbacks are not
            if t != "note":
                st.trusted = t in trusted_types or any(
                    c.confidence == "tool_supported" for c in (claim_observations or [])
                )
