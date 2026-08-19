#!/usr/bin/env python3
"""Merge feasibility (19) + batch (181) into a unified 200-sample checklist summary.

Statistics follow the official MMTS taxonomy: by subset and by task.

Example:
  python3 scripts/merge_checklist_results.py --batch-dir outputs/checklist_full_181
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS))

from merge_stats_common import finalize_merge_output, load_summary, merge_rows  # noqa: E402

DEFAULT_CHECKLIST = ROOT / "outputs" / "weighted_mmts_selection_200" / "sample_ids.txt"
DEFAULT_FEASIBILITY = ROOT / "outputs" / "feasibility_test_19" / "runs" / "summary.json"


def _load_ids(path: Path) -> List[str]:
    return [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def merge(
    batch_dir: Path,
    checklist_file: Path = DEFAULT_CHECKLIST,
    feasibility_summary: Path = DEFAULT_FEASIBILITY,
    out_dir: Optional[Path] = None,
) -> Dict[str, Any]:
    checklist = _load_ids(checklist_file)
    batch_summary_path = batch_dir / "runs" / "summary.json"
    if not batch_summary_path.is_file():
        raise SystemExit(f"batch summary not found: {batch_summary_path}")

    feasibility_rows = load_summary(feasibility_summary) if feasibility_summary.is_file() else []
    batch_rows = load_summary(batch_summary_path)
    merged, missing = merge_rows(checklist, feasibility_rows, batch_rows)

    meta = {
        "checklist_file": str(checklist_file),
        "feasibility_summary": str(feasibility_summary),
        "batch_summary": str(batch_summary_path),
    }
    dest = out_dir or (batch_dir / "merged_200")
    stats = finalize_merge_output(
        dest=dest,
        universe=checklist,
        merged=merged,
        missing=missing,
        meta=meta,
        title="Unified checklist summary (200 samples)",
    )
    return {"dest": dest, "stats": stats}


def main() -> None:
    parser = argparse.ArgumentParser(description="Merge feasibility + batch into 200-sample summary.")
    parser.add_argument(
        "--batch-dir",
        type=Path,
        required=True,
        help="Batch experiment directory, e.g. outputs/checklist_full_181",
    )
    parser.add_argument(
        "--checklist-file",
        type=Path,
        default=DEFAULT_CHECKLIST,
        help=f"200-sample checklist (default: {DEFAULT_CHECKLIST})",
    )
    parser.add_argument(
        "--feasibility-summary",
        type=Path,
        default=DEFAULT_FEASIBILITY,
        help=f"Feasibility summary.json (default: {DEFAULT_FEASIBILITY})",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=None,
        help="Output directory (default: <batch-dir>/merged_200)",
    )
    args = parser.parse_args()

    batch_dir = args.batch_dir if args.batch_dir.is_absolute() else ROOT / args.batch_dir
    result = merge(
        batch_dir=batch_dir,
        checklist_file=args.checklist_file,
        feasibility_summary=args.feasibility_summary,
        out_dir=args.out_dir,
    )
    stats = result["stats"]
    dest = result["dest"]
    print(f"[done] merged summary → {dest / 'summary.json'}")
    print(f"[done] stats → {dest / 'stats.json'}")
    print(f"[done] task stats → {dest / 'stats_by_task.json'}")
    print(
        f"[done] architecture {stats['architecture_correct']}/{stats['present']} "
        f"({stats['architecture_accuracy']:.1%})"
    )
    print(
        f"[done] baseline {stats['baseline_correct']}/{stats['present']} "
        f"({stats['baseline_accuracy']:.1%})"
    )
    print(
        f"[done] sources: feasibility={stats['from_feasibility']} "
        f"batch={stats['from_batch']} missing={stats['missing']}"
    )
    if stats["missing"]:
        print(f"[warn] missing sample IDs: {stats['missing_ids']}")


if __name__ == "__main__":
    main()
