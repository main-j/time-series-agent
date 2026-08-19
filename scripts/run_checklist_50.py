#!/usr/bin/env python3
"""Select a proportional 50-sample subset from the weighted 200 and run it."""
from __future__ import annotations

import argparse
import hashlib
import json
import random
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, Iterable, List, Sequence


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = ROOT / "outputs" / "weighted_mmts_selection_200" / "manifest.json"
DEFAULT_OUTPUT = ROOT / "outputs" / "weighted_mmts_selection_50"
DIVERSITY_FIELDS = (
    "qa_type",
    "local_overall",
    "is_univariate",
    "domain",
    "freq",
    "answer",
)


def _stable_seed(seed: int, label: str) -> int:
    digest = hashlib.sha256(f"{seed}:{label}".encode("utf-8")).hexdigest()
    return int(digest[:16], 16)


def _allocate_proportionally(counts: Dict[str, int], target: int) -> Dict[str, int]:
    """Allocate target slots with Hamilton's largest-remainder method."""
    total = sum(counts.values())
    if target < 1:
        raise ValueError("count must be positive")
    if target > total:
        raise ValueError(f"count={target} exceeds source size={total}")

    exact = {key: value * target / total for key, value in counts.items()}
    allocated = {key: int(value) for key, value in exact.items()}
    remaining = target - sum(allocated.values())
    order = sorted(
        counts,
        key=lambda key: (-(exact[key] - allocated[key]), -counts[key], key),
    )
    for key in order[:remaining]:
        allocated[key] += 1
    return allocated


def _diverse_pick(
    rows: Sequence[Dict[str, Any]],
    count: int,
    *,
    seed: int,
) -> List[Dict[str, Any]]:
    remaining = list(rows)
    rng = random.Random(seed)
    rng.shuffle(remaining)
    selected: List[Dict[str, Any]] = []
    value_counts: Dict[str, Counter[str]] = defaultdict(Counter)
    while remaining and len(selected) < count:
        best = max(
            remaining,
            key=lambda row: (
                sum(
                    1.0 / (1.0 + value_counts[field][str(row.get(field))])
                    for field in DIVERSITY_FIELDS
                )
                + rng.random() * 1e-6
            ),
        )
        selected.append(best)
        remaining.remove(best)
        for field in DIVERSITY_FIELDS:
            value_counts[field][str(best.get(field))] += 1
    return selected


def select_subset(
    rows: Sequence[Dict[str, Any]],
    *,
    count: int,
    seed: int,
) -> tuple[List[Dict[str, Any]], Dict[str, int]]:
    groups: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for row in rows:
        task = str(row.get("assigned_task") or "")
        if not task:
            raise ValueError(f"sample lacks assigned_task: {row.get('sample_id')}")
        groups[task].append(dict(row))

    quotas = _allocate_proportionally(
        {task: len(group) for task, group in groups.items()},
        count,
    )
    selected: List[Dict[str, Any]] = []
    for task, group in groups.items():
        quota = quotas[task]
        errors = [row for row in group if row.get("historical_architecture_correct") is False]
        others = [row for row in group if row.get("historical_architecture_correct") is not False]
        error_quota = min(len(errors), round(len(errors) * quota / len(group)))
        task_seed = _stable_seed(seed, task)
        picked = _diverse_pick(errors, error_quota, seed=task_seed)
        picked += _diverse_pick(
            others,
            quota - len(picked),
            seed=_stable_seed(seed, f"{task}:other"),
        )
        if len(picked) < quota:
            picked_ids = {row["sample_id"] for row in picked}
            remainder = [row for row in group if row["sample_id"] not in picked_ids]
            picked += _diverse_pick(
                remainder,
                quota - len(picked),
                seed=_stable_seed(seed, f"{task}:remainder"),
            )
        random.Random(task_seed).shuffle(picked)
        selected.extend(picked)

    if len(selected) != count:
        raise RuntimeError(f"selected {len(selected)} samples, expected {count}")
    if len({row["sample_id"] for row in selected}) != count:
        raise RuntimeError("selection contains duplicate sample IDs")
    return selected, quotas


