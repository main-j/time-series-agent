#!/usr/bin/env python3
"""Full MMTS-Bench architecture evaluation with taxonomy live stats.

- Universe: all samples in data/processed/mmts-bench/index.jsonl (2424)
- Architecture only (no baseline)
- On tool/$ref/call issues or OOM/exception: record + skip sample (continue batch)
- Accuracy excludes skipped samples
- Terminal shows overall / current-subset / current-task running accuracy
- Final report: by subset + by taxonomy task (and dimension)

Example:
  python3 scripts/run_full_arch_eval.py --exp-name full_arch_eval_v1
  python3 scripts/run_full_arch_eval.py --exp-name full_arch_eval_v1 --resume
  python3 scripts/run_full_arch_eval.py --limit 5
"""
from __future__ import annotations

import argparse
import gc
import json
import os
import re
import sys
import traceback
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

from tqdm import tqdm

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(SCRIPTS))
os.environ.setdefault("HF_HUB_OFFLINE", "1")
os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")
os.environ.setdefault("PYTHONUNBUFFERED", "1")

from mmts_taxonomy import (  # noqa: E402
    SUBSET_ORDER,
    TASK_DIMENSION,
    TASK_KEYS,
    TASK_LABEL,
    compute_evaluation_stats,
    normalize_subset,
    taxonomy_tasks_for_sample,
    write_stats_markdown,
)
from run_feasibility_batch import _answer_correct, run_one  # noqa: E402
from ts_agent.core.llm import build_provider
from ts_agent.core.utils import ensure_dir, load_yaml
from ts_agent.data.mmts import MMTSBenchDataset
from ts_agent.pipelines.experiment import ExperimentPipeline

DEFAULT_INDEX = ROOT / "data" / "processed" / "mmts-bench" / "index.jsonl"

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


def _load_all_ids(index_path: Path) -> List[str]:
    ids: List[str] = []
    for line in index_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        ids.append(str(json.loads(line)["sample_id"]))
    return ids


def _acc(ok: int, n: int) -> str:
    if n <= 0:
        return "—/0"
    return f"{ok}/{n} ({100.0 * ok / n:.1f}%)"


def primary_task_key(task_keys: List[str]) -> str:
    """Prefer specific feature/reasoning/match/align task over blanket Uni.-Multi."""
    for key in task_keys:
        if key != "Structural/Uni.-Multi.":
            return key
    return task_keys[0] if task_keys else "Unknown"


def scan_tool_issues(arch: Dict[str, Any]) -> Dict[str, Any]:
    details = arch.get("details") or {}
    attempted = successes = failed = issue_hits = 0
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


class LiveStats:
    """Running accuracy among scored (non-skipped) samples."""

    def __init__(self) -> None:
        self.scored_n = 0
        self.scored_ok = 0
        self.skipped = 0
        self.by_subset: Dict[str, Dict[str, int]] = {
            s: {"n": 0, "ok": 0} for s in SUBSET_ORDER
        }
        self.by_task: Dict[str, Dict[str, int]] = {k: {"n": 0, "ok": 0} for k in TASK_KEYS}

    def observe_scored(self, subset: str, task_keys: List[str], ok: bool) -> None:
        self.scored_n += 1
        if ok:
            self.scored_ok += 1
        if subset in self.by_subset:
            self.by_subset[subset]["n"] += 1
            if ok:
                self.by_subset[subset]["ok"] += 1
        seen: Set[str] = set()
        for key in task_keys:
            if key in seen or key not in self.by_task:
                continue
            seen.add(key)
            self.by_task[key]["n"] += 1
            if ok:
                self.by_task[key]["ok"] += 1

    def observe_skip(self) -> None:
        self.skipped += 1

    def postfix(self, subset: str, task_key: str) -> Dict[str, str]:
        sub = self.by_subset.get(subset, {"n": 0, "ok": 0})
        task = self.by_task.get(task_key, {"n": 0, "ok": 0})
        label = TASK_LABEL.get(task_key, task_key)
        return {
            "all": _acc(self.scored_ok, self.scored_n),
            "sub": f"{subset} {_acc(sub['ok'], sub['n'])}",
            "task": f"{label} {_acc(task['ok'], task['n'])}",
            "skip": str(self.skipped),
        }


def _completed_ids(summary: List[Dict[str, Any]]) -> Set[str]:
    done: Set[str] = set()
    for row in summary:
        sid = str(row.get("sample_id") or "")
        if not sid:
            continue
        if row.get("skipped_tool_issue") or row.get("skipped_exception"):
            done.add(sid)
        elif not row.get("incomplete"):
            done.add(sid)
    return done


