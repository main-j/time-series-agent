#!/usr/bin/env python3
"""Run the weighted MMTS checklist, excluding feasibility-tested samples.

Default checklist: outputs/weighted_mmts_selection_200/sample_ids.txt (200)
Default exclusion: outputs/feasibility_test_19/sample_ids.txt (19)
Remaining: 181 samples.

Example:
  cd /root/autodl-tmp/time-series-agent
  python3 scripts/run_checklist_batch.py
  python3 scripts/run_checklist_batch.py --exp-name tool_fix_batch_v1
  python3 scripts/run_checklist_batch.py --resume --limit 5
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Set

from tqdm import tqdm

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(SCRIPTS))
os.environ.setdefault("HF_HUB_OFFLINE", "1")
os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")
os.environ.setdefault("PYTHONUNBUFFERED", "1")

from ts_agent.core.llm import build_provider
from ts_agent.core.utils import ensure_dir, load_yaml
from ts_agent.data.mmts import MMTSBenchDataset
from ts_agent.pipelines.experiment import ExperimentPipeline

# Reuse IO dump + scoring from feasibility runner.
from run_feasibility_batch import run_one  # noqa: E402

DEFAULT_CHECKLIST = ROOT / "outputs" / "weighted_mmts_selection_200" / "sample_ids.txt"
DEFAULT_EXCLUDE = ROOT / "outputs" / "feasibility_test_19" / "sample_ids.txt"


def _load_ids(path: Path) -> List[str]:
    return [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def _build_checklist(
    checklist_file: Path,
    exclude_file: Optional[Path],
    extra_exclude: Sequence[str],
) -> tuple[List[str], List[str], List[str]]:
    all_ids = _load_ids(checklist_file)
    excluded: Set[str] = set(extra_exclude)
    if exclude_file and exclude_file.exists():
        excluded.update(_load_ids(exclude_file))
    remaining = [sid for sid in all_ids if sid not in excluded]
    excluded_ordered = [sid for sid in all_ids if sid in excluded]
    return all_ids, excluded_ordered, remaining


def _completed_ids(out_root: Path) -> Set[str]:
    done: Set[str] = set()
    summary_path = out_root / "summary.json"
    if summary_path.is_file():
        try:
            for row in json.loads(summary_path.read_text(encoding="utf-8")):
                if not row.get("arch_error") and not row.get("baseline_error"):
                    done.add(str(row["sample_id"]))
        except (json.JSONDecodeError, KeyError, TypeError):
            pass
    return done


def _write_summary_md(summary: List[Dict[str, Any]], path: Path, title: str) -> None:
    lines = [f"# {title}", ""]
    lines.append(
        "| sample | subset | n_series | task | gold | arch | base | arch_ok | base_ok | tools | latency_s |"
    )
    lines.append("|---|---|---:|---|---|---|---|---|---|---:|---:|")
    for r in summary:
        lines.append(
            f"| `{r['sample_id']}` | {r['subset']} | {r['n_series']} | {r['task_type']} | {r['gold']} | "
            f"{r['arch_pred']} | {r['baseline_pred']} | {r['arch_ok']} | {r['baseline_ok']} | "
            f"{r['arch_tool_calls']} | {r['arch_latency_sec']:.1f} |"
        )
    lines.append("")
    n_ok = sum(1 for r in summary if r["arch_ok"])
    n_base = sum(1 for r in summary if r["baseline_ok"])
    lines.append(f"Architecture correct: **{n_ok}/{len(summary)}**")
    lines.append(f"Baseline correct: **{n_base}/{len(summary)}**")
    path.write_text("\n".join(lines), encoding="utf-8")


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run weighted MMTS checklist batch with progress bar.")
    parser.add_argument(
        "--checklist-file",
        type=Path,
        default=DEFAULT_CHECKLIST,
        help=f"Full test checklist (default: {DEFAULT_CHECKLIST})",
    )
    parser.add_argument(
        "--exclude-file",
        type=Path,
        default=DEFAULT_EXCLUDE,
        help=f"Sample IDs to exclude (default: {DEFAULT_EXCLUDE})",
    )
    parser.add_argument(
        "--no-exclude-feasibility",
        action="store_true",
        help="Do not exclude feasibility_test_19 samples.",
    )
    parser.add_argument(
        "--extra-exclude",
        nargs="*",
        default=[],
        help="Additional sample IDs to exclude.",
    )
    parser.add_argument(
        "--exp-name",
        default=None,
        help="Output experiment name under outputs/ (default: checklist_batch_<timestamp>).",
    )
    parser.add_argument(
        "--resume",
        action="store_true",
        help="Skip samples that already have full_io.json in the run directory.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Run at most N pending samples (after exclusion/resume).",
    )
    parser.add_argument(
        "--device",
        default="cuda:0",
        help="Torch device map for local Qwen (default: cuda:0).",
    )
    parser.add_argument(
        "--run-baseline",
        action="store_true",
        help="Also run baseline (default: architecture only).",
    )
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    exclude_file = None if args.no_exclude_feasibility else args.exclude_file
    all_ids, excluded_ids, target_ids = _build_checklist(
        args.checklist_file,
        exclude_file,
        args.extra_exclude,
    )

    exp_name = args.exp_name or f"checklist_batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    out_base = ensure_dir(ROOT / "outputs" / exp_name)
    out_root = ensure_dir(out_base / "runs")

    (out_base / "checklist_all_ids.txt").write_text("\n".join(all_ids) + "\n", encoding="utf-8")
    (out_base / "excluded_ids.txt").write_text("\n".join(excluded_ids) + "\n", encoding="utf-8")
    (out_base / "sample_ids.txt").write_text("\n".join(target_ids) + "\n", encoding="utf-8")

    pending = list(target_ids)
    existing_summary: List[Dict[str, Any]] = []
    if args.resume:
        if (out_root / "summary.json").is_file():
            existing_summary = json.loads((out_root / "summary.json").read_text(encoding="utf-8"))
        done_ids = {str(r["sample_id"]) for r in existing_summary} | _completed_ids(out_root)
        pending = [sid for sid in target_ids if sid not in done_ids]

    if args.limit is not None:
        pending = pending[: max(0, args.limit)]

    meta = {
        "exp_name": exp_name,
        "checklist_file": str(args.checklist_file),
        "exclude_file": str(exclude_file) if exclude_file else None,
        "extra_exclude": list(args.extra_exclude),
        "total_checklist": len(all_ids),
        "excluded": len(excluded_ids),
        "target": len(target_ids),
        "pending": len(pending),
        "resume": args.resume,
        "limit": args.limit,
        "started_at": datetime.now().isoformat(timespec="seconds"),
    }
    (out_base / "run_manifest.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")

    print(
        f"[info] checklist={len(all_ids)} excluded={len(excluded_ids)} "
        f"target={len(target_ids)} pending={len(pending)} exp={exp_name}",
        flush=True,
    )
    if not pending:
        print("[done] nothing to run.", flush=True)
        return

    cfg = load_yaml(ROOT / "configs" / "experiment.yaml")
    cfg["experiment"]["use_mock_llm"] = False
    cfg["experiment"]["max_series_text_chars"] = None
    cfg["experiment"]["cache_dir"] = str(out_base / "llm_cache")
    cfg["model"]["device_map"] = args.device

    ds = MMTSBenchDataset(
        cfg["data"]["processed_dir"],
        raw_dir=cfg["data"]["raw_dir"],
        max_series_text_chars=None,
    )
    samples = ds.filter(sample_ids=pending)
    found = {s.sample_id for s in samples}
    missing = [x for x in pending if x not in found]
    if missing:
        raise SystemExit(f"samples not found: {missing}")
    by_id = {s.sample_id: s for s in samples}
    ordered = [by_id[i] for i in pending]

    print("[info] building LLM provider (Qwen2.5-14B)...", flush=True)
    llm = build_provider(cfg)
    llm.record_io = True
    pipe = ExperimentPipeline(
        llm,
        cfg["experiment"]["prompt_dir"],
        max_tool_rounds=int(cfg["experiment"].get("max_tool_rounds", 3)),
    )

    summary: List[Dict[str, Any]] = list(existing_summary)
    n_arch_ok = sum(1 for r in summary if r.get("arch_ok"))
    n_base_ok = sum(1 for r in summary if r.get("baseline_ok"))

    pbar = tqdm(
        ordered,
        total=len(ordered),
        desc="checklist",
        unit="sample",
        dynamic_ncols=True,
        mininterval=0.5,
    )
    for sample in pbar:
        sid = sample.sample_id
        pbar.set_postfix(sid=sid[:32], refresh=False)
        try:
            row = run_one(pipe, sample, out_root, run_baseline=bool(args.run_baseline))
        except Exception as exc:
            tqdm.write(f"[error] {sid}: {exc}")
            row = {
                "sample_id": sid,
                "subset": str(sample.subset),
                "n_series": len(sample.series),
                "series_lengths": [len(x) for x in sample.series],
                "task_type": sample.task_type,
                "gold": sample.answer,
                "arch_pred": None,
                "arch_ok": False,
                "baseline_pred": None,
                "baseline_ok": False,
                "arch_model_calls": 0,
                "arch_tool_calls": 0,
                "arch_latency_sec": 0.0,
                "arch_error": str(exc),
                "out_dir": "",
            }
        summary.append(row)
        if row.get("arch_ok"):
            n_arch_ok += 1
        if row.get("baseline_ok"):
            n_base_ok += 1
        done = len(summary)
        pbar.set_postfix(
            sid=sid[:28],
            arch_ok=f"{n_arch_ok}/{done}",
            base_ok=f"{n_base_ok}/{done}",
            refresh=False,
        )
        (out_root / "summary.json").write_text(
            json.dumps(summary, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
    pbar.close()

    _write_summary_md(
        summary,
        out_root / "summary.md",
        title=f"Checklist batch summary ({exp_name})",
    )
    meta["finished_at"] = datetime.now().isoformat(timespec="seconds")
    meta["completed"] = len(summary)
    meta["architecture_correct"] = n_arch_ok
    meta["baseline_correct"] = n_base_ok
    (out_base / "run_manifest.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"[done] summary → {out_root / 'summary.json'}", flush=True)
    print(f"[done] architecture correct {n_arch_ok}/{len(summary)}", flush=True)
    print(f"[done] baseline correct {n_base_ok}/{len(summary)}", flush=True)


if __name__ == "__main__":
    main()
