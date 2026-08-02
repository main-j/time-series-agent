#!/usr/bin/env python3
"""Build a reproducible 200-sample MMTS regression set weighted toward weak tasks."""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
import random
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "mmts-bench" / "Benchmark"
DEFAULT_HISTORY = Path("/root/autodl-tmp/ts-agent-paper-repro/results/mmts_full_agent.jsonl")

# Weakest tasks are selected first so overlapping samples are reserved for them.
QUOTAS: Dict[str, int] = {
    "CrossModal/Semantic→TS": 20,
    "Structural/Non-Stationarity": 16,
    "CrossModal/TS→Semantic": 16,
    "Matching/Localization": 14,
    "Feature/Season.": 12,
    "Feature/Noise": 12,
    "Feature/Volat.": 12,
    "Reasoning/Count.": 12,
    "Feature/Trend": 10,
    "Reasoning/Ded.": 10,
    "Reasoning/Ind.": 10,
    "Reasoning/Analog.": 10,
    "Feature/Basic": 8,
    "Reasoning/Causal": 8,
    "Structural/Local-Global": 6,
    "Structural/Uni.-Multi.": 6,
    "Matching/Robust": 6,
    "Matching/Isomorphic": 6,
    "Matching/Reverse": 6,
}

BASELINE_SUBSET_ACCURACY = {
    "Base": 0.37662337662337664,
    "InWild": 0.5267527675276753,
    "Match": 0.5475,
    "Align_ts2caption": 0.8458333333333333,
    "Align_caption2ts": 0.8458333333333333,
}


@dataclass(frozen=True)
class Item:
    sample_id: str
    history_source: str
    history_id: int
    subset: str
    row_index: int
    question: str
    answer: str
    task_type: str
    qa_type: str
    local_overall: str
    is_univariate: bool
    domain: str
    freq: str


def _task_types(value: Any) -> List[str]:
    try:
        parsed = ast.literal_eval(str(value))
        values = parsed if isinstance(parsed, list) else [parsed]
    except Exception:
        values = [value]
    return [str(x).strip().lower() for x in values]


def _stable_seed(seed: int, task: str) -> int:
    digest = hashlib.sha256(f"{seed}:{task}".encode()).hexdigest()
    return int(digest[:16], 16)


def _load_history(path: Path) -> Dict[tuple[str, int], bool]:
    if not path.exists():
        return {}
    out: Dict[tuple[str, int], bool] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        out[(str(row["source"]), int(row["id"]))] = bool(row.get("agent", {}).get("correct"))
    return out


def _make_item(
    *,
    subset: str,
    file_stem: str,
    history_source: str,
    row_index: int,
    row: pd.Series,
) -> Item:
    return Item(
        sample_id=f"{subset}:{file_stem}:{row_index}",
        history_source=history_source,
        history_id=int(row["num"]),
        subset=subset,
        row_index=row_index,
        question=str(row.get("question", "")),
        answer=str(row.get("answer", "")),
        task_type=str(row.get("task_type", "")),
        qa_type=str(row.get("qa_type", "")),
        local_overall=str(row.get("local_overall", "")),
        is_univariate=bool(row.get("is_univariate", True)),
        domain=str(row.get("domain", "")),
        freq=str(row.get("freq", "")),
    )


def build_pools() -> Dict[str, List[Item]]:
    frames = {
        "Base": (
            pd.read_csv(RAW / "Base" / "synthtic_qa_700.csv"),
            "synthtic_qa_700",
            "Base",
        ),
        "InWild": (
            pd.read_csv(RAW / "InWild" / "tsqa_1084.csv"),
            "tsqa_1084",
            "InWild",
        ),
        "Match": (
            pd.read_csv(RAW / "Match" / "qats_400.csv"),
            "qats_400",
            "Match",
        ),
        "AlignTS": (
            pd.read_csv(RAW / "Align" / "ts2caption_qa_120.csv"),
            "ts2caption_qa_120",
            "Align_ts2caption",
        ),
        "AlignCaption": (
            pd.read_csv(RAW / "Align" / "caption2ts_qa_120.csv"),
            "caption2ts_qa_120",
            "Align_caption2ts",
        ),
    }
    all_items: Dict[str, List[Item]] = {}
    for name, (frame, stem, history_source) in frames.items():
        subset = "Align" if name.startswith("Align") else name
        all_items[name] = [
            _make_item(
                subset=subset,
                file_stem=stem,
                history_source=history_source,
                row_index=i,
                row=row,
            )
            for i, row in frame.iterrows()
        ]

    pools: Dict[str, List[Item]] = defaultdict(list)
    for item in all_items["Base"]:
        tags = _task_types(item.task_type)
        if any("stationarity" in tag for tag in tags):
            pools["Structural/Non-Stationarity"].append(item)
        if any("index" in tag for tag in tags):
            pools["Structural/Local-Global"].append(item)
        pools["Structural/Uni.-Multi."].append(item)

    feature_map = {
        "Feature/Trend": "trend",
        "Feature/Season.": "season",
        "Feature/Noise": "noise",
        "Feature/Volat.": "volatility",
        "Feature/Basic": "basic",
    }
    for item in all_items["Base"] + all_items["InWild"]:
        tags = _task_types(item.task_type)
        for task, needle in feature_map.items():
            if any(needle in tag for tag in tags):
                pools[task].append(item)

    reasoning_map = {
        "Reasoning/Ded.": "deductive",
        "Reasoning/Ind.": "inductive",
        "Reasoning/Causal": "causal",
        "Reasoning/Analog.": "analogical",
        "Reasoning/Count.": "counterfactual",
    }
    for item in all_items["InWild"]:
        tags = _task_types(item.task_type)
        for task, needle in reasoning_map.items():
            if any(needle in tag for tag in tags):
                pools[task].append(item)

    matching_map = {
        "Matching/Isomorphic": "choose it",
        "Matching/Robust": "smooth it",
        "Matching/Localization": "find it",
        "Matching/Reverse": "reverse it",
    }
    for item in all_items["Match"]:
        tags = _task_types(item.task_type)
        for task, needle in matching_map.items():
            if any(needle in tag for tag in tags):
                pools[task].append(item)

    pools["CrossModal/TS→Semantic"] = all_items["AlignTS"]
    pools["CrossModal/Semantic→TS"] = all_items["AlignCaption"]
    return dict(pools)


