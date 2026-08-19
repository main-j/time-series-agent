#!/usr/bin/env python3
"""Run the full MMTS-Bench (2424 samples).

Default universe: data/processed/mmts-bench/index.jsonl (2424)
Default behavior: run all 2424 with the current code and prompts.
Optional legacy reuse: exclude outputs/feasibility_test_19/sample_ids.txt (19),
leaving 2405 samples. This mixes experiment versions and must be explicit.

Merge back to 2424 after the batch:
  python3 scripts/merge_full_benchmark_results.py --batch-dir outputs/full_benchmark_2405

Example:
  python3 scripts/run_full_benchmark_batch.py --exp-name full_benchmark_2405 --resume
"""
from __future__ import annotations

import argparse
import gc
import json
import os
import sys
import time
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

from run_feasibility_batch import run_one  # noqa: E402
from run_checklist_batch import _completed_ids, _write_summary_md  # noqa: E402

DEFAULT_INDEX = ROOT / "data" / "processed" / "mmts-bench" / "index.jsonl"
DEFAULT_EXCLUDE = ROOT / "outputs" / "feasibility_test_19" / "sample_ids.txt"


def _release_cuda_memory() -> None:
    """Best-effort cleanup before retrying OOM / transient GPU failures."""
    gc.collect()
    try:
        import torch

        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            torch.cuda.ipc_collect()
    except Exception:  # noqa: BLE001
        pass


def _is_oom_error(exc: BaseException) -> bool:
    text = str(exc).lower()
    return "out of memory" in text or "cuda out of memory" in text