def _distribution(rows: Iterable[Dict[str, Any]], field: str) -> Dict[str, int]:
    return dict(Counter(str(row.get(field)) for row in rows))


def write_selection(
    *,
    source_manifest: Path,
    output_dir: Path,
    count: int,
    seed: int,
) -> List[Dict[str, Any]]:
    source = json.loads(source_manifest.read_text(encoding="utf-8"))
    source_rows = source.get("samples")
    if not isinstance(source_rows, list) or not source_rows:
        raise ValueError(f"manifest has no samples: {source_manifest}")

    selected, quotas = select_subset(source_rows, count=count, seed=seed)
    output_dir.mkdir(parents=True, exist_ok=True)
    sample_ids = [str(row["sample_id"]) for row in selected]
    (output_dir / "sample_ids.txt").write_text(
        "\n".join(sample_ids) + "\n",
        encoding="utf-8",
    )

    manifest = {
        "name": f"weighted_mmts_regression_{count}",
        "seed": seed,
        "source_manifest": str(source_manifest),
        "source_size": len(source_rows),
        "n_unique_samples": len(selected),
        "selection_policy": {
            "primary_stratum": "assigned_task",
            "quota_method": "Hamilton largest remainder",
            "historical_error_ratio": "preserved within each stratum by rounded quota",
            "diversity_fields": list(DIVERSITY_FIELDS),
        },
        "task_quotas": quotas,
        "source_distributions": {
            field: _distribution(source_rows, field)
            for field in ("assigned_task", "subset", "qa_type", "local_overall", "domain")
        },
        "selected_distributions": {
            field: _distribution(selected, field)
            for field in ("assigned_task", "subset", "qa_type", "local_overall", "domain")
        },
        "samples": selected,
    }
    (output_dir / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    report = [
        f"# Weighted proportional subset ({count}/{len(source_rows)})",
        "",
        f"- Seed: `{seed}`",
        f"- Source: `{source_manifest}`",
        "- Primary stratum: `assigned_task`",
        "- Allocation: Hamilton largest-remainder method",
        "",
        "| assigned_task | source | selected |",
        "|---|---:|---:|",
    ]
    source_task_counts = _distribution(source_rows, "assigned_task")
    for task, quota in quotas.items():
        report.append(f"| {task} | {source_task_counts[task]} | {quota} |")
    report.extend(["", f"Total: **{len(selected)}** samples.", ""])
    (output_dir / "report.md").write_text("\n".join(report), encoding="utf-8")
    return selected


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Select a proportional subset from weighted_mmts_selection_200 and run it."
    )
    parser.add_argument("--source-manifest", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--count", type=int, default=50)
    parser.add_argument("--seed", type=int, default=20260803)
    parser.add_argument("--select-only", action="store_true")
    parser.add_argument("--exp-name", default="checklist_weighted_50")
    parser.add_argument("--device", default="cuda:0")
    parser.add_argument("--run-baseline", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    selected = write_selection(
        source_manifest=args.source_manifest.resolve(),
        output_dir=args.output_dir.resolve(),
        count=args.count,
        seed=args.seed,
    )
    checklist = args.output_dir.resolve() / "sample_ids.txt"
    print(f"[ok] selected {len(selected)} samples -> {checklist}", flush=True)
    if args.select_only:
        return

    command = [
        sys.executable,
        str(ROOT / "scripts" / "run_checklist_batch.py"),
        "--checklist-file",
        str(checklist),
        "--no-exclude-feasibility",
        "--exp-name",
        args.exp_name,
        "--device",
        args.device,
        "--resume",
    ]
    if args.run_baseline:
        command.append("--run-baseline")
    print(f"[run] {' '.join(command)}", flush=True)
    subprocess.run(command, cwd=ROOT, check=True)


if __name__ == "__main__":
    main()
