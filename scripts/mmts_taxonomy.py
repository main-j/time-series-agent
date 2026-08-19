"""MMTS-Bench taxonomy: map samples to dimension / task for evaluation reporting."""
from __future__ import annotations

import ast
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Official MMTS taxonomy (dimension, task label, internal key, primary subset).
TAXONOMY_TABLE: List[Tuple[str, str, str, str]] = [
    ("Structural Awareness", "Non-Stationarity", "Structural/Non-Stationarity", "Base"),
    ("Structural Awareness", "Local-Global", "Structural/Local-Global", "Base"),
    ("Structural Awareness", "Uni.-Multi.", "Structural/Uni.-Multi.", "Base"),
    ("Feature Analysis", "Trend", "Feature/Trend", "Base & InWild"),
    ("Feature Analysis", "Season.", "Feature/Season.", "Base & InWild"),
    ("Feature Analysis", "Noise", "Feature/Noise", "Base & InWild"),
    ("Feature Analysis", "Volat.", "Feature/Volat.", "Base & InWild"),
    ("Feature Analysis", "Basic", "Feature/Basic", "Base & InWild"),
    ("Temporal Reasoning", "Ded.", "Reasoning/Ded.", "InWild"),
    ("Temporal Reasoning", "Ind.", "Reasoning/Ind.", "InWild"),
    ("Temporal Reasoning", "Causal", "Reasoning/Causal", "InWild"),
    ("Temporal Reasoning", "Analog.", "Reasoning/Analog.", "InWild"),
    ("Temporal Reasoning", "Count.", "Reasoning/Count.", "InWild"),
    ("Sequence Matching", "Isomorphic", "Matching/Isomorphic", "Match"),
    ("Sequence Matching", "Robust", "Matching/Robust", "Match"),
    ("Sequence Matching", "Localization", "Matching/Localization", "Match"),
    ("Sequence Matching", "Reverse", "Matching/Reverse", "Match"),
    ("Cross-Modal Understanding", "TS→Semantic", "CrossModal/TS→Semantic", "Align"),
    ("Cross-Modal Understanding", "Semantic→TS", "CrossModal/Semantic→TS", "Align"),
]

TASK_KEYS: List[str] = [row[2] for row in TAXONOMY_TABLE]
TASK_LABEL: Dict[str, str] = {row[2]: row[1] for row in TAXONOMY_TABLE}
TASK_DIMENSION: Dict[str, str] = {row[2]: row[0] for row in TAXONOMY_TABLE}
TASK_SUBSET_HINT: Dict[str, str] = {row[2]: row[3] for row in TAXONOMY_TABLE}

SUBSET_ORDER = ["Base", "InWild", "Match", "Align"]


def parse_task_tags(task_type: Any) -> List[str]:
    try:
        parsed = ast.literal_eval(str(task_type))
        values = parsed if isinstance(parsed, list) else [parsed]
    except Exception:
        values = [task_type]
    return [str(x).strip().lower() for x in values]


def normalize_subset(value: Any, sample_id: str = "") -> str:
    text = str(value or "")
    if "." in text:
        text = text.rsplit(".", 1)[-1]
    text = text.strip()
    if text in SUBSET_ORDER:
        return text
    sid = str(sample_id)
    if sid.startswith("Align:"):
        return "Align"
    if sid.startswith("Base:"):
        return "Base"
    if sid.startswith("InWild:"):
        return "InWild"
    if sid.startswith("Match:"):
        return "Match"
    return text or "Unknown"


