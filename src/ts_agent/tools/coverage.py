"""MMTS-Bench capability -> required tools mapping for coverage validation."""
from __future__ import annotations

import ast
import json
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Set, Tuple

import pandas as pd

from ts_agent.tools.registry import ToolRegistry, build_default_registry


@dataclass(frozen=True)
class CapabilitySpec:
    name: str
    pattern: str
    required_tools: frozenset[str]


# Each capability maps to tool(s) that MUST appear on the agent role whitelist.
CAPABILITIES: Tuple[CapabilitySpec, ...] = (
    CapabilitySpec("describe_basic", r"\b(mean|maximum|minimum|range|slope|standard deviation)\b", frozenset({"describe_series"})),
    CapabilitySpec("describe_percentile", r"\b(median|percentile|50th|90th|99th)\b", frozenset({"describe_series"})),
    CapabilitySpec(
        "crossing_points",
        r"\b(cross(?:es|ing)?|crossing points?).*(median|mean|zero|threshold)|(median|mean|zero|threshold).*(cross(?:es|ing)?|crossing points?)\b",
        frozenset({"crossing_points"}),
    ),
    CapabilitySpec(
        "advanced_features",
        r"\b(skewness|kurtosis|entropy|stability|lumpiness|heteroskedastic|arch)\b",
        frozenset({"advanced_features"}),
    ),
    CapabilitySpec("value_at_index", r"\b(value at index|what is the value at)\b", frozenset({"value_at_index"})),
    CapabilitySpec(
        "global_index",
        r"\b(where does the global (maximum|minimum)|global maximum or minimum|present a global)\b",
        frozenset({"global_extrema"}),
    ),
    CapabilitySpec("local_extrema_count", r"\b(local maximum|local minimum|local max|local min)\b", frozenset({"local_extrema", "global_extrema"})),
    CapabilitySpec("segment_trend", r"\b(trend in the segment|trend from index|segment.*trend)\b", frozenset({"segment_trend"})),
    CapabilitySpec("step_levels", r"\b(step level|stepwise|plateau level|more step|staircase|step-like)\b", frozenset({"step_levels"})),
    CapabilitySpec("extrema", r"\b(peak|trough|extrema)\b", frozenset({"local_extrema", "global_extrema"})),
    CapabilitySpec("volatility", r"\b(volatil|fluctuat|noise level|noisy)\b", frozenset({"sliding_stats", "diff_stats"})),
    CapabilitySpec("seasonality", r"\b(season|periodic|period length|cyclical|seasonal strength)\b", frozenset({"fft_period", "stl_strength", "autocorr"})),
    CapabilitySpec("stationarity", r"\b(stationary|non-stationary|adf)\b", frozenset({"adf_stationarity"})),
    CapabilitySpec("change_point", r"\b(change point|structural break|regime shift)\b", frozenset({"change_points"})),
    CapabilitySpec("interval_compare", r"\b(compare.*segment|from index \d+.*to index|between indices|more .* than the segment)\b", frozenset({"interval_compare", "step_levels"})),
    CapabilitySpec("lag_causal", r"\b(causal|lag|correlat|lead|follow)\b", frozenset({"lag_corr", "lag_corr_scan"})),
    CapabilitySpec(
        "counterfactual",
        r"\b(if .* (were|was|had|would)|counterfactual|hypothetical|suppose|replace.*segment|scale.*segment)\b",
        frozenset({"counterfactual_simulate"}),
    ),
    CapabilitySpec(
        "extrema_alignment",
        r"\b(align|alignment|same time|simultaneous).*(peak|trough|extrema)|(peak|trough|extrema).*(align|same time)\b",
        frozenset({"extrema_align"}),
    ),
    CapabilitySpec("hurst", r"\bhurst\b", frozenset({"hurst_exponent"})),
    CapabilitySpec(
        "noise_decomp",
        r"\b(residual standard deviation|noise type|uniform|gauss|quantization|random walk)\b",
        frozenset({"noise_decomposition"}),
    ),
    CapabilitySpec("anomaly", r"\b(anomaly|outlier|spike)\b", frozenset({"anomaly_detect"})),
    CapabilitySpec(
        "pairwise_match",
        r"\b(most similar|closest|nearest|robust match)\b",
        frozenset({"pairwise_distance", "robust_shape_match"}),
    ),
    CapabilitySpec("subsequence", r"\b(locate|subsequence|where.*occur)\b", frozenset({"subsequence_locate"})),
    CapabilitySpec("reverse_smooth", r"\b(reversed|smoothed)\b", frozenset({"smooth_reverse_stats", "reverse_match"})),
    CapabilitySpec(
        "caption_align",
        r"\b(select the description|best corresponds to the data|caption)\b",
        frozenset(
            {
                "caption_verify",
                "describe_series",
                "step_levels",
                "local_extrema",
                "fft_period",
                "stl_strength",
                "sliding_stats",
            }
        ),
    ),
)

TASK_TYPE_CAPS: Dict[str, Set[str]] = {
    "stationarity": {"stationarity"},
    "index": {"global_index", "local_extrema_count", "segment_trend", "value_at_index"},
    "choose it": {"pairwise_match"},
    "find it": {"subsequence"},
    "reverse it": {"reverse_smooth"},
    "smooth it": {"reverse_smooth"},
    "caption": {"caption_align"},
    "counterfactual": {"counterfactual"},
}


