#!/usr/bin/env python3
"""Architecture evaluation batch with tool-issue skip.

Runs architecture-only on a checklist (default: per_task_2x_v1, 38 samples).
If a sample hits tool/$ref/call binding failures (or OOM/crash), record the
issue and skip scoring that sample — do not abort the whole batch.

Example:
  python3 scripts/run_arch_eval_batch.py
  python3 scripts/run_arch_eval_batch.py --exp-name arch_eval_v1 --resume
  python3 scripts/run_arch_eval_batch.py --limit 3
"""
from __future__ import annotations

import argparse
import gc
import json
import os
import re
import sys
import traceback
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

from tqdm import tqdm

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(SCRIPTS))
os.environ.setdefault("HF_HUB_OFFLINE", "1")
os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")
os.environ.setdefault("PYTHONUNBUFFERED", "1")

from run_feasibility_batch import _answer_correct, run_one  # noqa: E402
from ts_agent.core.llm import build_provider
from ts_agent.core.utils import ensure_dir, load_yaml
from ts_agent.data.mmts import MMTSBenchDataset
from ts_agent.pipelines.experiment import ExperimentPipeline

DEFAULT_CHECKLIST = ROOT / "outputs" / "per_task_2x_v1" / "sample_ids.txt"

# Tool / call binding problems that should exclude a sample from accuracy.
TOOL_ISSUE_RE = re.compile(
    r"path '.*' not found"
    r"|unresolved reference"
    r"|invalid reference"
    r"|Unrecognized series selector:\s*'\$"
    r"|tool tool not in prior"
    r"|\$tool\.series"
    r"|WorkflowExecutor"
    r"|KeyError",
    re.I,
)