def taxonomy_tasks_for_sample(
    sample_id: str,
    subset: Any,
    task_type: Any,
) -> List[str]:
    """Return all taxonomy task keys a sample belongs to (pool membership)."""
    sid = str(sample_id)
    sub = normalize_subset(subset, sid)
    tags = parse_task_tags(task_type)
    tasks: List[str] = []

    if sub == "Base":
        if any("stationarity" in tag for tag in tags):
            tasks.append("Structural/Non-Stationarity")
        if any("index" in tag for tag in tags):
            tasks.append("Structural/Local-Global")
        tasks.append("Structural/Uni.-Multi.")

    feature_map = {
        "Feature/Trend": "trend",
        "Feature/Season.": "season",
        "Feature/Noise": "noise",
        "Feature/Volat.": "volatility",
        "Feature/Basic": "basic",
    }
    if sub in {"Base", "InWild"}:
        for task, needle in feature_map.items():
            if any(needle in tag for tag in tags):
                tasks.append(task)

    if sub == "InWild":
        reasoning_map = {
            "Reasoning/Ded.": "deductive",
            "Reasoning/Ind.": "inductive",
            "Reasoning/Causal": "causal",
            "Reasoning/Analog.": "analogical",
            "Reasoning/Count.": "counterfactual",
        }
        for task, needle in reasoning_map.items():
            if any(needle in tag for tag in tags):
                tasks.append(task)

    if sub == "Match":
        matching_map = {
            "Matching/Isomorphic": "choose it",
            "Matching/Robust": "smooth it",
            "Matching/Localization": "find it",
            "Matching/Reverse": "reverse it",
        }
        for task, needle in matching_map.items():
            if any(needle in tag for tag in tags):
                tasks.append(task)

    if sub == "Align":
        if "ts2caption" in sid:
            tasks.append("CrossModal/TS→Semantic")
        elif "caption2ts" in sid:
            tasks.append("CrossModal/Semantic→TS")

    # Preserve table order, dedupe.
    seen: set[str] = set()
    ordered: List[str] = []
    for key in TASK_KEYS:
        if key in tasks and key not in seen:
            ordered.append(key)
            seen.add(key)
    return ordered


def _acc(ok: int, n: int) -> float:
    return ok / n if n else 0.0


def _bucket() -> Dict[str, int]:
    return {"n": 0, "arch_ok": 0, "base_ok": 0}


