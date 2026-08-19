#!/usr/bin/env python3
"""Select N samples per MMTS taxonomy task (across all subsets).

Writes:
  outputs/<out-name>/manifest.json   task_key -> [sample_id, ...]
  outputs/<out-name>/sample_ids.txt  deduplicated run list
  outputs/<out-name>/selection.md    human-readable table
"""
from __future__ import annotations

import argparse
import hashlib
import json
import random
import sys
from collections import defaultdict
from pathlib import Path
from typing import Dict, List

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from mmts_taxonomy import (  # noqa: E402
    SUBSET_ORDER,
    TASK_DIMENSION,
    TASK_KEYS,
    TASK_LABEL,
    TASK_SUBSET_HINT,
    normalize_subset,
    taxonomy_tasks_for_sample,
)

INDEX = ROOT / "data" / "processed" / "mmts-bench" / "index.jsonl"
DEFAULT_OUT = ROOT / "outputs" / "per_task_2x_v1"
SEED = 20260803


def _stable_seed(seed: int, task: str) -> int:
    digest = hashlib.sha256(f"{seed}:{task}".encode()).hexdigest()
    return int(digest[:16], 16)


def _load_index() -> List[dict]:
    rows: List[dict] = []
    for line in INDEX.read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows


def _build_task_pools(rows: List[dict]) -> Dict[str, List[str]]:
    pools: Dict[str, List[str]] = defaultdict(list)
    for row in rows:
        sid = str(row["sample_id"])
        tasks = taxonomy_tasks_for_sample(sid, row.get("subset"), row.get("task_type"))
        for task in tasks:
            pools[task].append(sid)
    return {task: sorted(set(ids)) for task, ids in pools.items()}


def _pick(ids: List[str], k: int, seed: int, task: str) -> List[str]:
    if k <= 0 or not ids:
        return []
    rng = random.Random(_stable_seed(seed, task))
    pool = ids[:]
    rng.shuffle(pool)
    return pool[: min(k, len(pool))]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--per-task", type=int, default=2, help="Samples per taxonomy task.")
    parser.add_argument("--seed", type=int, default=SEED)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()

    rows = _load_index()
    row_by_id = {str(r["sample_id"]): r for r in rows}
    pools = _build_task_pools(rows)

    manifest: Dict[str, List[str]] = {}
    ordered: List[str] = []
    for task in TASK_KEYS:
        picked = _pick(pools.get(task, []), args.per_task, args.seed, task)
        manifest[task] = picked
        ordered.extend(picked)

    unique = list(dict.fromkeys(ordered))
    out_dir = args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (out_dir / "sample_ids.txt").write_text(
        "\n".join(unique) + ("\n" if unique else ""),
        encoding="utf-8",
    )

    lines = [
        f"# Per-task selection ({args.per_task} per task, seed={args.seed})",
        "",
        f"- Taxonomy tasks: {len(TASK_KEYS)}",
        f"- Total picks (with duplicates): {len(ordered)}",
        f"- Unique samples to run: {len(unique)}",
        "",
        "| Task | Subset | Pool | Picked | Sample IDs |",
        "|---|---|---|---:|---|",
    ]
    for task in TASK_KEYS:
        picked = manifest[task]
        pool_n = len(pools.get(task, []))
        sid_cells = ", ".join(f"`{s}`" for s in picked) if picked else "(empty)"
        lines.append(
            f"| {TASK_LABEL[task]} | {TASK_SUBSET_HINT[task]} | {pool_n} | {len(picked)} | {sid_cells} |"
        )

    lines.extend(["", "## By subset (unique samples)", ""])
    by_subset: Dict[str, List[str]] = {s: [] for s in SUBSET_ORDER}
    for sid in unique:
        row = row_by_id.get(sid, {})
        sub = normalize_subset(row.get("subset"), sid)
        if sub in by_subset:
            by_subset[sub].append(sid)
    for sub in SUBSET_ORDER:
        ids = by_subset[sub]
        if not ids:
            continue
        lines.append(f"### {sub} ({len(ids)})")
        lines.append("")
        for sid in ids:
            row = row_by_id.get(sid, {})
            tasks = taxonomy_tasks_for_sample(sid, row.get("subset"), row.get("task_type"))
            lines.append(f"- `{sid}` — tasks={tasks}, task_type={row.get('task_type')}")
        lines.append("")

    (out_dir / "selection.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"[done] {len(unique)} unique samples → {out_dir / 'sample_ids.txt'}")
    for task in TASK_KEYS:
        n = len(manifest[task])
        if n < args.per_task:
            print(f"[warn] {task}: only {n}/{args.per_task} available (pool={len(pools.get(task, []))})")


if __name__ == "__main__":
    main()