def _diverse_pick(items: List[Item], n: int, rng: random.Random) -> List[Item]:
    remaining = list(items)
    rng.shuffle(remaining)
    selected: List[Item] = []
    value_counts: Dict[str, Counter[str]] = defaultdict(Counter)
    attrs = ("qa_type", "local_overall", "is_univariate", "domain", "freq", "answer")
    while remaining and len(selected) < n:
        best: Optional[Item] = None
        best_score = float("-inf")
        for item in remaining:
            score = 0.0
            for attr in attrs:
                value = str(getattr(item, attr))
                score += 1.0 / (1.0 + value_counts[attr][value])
            score += rng.random() * 1e-6
            if score > best_score:
                best, best_score = item, score
        assert best is not None
        selected.append(best)
        remaining.remove(best)
        for attr in attrs:
            value_counts[attr][str(getattr(best, attr))] += 1
    return selected


def select_samples(
    pools: Dict[str, List[Item]],
    history: Dict[tuple[str, int], bool],
    *,
    seed: int,
) -> tuple[List[Dict[str, Any]], Dict[str, Dict[str, Any]]]:
    used: set[str] = set()
    selected_rows: List[Dict[str, Any]] = []
    stats: Dict[str, Dict[str, Any]] = {}
    membership: Dict[str, List[str]] = defaultdict(list)
    for task, items in pools.items():
        for item in items:
            membership[item.sample_id].append(task)

    for task, quota in QUOTAS.items():
        rng = random.Random(_stable_seed(seed, task))
        available = [item for item in pools[task] if item.sample_id not in used]
        historical_errors = [
            item for item in available if history.get((item.history_source, item.history_id)) is False
        ]
        historical_correct = [
            item for item in available if history.get((item.history_source, item.history_id)) is True
        ]
        unknown = [
            item for item in available if (item.history_source, item.history_id) not in history
        ]
        target_errors = min(len(historical_errors), round(quota * 0.7))
        picked = _diverse_pick(historical_errors, target_errors, rng)
        needed = quota - len(picked)
        picked += _diverse_pick(historical_correct, needed, rng)
        needed = quota - len(picked)
        if needed:
            picked += _diverse_pick(unknown, needed, rng)
        needed = quota - len(picked)
        if needed:
            leftovers = [item for item in available if item not in picked]
            picked += _diverse_pick(leftovers, needed, rng)
        if len(picked) != quota:
            raise RuntimeError(f"{task}: requested {quota}, selected {len(picked)}")

        historical_values = [
            history[(item.history_source, item.history_id)]
            for item in pools[task]
            if (item.history_source, item.history_id) in history
        ]
        architecture_accuracy = (
            sum(historical_values) / len(historical_values) if historical_values else None
        )
        baseline_reference = sum(
            BASELINE_SUBSET_ACCURACY[item.history_source] for item in pools[task]
        ) / len(pools[task])
        stats[task] = {
            "pool_size": len(pools[task]),
            "quota": quota,
            "sample_rate": quota / len(pools[task]),
            "historical_architecture_accuracy": architecture_accuracy,
            "baseline_subset_reference": baseline_reference,
            "architecture_minus_baseline_reference": (
                architecture_accuracy - baseline_reference
                if architecture_accuracy is not None
                else None
            ),
            "historical_error_count": (
                len(historical_values) - sum(historical_values) if historical_values else None
            ),
            "selected_historical_errors": sum(
                history.get((item.history_source, item.history_id)) is False for item in picked
            ),
        }
        for item in picked:
            used.add(item.sample_id)
            previous = history.get((item.history_source, item.history_id))
            selected_rows.append(
                {
                    "sample_id": item.sample_id,
                    "assigned_task": task,
                    "all_task_tags": sorted(membership[item.sample_id]),
                    "subset": item.subset,
                    "row_index": item.row_index,
                    "task_type": item.task_type,
                    "qa_type": item.qa_type,
                    "local_overall": item.local_overall,
                    "is_univariate": item.is_univariate,
                    "domain": item.domain,
                    "freq": item.freq,
                    "answer": item.answer,
                    "historical_architecture_correct": previous,
                    "question": item.question,
                }
            )
    return selected_rows, stats