def _load_ids(path: Path) -> List[str]:
    return [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def _load_all_ids_from_index(index_path: Path) -> List[str]:
    ids: List[str] = []
    for line in index_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        ids.append(str(json.loads(line)["sample_id"]))
    return ids


def _build_target_ids(
    index_file: Path,
    exclude_file: Optional[Path],
    extra_exclude: Sequence[str],
) -> tuple[List[str], List[str], List[str]]:
    all_ids = _load_all_ids_from_index(index_file)
    excluded: Set[str] = set(extra_exclude)
    if exclude_file and exclude_file.exists():
        excluded.update(_load_ids(exclude_file))
    excluded_ordered = [sid for sid in all_ids if sid in excluded]
    target_ids = [sid for sid in all_ids if sid not in excluded]
    return all_ids, excluded_ordered, target_ids


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run full MMTS-Bench batch with progress bar.")
    parser.add_argument(
        "--index-file",
        type=Path,
        default=DEFAULT_INDEX,
        help=f"Processed index.jsonl (default: {DEFAULT_INDEX})",
    )
    parser.add_argument(
        "--exclude-file",
        type=Path,
        default=DEFAULT_EXCLUDE,
        help=f"Sample IDs to exclude (default: {DEFAULT_EXCLUDE})",
    )
    parser.add_argument(
        "--reuse-feasibility",
        action="store_true",
        help=(
            "Exclude and later reuse feasibility_test_19. The existing results "
            "were produced before current tool/prompt fixes, so this is not "
            "enabled by default."
        ),
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
        help="Output experiment name under outputs/ (default: full_benchmark_<timestamp>).",
    )
    parser.add_argument(
        "--resume",
        action="store_true",
        help="Skip samples already present in runs/summary.json.",
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
        "--max-attempts",
        type=int,
        default=3,
        help="Maximum attempts per failed sample (default: 3).",
    )
    parser.add_argument(
        "--retry-delay",
        type=float,
        default=2.0,
        help="Seconds between retry attempts (default: 2).",
    )
    parser.add_argument(
        "--run-baseline",
        action="store_true",
        help="Also run baseline for each sample (default: architecture only).",
    )
    parser.add_argument(
        "--no-run-baseline",
        action="store_true",
        help="Explicitly skip baseline (default behavior).",
    )
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    exclude_file = args.exclude_file if args.reuse_feasibility else None
    all_ids, excluded_ids, target_ids = _build_target_ids(
        args.index_file,
        exclude_file,
        args.extra_exclude,
    )

    exp_name = args.exp_name or f"full_benchmark_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    out_base = ensure_dir(ROOT / "outputs" / exp_name)
    out_root = ensure_dir(out_base / "runs")

    (out_base / "universe_all_ids.txt").write_text("\n".join(all_ids) + "\n", encoding="utf-8")
    (out_base / "excluded_ids.txt").write_text("\n".join(excluded_ids) + "\n", encoding="utf-8")
    (out_base / "sample_ids.txt").write_text("\n".join(target_ids) + "\n", encoding="utf-8")

    pending = list(target_ids)
    existing_summary: List[Dict[str, Any]] = []
    if args.resume:
        if (out_root / "summary.json").is_file():
            previous_summary = json.loads((out_root / "summary.json").read_text(encoding="utf-8"))
            existing_summary = [
                row
                for row in previous_summary
                if not row.get("arch_error") and not row.get("baseline_error")
            ]
        done_ids = {str(r["sample_id"]) for r in existing_summary} | _completed_ids(out_root)
        pending = [sid for sid in target_ids if sid not in done_ids]

    if args.limit is not None:
        pending = pending[: max(0, args.limit)]

    run_baseline = bool(args.run_baseline) and not bool(args.no_run_baseline)
    meta = {
        "exp_name": exp_name,
        "index_file": str(args.index_file),
        "exclude_file": str(exclude_file) if exclude_file else None,
        "reuse_feasibility": args.reuse_feasibility,
        "extra_exclude": list(args.extra_exclude),
        "total_universe": len(all_ids),
        "excluded": len(excluded_ids),
        "target": len(target_ids),
        "pending": len(pending),
        "resume": args.resume,
        "limit": args.limit,
        "max_attempts": args.max_attempts,
        "retry_delay": args.retry_delay,
        "run_baseline": run_baseline,
        "started_at": datetime.now().isoformat(timespec="seconds"),
    }
    (out_base / "run_manifest.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")

    print(
        f"[info] universe={len(all_ids)} excluded={len(excluded_ids)} "
        f"target={len(target_ids)} pending={len(pending)} exp={exp_name} "
        f"run_baseline={run_baseline}",
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
        raise SystemExit(f"samples not found: {missing[:10]}{'...' if len(missing) > 10 else ''} (total {len(missing)})")
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
        desc="full_benchmark",
        unit="sample",
        dynamic_ncols=True,
        mininterval=0.5,
    )
    for sample in pbar:
        sid = sample.sample_id
        pbar.set_postfix(sid=sid[:32], refresh=False)
        row: Dict[str, Any]
        last_error: Optional[Exception] = None
        for attempt in range(1, max(1, args.max_attempts) + 1):
            try:
                row = run_one(pipe, sample, out_root, run_baseline=run_baseline)
                baseline_failed = bool(row.get("baseline_error")) if run_baseline else False
                if not row.get("arch_error") and not baseline_failed:
                    break
                raise RuntimeError(
                    f"pipeline error: architecture={row.get('arch_error')!r}, "
                    f"baseline={row.get('baseline_error')!r}"
                )
            except Exception as exc:
                last_error = exc
                tqdm.write(f"[error] {sid} attempt {attempt}/{max(1, args.max_attempts)}: {exc}")
                if attempt < max(1, args.max_attempts):
                    if _is_oom_error(exc):
                        tqdm.write(f"[info] {sid}: OOM detected, releasing CUDA cache before retry")
                    _release_cuda_memory()
                    time.sleep(max(0.0, args.retry_delay))
        else:
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
                "baseline_skipped": not run_baseline,
                "arch_model_calls": 0,
                "arch_tool_calls": 0,
                "arch_latency_sec": 0.0,
                "arch_error": str(last_error),
                "baseline_error": None,
                "execution_failure": True,
                "attempts": max(1, args.max_attempts),
                "out_dir": "",
            }
            _release_cuda_memory()
        row["attempts"] = attempt
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
        title=f"Full benchmark batch summary ({exp_name})",
    )
    executed = [row for row in summary if not row.get("arch_error") and not row.get("execution_failure")]
    n_exec_ok = sum(1 for row in executed if row.get("arch_ok"))
    meta["finished_at"] = datetime.now().isoformat(timespec="seconds")
    meta["completed"] = len(summary)
    meta["architecture_correct"] = n_arch_ok
    meta["architecture_correct_executed"] = n_exec_ok
    meta["architecture_executed"] = len(executed)
    meta["baseline_correct"] = n_base_ok
    meta["run_baseline"] = run_baseline
    failed_rows = [
        row
        for row in summary
        if row.get("arch_error") or row.get("execution_failure") or (run_baseline and row.get("baseline_error"))
    ]
    meta["failed"] = len(failed_rows)
    meta["failed_sample_ids"] = [str(row["sample_id"]) for row in failed_rows]
    meta["end_to_end_accuracy"] = (n_arch_ok / len(summary)) if summary else 0.0
    meta["executed_accuracy"] = (n_exec_ok / len(executed)) if executed else 0.0
    meta["execution_failure_rate"] = (len(failed_rows) / len(summary)) if summary else 0.0
    (out_base / "run_manifest.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"[done] summary → {out_root / 'summary.json'}", flush=True)
    print(
        f"[done] architecture end-to-end {n_arch_ok}/{len(summary)} "
        f"({meta['end_to_end_accuracy']:.3f})",
        flush=True,
    )
    print(
        f"[done] architecture executed-only {n_exec_ok}/{len(executed)} "
        f"({meta['executed_accuracy']:.3f})",
        flush=True,
    )
    print(
        f"[done] execution failures {len(failed_rows)}/{len(summary)} "
        f"({meta['execution_failure_rate']:.3f})",
        flush=True,
    )
    if run_baseline:
        print(f"[done] baseline correct {n_base_ok}/{len(summary)}", flush=True)
    else:
        print("[done] baseline skipped; merge historical per-sample baseline later", flush=True)
    if failed_rows:
        print(
            f"[error] {len(failed_rows)} samples still failed after retries; "
            "rerun with --resume to retry them.",
            flush=True,
        )
        raise SystemExit(2)
    print(
        f"[done] merge to 2424: python3 scripts/merge_full_benchmark_results.py "
        f"--batch-dir outputs/{exp_name}",
        flush=True,
    )


if __name__ == "__main__":
    main()
