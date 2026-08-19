#!/usr/bin/env python3
"""Shared merge + taxonomy statistics for benchmark result aggregation."""
from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

SCRIPTS = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS))

from mmts_taxonomy import compute_evaluation_stats, write_stats_markdown  # noqa: E402


def load_summary(path: Path) -> List[Dict[str, Any]]:
    return json.loads(path.read_text(encoding="utf-8"))


def merge_rows(
    universe: List[str],
    feasibility_rows: List[Dict[str, Any]],
    batch_rows: List[Dict[str, Any]],
) -> tuple[List[Dict[str, Any]], List[str]]:
    by_id: Dict[str, Dict[str, Any]] = {}
    for row in feasibility_rows:
        tagged = dict(row)
        tagged["source"] = "feasibility"
        by_id[str(row["sample_id"])] = tagged
    for row in batch_rows:
        tagged = dict(row)
        tagged["source"] = "batch"
        by_id[str(row["sample_id"])] = tagged

    merged: List[Dict[str, Any]] = []
    missing: List[str] = []
    for sid in universe:
        if sid in by_id:
            merged.append(by_id[sid])
        else:
            missing.append(sid)
            merged.append(
                {
                    "sample_id": sid,
                    "source": "missing",
                    "subset": None,
                    "task_type": None,
                    "gold": None,
                    "arch_pred": None,
                    "baseline_pred": None,
                    "arch_ok": False,
                    "baseline_ok": False,
                }
            )
    return merged, missing


def finalize_merge_output(
    *,
    dest: Path,
    universe: List[str],
    merged: List[Dict[str, Any]],
    missing: List[str],
    meta: Dict[str, Any],
    title: str,
) -> Dict[str, Any]:
    eval_stats = compute_evaluation_stats(merged)
    enriched = eval_stats.pop("enriched_rows")

    stats = {
        **meta,
        "total": len(universe),
        "present": len(universe) - len(missing),
        "missing": len(missing),
        "missing_ids": missing,
        "from_feasibility": sum(1 for r in merged if r.get("source") == "feasibility"),
        "from_batch": sum(1 for r in merged if r.get("source") == "batch"),
        "architecture_correct": eval_stats["architecture_correct"],
        "baseline_correct": eval_stats["baseline_correct"],
        "architecture_accuracy": eval_stats["architecture_accuracy"],
        "baseline_accuracy": eval_stats["baseline_accuracy"],
        "by_subset": eval_stats["by_subset"],
        "by_task": eval_stats["by_task"],
        "by_dimension": eval_stats["by_dimension"],
        "task_rows": eval_stats["task_rows"],
        "merged_at": datetime.now().isoformat(timespec="seconds"),
    }

    dest.mkdir(parents=True, exist_ok=True)
    (dest / "sample_ids.txt").write_text("\n".join(universe) + "\n", encoding="utf-8")
    (dest / "summary.json").write_text(json.dumps(enriched, ensure_ascii=False, indent=2), encoding="utf-8")
    (dest / "stats.json").write_text(json.dumps(stats, ensure_ascii=False, indent=2), encoding="utf-8")
    (dest / "stats_by_task.json").write_text(
        json.dumps(eval_stats["task_rows"], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    extra = [
        f"- From feasibility: {stats['from_feasibility']}",
        f"- From batch: {stats['from_batch']}",
        f"- Missing: {stats['missing']}",
    ]
    write_stats_markdown(dest / "summary.md", stats, title=title, extra_lines=extra)
    write_stats_markdown(dest / "stats_by_task.md", stats, title=f"{title} — task breakdown")

    return stats