def _parse_task_types(task_type: Any) -> List[str]:
    if task_type is None:
        return []
    try:
        items = ast.literal_eval(str(task_type)) if isinstance(task_type, str) else task_type
        if isinstance(items, list):
            return [str(x).strip().lower() for x in items]
        return [str(items).strip().lower()]
    except Exception:
        return [str(task_type).strip().lower()]


def infer_capabilities(question: str, task_type: Any, subset: str, question_type: str) -> Set[str]:
    q = (question or "").lower()
    caps: Set[str] = set()
    for spec in CAPABILITIES:
        if re.search(spec.pattern, q, flags=re.I):
            caps.add(spec.name)
    for tt in _parse_task_types(task_type):
        for key, extra in TASK_TYPE_CAPS.items():
            if key in tt:
                caps.update(extra)
    if subset == "Align":
        caps.add("caption_align")
    if subset == "Match":
        for tt in _parse_task_types(task_type):
            for key in ("choose it", "find it", "reverse it", "smooth it"):
                if key in tt:
                    caps.update(TASK_TYPE_CAPS[key])
        # Match-only wording in task_type overrides broad regex misses.
        caps.discard("subsequence")
        caps.discard("pairwise_match")
        caps.discard("reverse_smooth")
        for tt in _parse_task_types(task_type):
            if "choose it" in tt:
                caps.add("pairwise_match")
            if "find it" in tt:
                caps.add("subsequence")
            if "reverse it" in tt or "smooth it" in tt:
                caps.add("reverse_smooth")
    else:
        # Non-Match samples must not require matching-only tools.
        caps -= {"pairwise_match", "subsequence", "reverse_smooth"}
    if question_type == "numerical" and not caps:
        caps.add("describe_basic")
    return caps


def agent_roles_for_sample(subset: str, local_overall: str, capabilities: Set[str]) -> Set[str]:
    roles: Set[str] = set()
    if subset == "Match":
        roles.add("matching")
        return roles
    if subset == "Align":
        roles.add("alignment")
        return roles
    if local_overall == "local" or capabilities.intersection(
        {
            "interval_compare",
            "step_levels",
            "value_at_index",
            "extrema",
            "segment_trend",
            "global_index",
            "crossing_points",
            "counterfactual",
            "extrema_alignment",
        }
    ):
        roles.add("short")
    else:
        roles.update({"short", "medium", "long"})
    roles.update({"structure", "reasoning"})
    return roles


def required_tools_for_capability(cap: str) -> Set[str]:
    for spec in CAPABILITIES:
        if spec.name == cap:
            return set(spec.required_tools)
    return set()


def role_tool_map(registry: Optional[ToolRegistry] = None) -> Dict[str, Set[str]]:
    reg = registry or build_default_registry()
    out: Dict[str, Set[str]] = defaultdict(set)
    for spec in reg._specs.values():
        for role in spec.roles:
            out[role].add(spec.name)
    return dict(out)


def check_sample_coverage(
    *,
    sample_id: str,
    subset: str,
    local_overall: str,
    question: str,
    task_type: Any,
    question_type: str,
    role_tools: Dict[str, Set[str]],
) -> List[Dict[str, Any]]:
    caps = infer_capabilities(question, task_type, subset, question_type)
    roles = agent_roles_for_sample(subset, local_overall, caps)
    gaps: List[Dict[str, Any]] = []
    for cap in sorted(caps):
        needed = required_tools_for_capability(cap)
        if not needed:
            continue
        for role in sorted(roles):
            have = role_tools.get(role, set())
            if not needed.intersection(have):
                gaps.append(
                    {
                        "sample_id": sample_id,
                        "subset": subset,
                        "capability": cap,
                        "role": role,
                        "required_any_of": sorted(needed),
                        "role_has": sorted(have),
                    }
                )
    return gaps


def audit_mmts_dataset(
    processed_dir: str | Path,
    raw_dir: str | Path,
    registry: Optional[ToolRegistry] = None,
) -> Dict[str, Any]:
    processed_dir = Path(processed_dir)
    raw_dir = Path(raw_dir)
    index_path = processed_dir / "index.jsonl"
    rows = [json.loads(line) for line in index_path.read_text().splitlines() if line.strip()]
    role_tools = role_tool_map(registry)
    cache: Dict[str, pd.DataFrame] = {}
    all_gaps: List[Dict[str, Any]] = []
    cap_counts: Counter[str] = Counter()

    for meta in rows:
        src = meta["source_file"]
        if src not in cache:
            cache[src] = pd.read_csv(raw_dir / src)
        row = cache[src].iloc[int(meta["row_index"])]
        question = str(row.get("question", ""))
        caps = infer_capabilities(question, row.get("task_type"), meta["subset"], meta["question_type"])
        for c in caps:
            cap_counts[c] += 1
        gaps = check_sample_coverage(
            sample_id=meta["sample_id"],
            subset=meta["subset"],
            local_overall=str(meta.get("local_overall", "")),
            question=question,
            task_type=row.get("task_type"),
            question_type=meta["question_type"],
            role_tools=role_tools,
        )
        all_gaps.extend(gaps)

    gap_by_cap = Counter(g["capability"] for g in all_gaps)
    return {
        "n_samples": len(rows),
        "n_gaps": len(all_gaps),
        "n_samples_with_gaps": len({g["sample_id"] for g in all_gaps}),
        "capability_counts": dict(cap_counts),
        "gap_by_capability": dict(gap_by_cap),
        "gaps": all_gaps,
        "role_tool_counts": {k: len(v) for k, v in sorted(role_tools.items())},
    }