def compute_evaluation_stats(rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Compute overall, subset, task, and dimension statistics."""
    present = [r for r in rows if r.get("source") != "missing"]
    n_total = len(rows)
    n_present = len(present)

    n_arch = sum(1 for r in present if r.get("arch_ok"))
    n_base = sum(1 for r in present if r.get("baseline_ok"))

    by_subset: Dict[str, Dict[str, int]] = {s: _bucket() for s in SUBSET_ORDER}
    by_task: Dict[str, Dict[str, int]] = {k: _bucket() for k in TASK_KEYS}
    by_dimension: Dict[str, Dict[str, int]] = defaultdict(_bucket)

    enriched: List[Dict[str, Any]] = []
    for row in rows:
        sid = str(row.get("sample_id", ""))
        subset = normalize_subset(row.get("subset"), sid)
        task_keys = taxonomy_tasks_for_sample(sid, subset, row.get("task_type"))
        enriched_row = dict(row)
        enriched_row["subset_norm"] = subset
        enriched_row["taxonomy_tasks"] = task_keys
        enriched.append(enriched_row)

        if row.get("source") == "missing":
            continue

        if subset in by_subset:
            by_subset[subset]["n"] += 1
            if row.get("arch_ok"):
                by_subset[subset]["arch_ok"] += 1
            if row.get("baseline_ok"):
                by_subset[subset]["base_ok"] += 1

        seen_tasks: set[str] = set()
        for task_key in task_keys:
            if task_key in seen_tasks:
                continue
            seen_tasks.add(task_key)
            by_task[task_key]["n"] += 1
            if row.get("arch_ok"):
                by_task[task_key]["arch_ok"] += 1
            if row.get("baseline_ok"):
                by_task[task_key]["base_ok"] += 1
            dim = TASK_DIMENSION[task_key]
            by_dimension[dim]["n"] += 1
            if row.get("arch_ok"):
                by_dimension[dim]["arch_ok"] += 1
            if row.get("baseline_ok"):
                by_dimension[dim]["base_ok"] += 1

    def _finalize_group(group: Dict[str, Dict[str, int]]) -> Dict[str, Any]:
        out: Dict[str, Any] = {}
        for name, b in group.items():
            n = b["n"]
            out[name] = {
                **b,
                "arch_acc": _acc(b["arch_ok"], n),
                "base_acc": _acc(b["base_ok"], n),
            }
        return out

    task_rows: List[Dict[str, Any]] = []
    for dim, label, key, subset_hint in TAXONOMY_TABLE:
        b = by_task[key]
        task_rows.append(
            {
                "dimension": dim,
                "task": label,
                "task_key": key,
                "subset_hint": subset_hint,
                **b,
                "arch_acc": _acc(b["arch_ok"], b["n"]),
                "base_acc": _acc(b["base_ok"], b["n"]),
            }
        )

    return {
        "total": n_total,
        "present": n_present,
        "architecture_correct": n_arch,
        "baseline_correct": n_base,
        "architecture_accuracy": _acc(n_arch, n_present),
        "baseline_accuracy": _acc(n_base, n_present),
        "by_subset": _finalize_group(by_subset),
        "by_task": _finalize_group(by_task),
        "by_dimension": _finalize_group(dict(by_dimension)),
        "task_rows": task_rows,
        "enriched_rows": enriched,
    }


def write_stats_markdown(
    path: Any,
    stats: Dict[str, Any],
    *,
    title: str,
    extra_lines: Optional[List[str]] = None,
) -> None:
    lines = [f"# {title}", ""]
    if extra_lines:
        lines.extend(extra_lines)
        lines.append("")

    lines.extend(
        [
            "## Overall",
            "",
            f"- Architecture: **{stats['architecture_correct']}/{stats['present']}** "
            f"({stats['architecture_accuracy']:.1%})",
            f"- Baseline: **{stats['baseline_correct']}/{stats['present']}** "
            f"({stats['baseline_accuracy']:.1%})",
            "",
            "## By subset",
            "",
            "| Subset | n | arch_ok | base_ok | arch_acc | base_acc |",
            "|---|---:|---:|---:|---:|---:|",
        ]
    )
    for subset in SUBSET_ORDER:
        s = stats["by_subset"].get(subset, _bucket())
        n = s["n"]
        if n == 0:
            continue
        lines.append(
            f"| {subset} | {n} | {s['arch_ok']} | {s['base_ok']} | "
            f"{s['arch_acc']:.1%} | {s['base_acc']:.1%} |"
        )

    lines.extend(
        [
            "",
            "## By task (MMTS taxonomy)",
            "",
            "| Dimension | Task | Subset | n | arch_ok | base_ok | arch_acc | base_acc |",
            "|---|---|---|---:|---:|---:|---:|---:|",
        ]
    )
    for row in stats["task_rows"]:
        lines.append(
            f"| {row['dimension']} | {row['task']} | {row['subset_hint']} | {row['n']} | "
            f"{row['arch_ok']} | {row['base_ok']} | {row['arch_acc']:.1%} | {row['base_acc']:.1%} |"
        )

    lines.extend(
        [
            "",
            "## By dimension (pool aggregate; samples may appear in multiple tasks within a dimension)",
            "",
            "| Dimension | n | arch_ok | base_ok | arch_acc | base_acc |",
            "|---|---:|---:|---:|---:|---:|",
        ]
    )
    printed: set[str] = set()
    for dim, _label, _key, _hint in TAXONOMY_TABLE:
        if dim in printed:
            continue
        printed.add(dim)
        s = stats["by_dimension"].get(dim, _bucket())
        n = s["n"]
        if n == 0:
            continue
        lines.append(
            f"| {dim} | {n} | {s['arch_ok']} | {s['base_ok']} | "
            f"{s['arch_acc']:.1%} | {s['base_acc']:.1%} |"
        )

    Path(path).write_text("\n".join(lines), encoding="utf-8")