def _rebuild_live_from_summary(summary: List[Dict[str, Any]]) -> LiveStats:
    live = LiveStats()
    for row in summary:
        if row.get("skipped_tool_issue") or row.get("skipped_exception"):
            live.observe_skip()
            continue
        if row.get("incomplete"):
            continue
        subset = normalize_subset(row.get("subset"), str(row.get("sample_id")))
        tasks = row.get("taxonomy_tasks") or taxonomy_tasks_for_sample(
            str(row.get("sample_id")), subset, row.get("task_type")
        )
        live.observe_scored(subset, list(tasks), bool(row.get("arch_ok")))
    return live


def _write_final_reports(out_base: Path, summary: List[Dict[str, Any]], meta: Dict[str, Any]) -> None:
    scored = [
        r
        for r in summary
        if not r.get("skipped_tool_issue")
        and not r.get("skipped_exception")
        and not r.get("incomplete")
    ]
    skipped = [r for r in summary if r.get("skipped_tool_issue") or r.get("skipped_exception")]

    # Reuse taxonomy stats (baseline fields unused → 0).
    stats_rows = []
    for r in scored:
        stats_rows.append(
            {
                "sample_id": r.get("sample_id"),
                "subset": r.get("subset"),
                "task_type": r.get("task_type"),
                "arch_ok": bool(r.get("arch_ok")),
                "baseline_ok": False,
                "source": "arch_eval",
            }
        )
    stats = compute_evaluation_stats(stats_rows)
    write_stats_markdown(
        out_base / "stats_by_taxonomy.md",
        stats,
        title="Full MMTS architecture evaluation — taxonomy stats",
        extra_lines=[
            f"- Scored samples: {len(scored)}",
            f"- Skipped (tool/exception): {len(skipped)}",
            "- Baseline not run in this experiment (base_ok columns are unused).",
        ],
    )
    (out_base / "stats_by_taxonomy.json").write_text(
        json.dumps(stats, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    lines = [
        "# Full MMTS architecture evaluation",
        "",
        f"- Finished rows: {len(summary)}",
        f"- Scored: **{len(scored)}**",
        f"- Skipped (tool/exception): **{len(skipped)}**",
        f"- Architecture correct (scored): "
        f"**{sum(1 for r in scored if r.get('arch_ok'))}/{len(scored)}**",
        "",
        "See `stats_by_taxonomy.md` for subset / task / dimension tables.",
        "",
        "## Skipped samples",
        "",
    ]
    if not skipped:
        lines.append("(none)")
    else:
        lines.append("| sample | subset | task | reason |")
        lines.append("|---|---|---|---|")
        for r in skipped:
            sid = r.get("sample_id")
            subset = normalize_subset(r.get("subset"), str(sid))
            tasks = r.get("taxonomy_tasks") or []
            primary = TASK_LABEL.get(primary_task_key(tasks), primary_task_key(tasks))
            reason = r.get("skip_reason") or ""
            lines.append(f"| `{sid}` | {subset} | {primary} | {reason} |")
    (out_base / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    meta["scored"] = len(scored)
    meta["skipped"] = len(skipped)
    meta["architecture_correct"] = sum(1 for r in scored if r.get("arch_ok"))
    (out_base / "run_manifest.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--exp-name", default="full_arch_eval_v1")
    p.add_argument("--index-file", type=Path, default=DEFAULT_INDEX)
    p.add_argument("--resume", action="store_true")
    p.add_argument("--limit", type=int, default=None)
    p.add_argument("--device", default="cuda:0")
    return p.parse_args()


def main() -> None:
    args = _parse_args()
    out_base = ensure_dir(ROOT / "outputs" / args.exp_name)
    runs = ensure_dir(out_base / "runs")
    issues_path = out_base / "tool_issues.jsonl"
    summary_path = out_base / "summary.json"

    all_ids = _load_all_ids(args.index_file)
    summary: List[Dict[str, Any]] = []
    if args.resume and summary_path.is_file():
        try:
            summary = json.loads(summary_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            summary = []

    done = _completed_ids(summary) if args.resume else set()
    pending = [sid for sid in all_ids if sid not in done]
    if args.limit is not None:
        pending = pending[: args.limit]

    live = _rebuild_live_from_summary(summary) if args.resume else LiveStats()

    meta = {
        "exp_name": args.exp_name,
        "index_file": str(args.index_file),
        "total": len(all_ids),
        "already_done": len(done),
        "pending": len(pending),
        "resume": bool(args.resume),
        "limit": args.limit,
        "started_at": datetime.now().isoformat(timespec="seconds"),
        "policy": "skip_sample_on_tool_issue; accuracy excludes skipped",
        "stats_layers": ["subset", "taxonomy_task", "dimension"],
    }
    (out_base / "sample_ids.txt").write_text("\n".join(all_ids) + "\n", encoding="utf-8")
    (out_base / "run_manifest.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")

    print(
        f"[info] full MMTS={len(all_ids)} pending={len(pending)} exp={args.exp_name}",
        flush=True,
    )
    if not pending:
        print("[done] nothing to run.", flush=True)
        _write_final_reports(out_base, summary, meta)
        return

    cfg = load_yaml(ROOT / "configs" / "experiment.yaml")
    cfg["experiment"]["use_mock_llm"] = False
    cfg["experiment"]["max_series_text_chars"] = None
    cfg["experiment"]["cache_dir"] = str(out_base / "llm_cache")
    cfg["model"]["device_map"] = args.device

    print("[info] loading dataset index...", flush=True)
    ds = MMTSBenchDataset(
        cfg["data"]["processed_dir"],
        raw_dir=cfg["data"]["raw_dir"],
        max_series_text_chars=None,
    )
    # Load pending in chunks would be nicer, but filter handles list.
    print(f"[info] resolving {len(pending)} samples...", flush=True)
    samples = ds.filter(sample_ids=pending)
    by_id = {s.sample_id: s for s in samples}
    missing = [x for x in pending if x not in by_id]
    if missing:
        raise SystemExit(f"samples not found ({len(missing)}): {missing[:5]}...")

    print("[info] building LLM...", flush=True)
    llm = build_provider(cfg)
    llm.record_io = True
    pipe = ExperimentPipeline(
        llm,
        cfg["experiment"]["prompt_dir"],
        max_tool_rounds=int(cfg["experiment"].get("max_tool_rounds", 3)),
    )

    bar = tqdm(pending, desc="full-arch", unit="sample")
    for sid in bar:
        sample = by_id[sid]
        subset = normalize_subset(sample.subset, sid)
        task_keys = taxonomy_tasks_for_sample(sid, subset, sample.task_type)
        primary = primary_task_key(task_keys)
        primary_label = TASK_LABEL.get(primary, primary)

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
            ok = _answer_correct(sample.question_type, arch.get("predicted_answer"), sample.answer)
            row.update(
                {
                    "subset": subset,
                    "task_type": sample.task_type,
                    "taxonomy_tasks": task_keys,
                    "primary_task": primary,
                    "tool_scan": scan,
                    "arch_ok": ok,
                }
            )

            if scan["has_issue"]:
                row["skipped_tool_issue"] = True
                row["skip_reason"] = scan["reason"]
                row["arch_ok"] = False
                live.observe_skip()
                with issues_path.open("a", encoding="utf-8") as f:
                    f.write(
                        json.dumps(
                            {
                                "sample_id": sid,
                                "subset": subset,
                                "primary_task": primary,
                                "reason": scan["reason"],
                                "examples": scan["examples"],
                            },
                            ensure_ascii=False,
                        )
                        + "\n"
                    )
                tqdm.write(f"[skip-tool] {sid} [{subset}/{primary_label}] {scan['reason']}")
            else:
                live.observe_scored(subset, task_keys, ok)
                mark = "✓" if ok else "✗"
                tqdm.write(
                    f"[{mark}] {sid} gold={row.get('gold')} pred={row.get('arch_pred')} "
                    f"| {subset} {_acc(live.by_subset[subset]['ok'], live.by_subset[subset]['n'])} "
                    f"| {primary_label} {_acc(live.by_task[primary]['ok'], live.by_task[primary]['n'])}"
                )

            summary.append(row)
        except Exception as exc:
            tb = traceback.format_exc()
            err = str(exc)
            low = err.lower()
            is_oom = ("out of memory" in low) or ("cuda" in low and "memory" in low)
            row = {
                "sample_id": sid,
                "subset": subset,
                "task_type": sample.task_type,
                "taxonomy_tasks": task_keys,
                "primary_task": primary,
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
            live.observe_skip()
            summary.append(row)
            with issues_path.open("a", encoding="utf-8") as f:
                f.write(
                    json.dumps(
                        {"sample_id": sid, "subset": subset, "reason": row["skip_reason"], "error": err},
                        ensure_ascii=False,
                    )
                    + "\n"
                )
            (out_base / "last_exception.txt").write_text(tb, encoding="utf-8")
            tqdm.write(f"[skip-exc] {sid} [{subset}/{primary_label}] {row['skip_reason']}")

        summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
        bar.set_postfix(live.postfix(subset, primary))

        # Lightweight checkpoint of running subset/task snapshot
        (out_base / "live_stats.json").write_text(
            json.dumps(
                {
                    "scored": {"ok": live.scored_ok, "n": live.scored_n},
                    "skipped": live.skipped,
                    "by_subset": live.by_subset,
                    "by_task": {
                        k: v for k, v in live.by_task.items() if v["n"] > 0
                    },
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )

    meta["finished_at"] = datetime.now().isoformat(timespec="seconds")
    meta["completed_rows"] = len(summary)
    _write_final_reports(out_base, summary, meta)
    print(
        f"[done] scored={_acc(live.scored_ok, live.scored_n)} skipped={live.skipped} → {out_base}",
        flush=True,
    )


if __name__ == "__main__":
    main()
