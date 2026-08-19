#!/usr/bin/env python3
"""Build a unified 2424-sample summary from a full benchmark run.

Statistics follow the official MMTS taxonomy: by subset (Base/InWild/Match/Align)
and by task (19 tasks across 5 dimensions).

If the batch contains all 2424 current-version results, they take precedence
over the optional feasibility summary. A 2405-sample legacy-reuse batch can
still be merged with the 19 feasibility rows for diagnostic use.

Example:
  python3 scripts/merge_full_benchmark_results.py --batch-dir outputs/full_benchmark_2424
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS))

from merge_stats_common import finalize_merge_output, load_summary, merge_rows  # noqa: E402

DEFAULT_INDEX = ROOT / "data" / "processed" / "mmts-bench" / "index.jsonl"
DEFAULT_FEASIBILITY = ROOT / "outputs" / "feasibility_test_19" / "runs" / "summary.json"


def _load_universe(index_file: Path) -> List[str]:
    ids: List[str] = []
    for line in index_file.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        ids.append(str(json.loads(line)["sample_id"]))
    return ids


def merge(
    batch_dir: Path,
    index_file: Path = DEFAULT_INDEX,
    feasibility_summary: Path = DEFAULT_FEASIBILITY,
    out_dir: Optional[Path] = None,
) -> Dict[str, Any]:
    universe = _load_universe(index_file)
    batch_summary_path = batch_dir / "runs" / "summary.json"
    if not batch_summary_path.is_file():
        raise SystemExit(f"batch summary not found: {batch_summary_path}")

    feasibility_rows = load_summary(feasibility_summary) if feasibility_summary.is_file() else []
    batch_rows = load_summary(batch_summary_path)
    merged, missing = merge_rows(universe, feasibility_rows, batch_rows)

    meta = {
        "index_file": str(index_file),
        "feasibility_summary": str(feasibility_summary),
        "batch_summary": str(batch_summary_path),
    }
    dest = out_dir or (batch_dir / "merged_2424")
    stats = finalize_merge_output(
        dest=dest,
        universe=universe,
        merged=merged,
        missing=missing,
        meta=meta,
        title="Unified full benchmark summary (2424 samples)",
    )
    return {"dest": dest, "stats": stats}


def main() -> None:
    parser = argparse.ArgumentParser(description="Merge feasibility + batch into 2424-sample summary.")
    parser.add_argument(
        "--batch-dir",
        type=Path,
        required=True,
        help="Batch experiment directory, e.g. outputs/full_benchmark_2424",
    )
    parser.add_argument(
        "--index-file",
        type=Path,
        default=DEFAULT_INDEX,
        help=f"Full universe index.jsonl (default: {DEFAULT_INDEX})",
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
        help="Output directory (default: <batch-dir>/merged_2424)",
    )
    args = parser.parse_args()

    batch_dir = args.batch_dir if args.batch_dir.is_absolute() else ROOT / args.batch_dir
    result = merge(
        batch_dir=batch_dir,
        index_file=args.index_file,
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
    print("[done] by subset:", ", ".join(
        f"{k}={v['arch_acc']:.1%}" for k, v in stats["by_subset"].items() if v["n"]
    ))
    if stats["missing"]:
        print(f"[warn] missing sample IDs ({len(stats['missing_ids'])}): {stats['missing_ids'][:5]}...")


if __name__ == "__main__":
    main()