def _load_ids(path: Path) -> List[str]:
    return [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def scan_tool_issues(arch: Dict[str, Any]) -> Dict[str, Any]:
    details = arch.get("details") or {}
    attempted = 0
    successes = 0
    failed = 0
    issue_hits = 0
    examples: List[Dict[str, Any]] = []

    def consider(step: Dict[str, Any], where: str) -> None:
        nonlocal attempted, successes, failed, issue_hits
        attempted += 1
        err = str(step.get("error") or "")
        args_txt = json.dumps(step.get("arguments") or {}, ensure_ascii=False)
        if step.get("success"):
            successes += 1
            return
        failed += 1
        if TOOL_ISSUE_RE.search(err) or TOOL_ISSUE_RE.search(args_txt):
            issue_hits += 1
            if len(examples) < 12:
                examples.append(
                    {
                        "where": where,
                        "call_id": step.get("call_id"),
                        "tool": step.get("tool_name"),
                        "arguments": step.get("arguments"),
                        "error": err[:400],
                    }
                )

    for scale, st in (details.get("homo_stages") or {}).items():
        for mac in st.get("macros") or []:
            for step in mac.get("executed_steps") or []:
                consider(step, f"homo:{scale}:m{mac.get('macro')}")
    for role, st in (details.get("hetero_stages") or {}).items():
        for mac in st.get("macros") or []:
            for step in mac.get("executed_steps") or []:
                consider(step, f"hetero:{role}:m{mac.get('macro')}")

    arch_err = str(arch.get("error") or "")
    arch_err_issue = bool(arch_err and TOOL_ISSUE_RE.search(arch_err))

    has_issue = issue_hits > 0 or arch_err_issue
    reason = None
    if issue_hits > 0:
        reason = f"{issue_hits} tool-step binding/path failures out of {attempted}"
    elif arch_err_issue:
        reason = f"architecture error looks tool-related: {arch_err[:200]}"

    return {
        "has_issue": has_issue,
        "reason": reason,
        "attempted": attempted,
        "successes": successes,
        "failed": failed,
        "issue_hits": issue_hits,
        "examples": examples,
        "arch_error": arch_err or None,
    }


def _completed_ids(summary: List[Dict[str, Any]]) -> Set[str]:
    """Resume: skip samples already finished (scored or tool-skipped)."""
    done: Set[str] = set()
    for row in summary:
        sid = str(row.get("sample_id") or "")
        if not sid:
            continue
        if row.get("skipped_tool_issue") or row.get("skipped_exception"):
            done.add(sid)
        elif row.get("arch_error"):
            continue  # allow retry of hard arch errors that weren't classified
        else:
            done.add(sid)
    return done


def _write_reports(out_base: Path, summary: List[Dict[str, Any]], meta: Dict[str, Any]) -> None:
    scored = [r for r in summary if not r.get("skipped_tool_issue") and not r.get("skipped_exception")]
    skipped = [r for r in summary if r.get("skipped_tool_issue") or r.get("skipped_exception")]
    n_ok = sum(1 for r in scored if r.get("arch_ok"))

    lines = [
        "# Architecture evaluation",
        "",
        f"- Total finished rows: {len(summary)}",
        f"- Scored (no tool skip): **{len(scored)}**",
        f"- Skipped (tool/exception): **{len(skipped)}**",
        f"- Architecture correct (among scored): **{n_ok}/{len(scored)}**"
        + (f" ({100.0 * n_ok / len(scored):.1f}%)" if scored else ""),
        "",
        "## Scored samples",
        "",
        "| sample | gold | pred | ok | tools | tool_ok | latency_s |",
        "|---|---|---|---|---:|---|---:|",
    ]
    for r in scored:
        tr = r.get("tool_scan") or {}
        lines.append(
            f"| `{r['sample_id']}` | {r.get('gold')} | {r.get('arch_pred')} | {r.get('arch_ok')} | "
            f"{r.get('arch_tool_calls')} | {tr.get('successes')}/{tr.get('attempted')} | "
            f"{float(r.get('arch_latency_sec') or 0):.1f} |"
        )
    lines.extend(["", "## Skipped (tool / exception)", ""])
    if not skipped:
        lines.append("(none)")
    else:
        lines.append("| sample | reason | examples |")
        lines.append("|---|---|---|")
        for r in skipped:
            reason = r.get("skip_reason") or (r.get("tool_scan") or {}).get("reason") or r.get("error") or ""
            ex = (r.get("tool_scan") or {}).get("examples") or []
            ex_s = "; ".join(
                f"{e.get('tool')}:{str(e.get('error') or '')[:80]}" for e in ex[:3]
            )
            lines.append(f"| `{r['sample_id']}` | {reason} | {ex_s} |")

    (out_base / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    (out_base / "run_manifest.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--exp-name", default="arch_eval_per_task_2x_v1")
    p.add_argument("--checklist-file", type=Path, default=DEFAULT_CHECKLIST)
    p.add_argument("--resume", action="store_true")
    p.add_argument("--limit", type=int, default=None)
    p.add_argument("--device", default="cuda:0")
    return p.parse_args()


def main() -> None:
    args = _parse_args()
    out_base = ensure_dir(ROOT / "outputs" / args.exp_name)
    runs = ensure_dir(out_base / "runs")
    issues_path = out_base / "tool_issues.jsonl"

    ids = _load_ids(args.checklist_file)
    summary_path = out_base / "summary.json"
    summary: List[Dict[str, Any]] = []
    if args.resume and summary_path.is_file():
        try:
            summary = json.loads(summary_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            summary = []

    done = _completed_ids(summary) if args.resume else set()
    pending = [sid for sid in ids if sid not in done]
    if args.limit is not None:
        pending = pending[: args.limit]

    meta = {
        "exp_name": args.exp_name,
        "checklist_file": str(args.checklist_file),
        "total_checklist": len(ids),
        "already_done": len(done),
        "pending": len(pending),
        "resume": bool(args.resume),
        "limit": args.limit,
        "started_at": datetime.now().isoformat(timespec="seconds"),
        "policy": "skip_sample_on_tool_issue",
    }
    (out_base / "sample_ids.txt").write_text("\n".join(ids) + "\n", encoding="utf-8")
    (out_base / "run_manifest.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"[info] checklist={len(ids)} pending={len(pending)} exp={args.exp_name}", flush=True)
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
    by_id = {s.sample_id: s for s in samples}
    missing = [x for x in pending if x not in by_id]
    if missing:
        raise SystemExit(f"samples not found: {missing}")

    print("[info] building LLM...", flush=True)
    llm = build_provider(cfg)
    llm.record_io = True
    pipe = ExperimentPipeline(
        llm,
        cfg["experiment"]["prompt_dir"],
        max_tool_rounds=int(cfg["experiment"].get("max_tool_rounds", 3)),
    )

    n_ok = sum(1 for r in summary if r.get("arch_ok") and not r.get("skipped_tool_issue"))
    n_skip = sum(1 for r in summary if r.get("skipped_tool_issue") or r.get("skipped_exception"))
    bar = tqdm(pending, desc="arch-eval", unit="sample")
    for sid in bar:
        sample = by_id[sid]
        try:
            try:
                import torch

                if torch.cuda.is_available():
                    torch.cuda.empty_cache()
                    gc.collect()
            except Exception:
                pass

            row = run_one(pipe, sample, runs, run_baseline=False)
            full = json.loads(Path(row["out_dir"], "full_io.json").read_text(encoding="utf-8"))
            arch = full["architecture"]
            scan = scan_tool_issues(arch)
            row["tool_scan"] = scan
            row["arch_ok"] = _answer_correct(
                sample.question_type, arch.get("predicted_answer"), sample.answer
            )

            if scan["has_issue"]:
                row["skipped_tool_issue"] = True
                row["skip_reason"] = scan["reason"]
                row["arch_ok"] = False  # not counted in scored accuracy
                n_skip += 1
                with issues_path.open("a", encoding="utf-8") as f:
                    f.write(
                        json.dumps(
                            {
                                "sample_id": sid,
                                "reason": scan["reason"],
                                "examples": scan["examples"],
                                "arch_error": scan.get("arch_error"),
                                "out_dir": row.get("out_dir"),
                            },
                            ensure_ascii=False,
                        )
                        + "\n"
                    )
                print(f"[skip-tool] {sid}: {scan['reason']}", flush=True)
            else:
                if row["arch_ok"]:
                    n_ok += 1

            summary.append(row)
        except Exception as exc:
            tb = traceback.format_exc()
            err = str(exc)
            low = err.lower()
            is_oom = ("out of memory" in low) or ("cuda" in low and "memory" in low)
            row = {
                "sample_id": sid,
                "gold": sample.answer,
                "arch_pred": None,
                "arch_ok": False,
                "skipped_exception": True,
                "skipped_tool_issue": bool(TOOL_ISSUE_RE.search(err)) or is_oom,
                "skip_reason": "oom" if is_oom else f"exception: {err[:200]}",
                "error": err,
                "traceback": tb,
                "oom": is_oom,
            }
            n_skip += 1
            summary.append(row)
            with issues_path.open("a", encoding="utf-8") as f:
                f.write(json.dumps({"sample_id": sid, "reason": row["skip_reason"], "error": err}, ensure_ascii=False) + "\n")
            (out_base / "last_exception.txt").write_text(tb, encoding="utf-8")
            print(f"[skip-exc] {sid}: {row['skip_reason']}", flush=True)

        summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
        scored_n = sum(
            1
            for r in summary
            if not r.get("skipped_tool_issue") and not r.get("skipped_exception")
        )
        scored_ok = sum(
            1
            for r in summary
            if r.get("arch_ok")
            and not r.get("skipped_tool_issue")
            and not r.get("skipped_exception")
        )
        bar.set_postfix(ok=f"{scored_ok}/{scored_n}", skip=n_skip)

    meta["finished_at"] = datetime.now().isoformat(timespec="seconds")
    meta["completed_rows"] = len(summary)
    scored = [r for r in summary if not r.get("skipped_tool_issue") and not r.get("skipped_exception")]
    meta["scored"] = len(scored)
    meta["skipped"] = len(summary) - len(scored)
    meta["architecture_correct"] = sum(1 for r in scored if r.get("arch_ok"))
    _write_reports(out_base, summary, meta)
    print(
        f"[done] scored_ok={meta['architecture_correct']}/{meta['scored']} "
        f"skipped={meta['skipped']} → {out_base}",
        flush=True,
    )


if __name__ == "__main__":
    main()
