#!/usr/bin/env python3
"""Build metadata-only generalization splits without historical correctness leakage.

Creates:
  outputs/splits/generalization_v1/
    manifest.json
    smoke_76/sample_ids.txt
    dev_190/sample_ids.txt
    heldout_190/sample_ids.txt
    reserve_*/sample_ids.txt

Contamination IDs (weighted 200 / feasibility 19 / diagnostic 5 / known ad-hoc
debug samples) are excluded from all generalization splits.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import random
import sys
from collections import defaultdict
from pathlib import Path
from typing import Dict, Iterable, List, Set

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from mmts_taxonomy import TASK_KEYS, taxonomy_tasks_for_sample  # noqa: E402

INDEX = ROOT / "data" / "processed" / "mmts-bench" / "index.jsonl"
OUT_ROOT = ROOT / "outputs" / "splits" / "generalization_v1"
SEED = 20260803

CONTAMINATION_FILES = [
    ROOT / "outputs" / "weighted_mmts_selection_200" / "sample_ids.txt",
    ROOT / "outputs" / "feasibility_test_19" / "sample_ids.txt",
    ROOT / "outputs" / "diagnostic_fix_validation" / "sample_ids.txt",
]
EXTRA_CONTAMINATION = [
    "InWild:tsqa_1084:64",
    "InWild:tsqa_1084:1080",
    "Match:qats_400:380",
]

# Per-task quotas for smoke / dev / heldout (metadata-only).
SMOKE_PER_TASK = 4
DEV_PER_TASK = 10
HELDOUT_PER_TASK = 10


def _load_ids(path: Path) -> List[str]:
    if not path.is_file():
        return []
    return [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def _stable_seed(seed: int, task: str) -> int:
    digest = hashlib.sha256(f"{seed}:{task}".encode()).hexdigest()
    return int(digest[:16], 16)


def _contamination() -> Set[str]:
    ids: Set[str] = set(EXTRA_CONTAMINATION)
    for path in CONTAMINATION_FILES:
        ids.update(_load_ids(path))
    return ids


def _load_index() -> List[dict]:
    rows = []
    for line in INDEX.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        rows.append(json.loads(line))
    return rows


def _build_task_pools(rows: List[dict], banned: Set[str]) -> Dict[str, List[str]]:
    pools: Dict[str, List[str]] = defaultdict(list)
    for row in rows:
        sid = str(row["sample_id"])
        if sid in banned:
            continue
        tasks = taxonomy_tasks_for_sample(sid, row.get("subset"), row.get("task_type"))
        for task in tasks:
            pools[task].append(sid)
    # Stable order then seeded shuffle later.
    for task, ids in pools.items():
        pools[task] = sorted(set(ids))
    return pools


def _pick(ids: List[str], k: int, seed: int, task: str) -> List[str]:
    if k <= 0 or not ids:
        return []
    rng = random.Random(_stable_seed(seed, task))
    pool = ids[:]
    rng.shuffle(pool)
    return pool[: min(k, len(pool))]


def _write_split(path: Path, ids: Iterable[str]) -> None:
    path.mkdir(parents=True, exist_ok=True)
    unique = list(dict.fromkeys(ids))
    (path / "sample_ids.txt").write_text("\n".join(unique) + ("\n" if unique else ""), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", type=int, default=SEED)
    parser.add_argument("--out-root", type=Path, default=OUT_ROOT)
    args = parser.parse_args()

    banned = _contamination()
    rows = _load_index()
    pools = _build_task_pools(rows, banned)

    smoke: List[str] = []
    dev: List[str] = []
    heldout: List[str] = []
    used: Set[str] = set()
    task_stats = {}

    for task in TASK_KEYS:
        pool = [sid for sid in pools.get(task, []) if sid not in used]
        # Draw heldout first so the gate set is fixed before tuning draws.
        h = _pick(pool, HELDOUT_PER_TASK, args.seed + 1, task)
        used.update(h)
        pool = [sid for sid in pool if sid not in used]
        d = _pick(pool, DEV_PER_TASK, args.seed + 2, task)
        used.update(d)
        pool = [sid for sid in pool if sid not in used]
        s = _pick(pool, SMOKE_PER_TASK, args.seed + 3, task)
        used.update(s)
        smoke.extend(s)
        dev.extend(d)
        heldout.extend(h)
        task_stats[task] = {"smoke": len(s), "dev": len(d), "heldout": len(h), "pool": len(pools.get(task, []))}

    all_ids = [str(r["sample_id"]) for r in rows]
    reserve = [sid for sid in all_ids if sid not in banned and sid not in used]

    out = args.out_root
    _write_split(out / "smoke_76", smoke)
    _write_split(out / "dev_190", dev)
    _write_split(out / "heldout_190", heldout)
    _write_split(out / f"reserve_{len(reserve)}", reserve)

    manifest = {
        "seed": args.seed,
        "policy": "metadata_only_no_historical_correctness",
        "contamination_excluded": sorted(banned),
        "n_contamination": len(banned),
        "counts": {
            "smoke": len(list(dict.fromkeys(smoke))),
            "dev": len(list(dict.fromkeys(dev))),
            "heldout": len(list(dict.fromkeys(heldout))),
            "reserve": len(reserve),
            "universe": len(all_ids),
        },
        "per_task": task_stats,
        "notes": [
            "Do not tune prompts/code against heldout_190.",
            "Diagnostic/weighted/feasibility IDs are regression-only, not generalization gate.",
        ],
    }
    out.mkdir(parents=True, exist_ok=True)
    (out / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(manifest["counts"], indent=2))
    print(f"[done] wrote splits → {out}")


if __name__ == "__main__":
    main()