def _fmt_pct(value: Optional[float]) -> str:
    return "—" if value is None else f"{100 * value:.1f}%"


def write_outputs(
    out_dir: Path,
    *,
    seed: int,
    history_path: Path,
    selected: List[Dict[str, Any]],
    stats: Dict[str, Dict[str, Any]],
) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    payload = {
        "name": "weighted_mmts_regression_200",
        "seed": seed,
        "n_unique_samples": len(selected),
        "selection_policy": {
            "minimum_per_task": 6,
            "weak_task_oversampling": "12-20 samples for high-error or below-baseline strata",
            "historical_error_target": "approximately 70% per stratum when available",
            "deduplication": "each physical sample assigned to exactly one primary stratum",
            "diversity_fields": [
                "qa_type",
                "local_overall",
                "is_univariate",
                "domain",
                "freq",
                "answer",
            ],
            "history_source": str(history_path),
            "recommended_run_chunks": "4 chunks × 50 samples for checkpointing",
            "baseline_caveat": (
                "Task-level architecture accuracy comes from the historical full TS-Agent run; "
                "baseline references are subset-level choice accuracies, so gaps are prioritization "
                "signals rather than paired significance estimates."
            ),
        },
        "task_stats": stats,
        "samples": selected,
    }
    (out_dir / "manifest.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (out_dir / "sample_ids.txt").write_text(
        "\n".join(row["sample_id"] for row in selected) + "\n", encoding="utf-8"
    )
    for chunk_index in range(0, len(selected), 50):
        chunk = selected[chunk_index : chunk_index + 50]
        chunk_name = f"sample_ids_chunk_{chunk_index // 50 + 1:02d}.txt"
        (out_dir / chunk_name).write_text(
            "\n".join(row["sample_id"] for row in chunk) + "\n", encoding="utf-8"
        )

    lines = [
        "# Weighted MMTS regression selection (200 unique samples)",
        "",
        f"- Seed: `{seed}`",
        f"- Historical run: `{history_path}`",
        "- Policy: every taxonomy task has a minimum quota; weak and below-baseline strata are oversampled.",
        "- Caveat: baseline references are subset-level choice accuracies, not paired per-task predictions.",
        "",
        "| task | pool | quota | rate | historical arch | baseline ref | gap | historical errors | selected old errors |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for task, row in stats.items():
        lines.append(
            f"| {task} | {row['pool_size']} | {row['quota']} | {_fmt_pct(row['sample_rate'])} | "
            f"{_fmt_pct(row['historical_architecture_accuracy'])} | "
            f"{_fmt_pct(row['baseline_subset_reference'])} | "
            f"{_fmt_pct(row['architecture_minus_baseline_reference'])} | "
            f"{row['historical_error_count']} | {row['selected_historical_errors']} |"
        )
    lines.extend(["", "## Selected samples", ""])
    by_task: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for row in selected:
        by_task[row["assigned_task"]].append(row)
    for task in QUOTAS:
        lines.append(f"### {task}")
        lines.append("")
        for row in by_task[task]:
            marker = "old-error" if row["historical_architecture_correct"] is False else "control"
            lines.append(f"- `{row['sample_id']}` · {marker} · {row['task_type']}")
        lines.append("")
    (out_dir / "report.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=20260802)
    parser.add_argument("--history", type=Path, default=DEFAULT_HISTORY)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=ROOT / "outputs" / "weighted_mmts_selection_200",
    )
    args = parser.parse_args()
    pools = build_pools()
    missing = sorted(set(QUOTAS) - set(pools))
    if missing:
        raise SystemExit(f"missing task pools: {missing}")
    history = _load_history(args.history)
    selected, stats = select_samples(pools, history, seed=args.seed)
    if len(selected) != sum(QUOTAS.values()) or len({x["sample_id"] for x in selected}) != len(selected):
        raise SystemExit("selection is not exactly 200 unique samples")
    write_outputs(
        args.output_dir,
        seed=args.seed,
        history_path=args.history,
        selected=selected,
        stats=stats,
    )
    print(f"wrote {len(selected)} unique samples to {args.output_dir}")


if __name__ == "__main__":
    main()
