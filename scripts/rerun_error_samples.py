#!/usr/bin/env python3
"""Rerun known architecture-error samples; stop on tool/$ref issues."""
from __future__ import annotations

import gc
import json
import re
import sys
import traceback
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from scripts.run_feasibility_batch import _answer_correct, run_one
from ts_agent.core.llm import build_provider
from ts_agent.core.utils import ensure_dir, load_yaml
from ts_agent.data.mmts import MMTSBenchDataset
from ts_agent.pipelines.experiment import ExperimentPipeline

SAMPLES = [
    "Base:synthtic_qa_700:108",
    "Base:synthtic_qa_700:91",
    "InWild:tsqa_1084:47",
    "InWild:tsqa_1084:944",
    "InWild:tsqa_1084:908",
    "InWild:tsqa_1084:303",
    "Match:qats_400:226",
    "Match:qats_400:57",
    "Match:qats_400:136",
    "Match:qats_400:340",
]

UNRESOLVED_RE = re.compile(
    r"unresolved reference|invalid reference|tool tool not in prior|\$tool\.series",
    re.I,
)


def inspect_tool_issues(arch: Dict[str, Any]) -> Dict[str, Any]:
    details = arch.get("details") or {}
    attempted = 0
    failed = 0
    unresolved = 0
    successes = 0
    examples: List[Dict[str, Any]] = []

    def consider(step: Dict[str, Any], where: str) -> None:
        nonlocal attempted, failed, unresolved, successes
        attempted += 1
        ok = bool(step.get("success"))
        err = str(step.get("error") or "")
        if ok:
            successes += 1
            return
        failed += 1
        args_txt = json.dumps(step.get("arguments") or {}, ensure_ascii=False)
        if UNRESOLVED_RE.search(err) or UNRESOLVED_RE.search(args_txt):
            unresolved += 1
            if len(examples) < 8:
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
    for e in details.get("evidences") or []:
        for t in e.get("executed_tools") or []:
            consider(
                {
                    "success": t.get("success"),
                    "error": t.get("error"),
                    "call_id": t.get("call_id"),
                    "tool_name": t.get("name") or t.get("tool"),
                    "arguments": t.get("arguments") or {},
                },
                f"evidence:{e.get('role')}",
            )

    err = str(arch.get("error") or "")
    crash_toolish = bool(
        re.search(r"period|unresolved|WorkflowExecutor|series_index|KeyError", err, re.I)
    ) and err not in ("", "None")

    stop = False
    reason = None
    if unresolved > 0:
        stop = True
        reason = f"found {unresolved} unresolved/$ref tool failures out of {attempted} attempted steps"
    elif crash_toolish and attempted == 0:
        stop = True
        reason = f"architecture crash before/during tools: {err!r}"
    elif attempted > 0 and successes == 0 and failed == attempted:
        bindish = any(
            "unresolved" in str(x.get("error", "")).lower()
            or "$" in json.dumps(x.get("arguments") or {})
            for x in examples
        )
        if bindish:
            stop = True
            reason = f"all {attempted} tool steps failed (binding-related)"

    return {
        "stop": stop,
        "reason": reason,
        "attempted": attempted,
        "successes": successes,
        "failed": failed,
        "unresolved": unresolved,
        "examples": examples,
        "arch_error": err or None,
    }


def main() -> None:
    out_root = ensure_dir(ROOT / "outputs" / "error_samples_rerun_v1")
    runs = ensure_dir(out_root / "runs")

    cfg = load_yaml(ROOT / "configs" / "experiment.yaml")
    cfg["experiment"]["use_mock_llm"] = False
    cfg["experiment"]["max_series_text_chars"] = None
    cfg["experiment"]["cache_dir"] = str(out_root / "llm_cache")
    cfg["model"]["device_map"] = "cuda:0"

    print("[info] loading samples...", flush=True)
    ds = MMTSBenchDataset(
        cfg["data"]["processed_dir"],
        raw_dir=cfg["data"]["raw_dir"],
        max_series_text_chars=None,
    )
    samples = ds.filter(sample_ids=SAMPLES)
    by_id = {s.sample_id: s for s in samples}
    missing = [x for x in SAMPLES if x not in by_id]
    if missing:
        raise SystemExit(f"missing samples: {missing}")

    print("[info] building LLM...", flush=True)
    llm = build_provider(cfg)
    llm.record_io = True
    pipe = ExperimentPipeline(
        llm,
        cfg["experiment"]["prompt_dir"],
        max_tool_rounds=int(cfg["experiment"].get("max_tool_rounds", 3)),
    )

    summary: List[Dict[str, Any]] = []
    stopped = False
    stop_payload: Dict[str, Any] | None = None

    for i, sid in enumerate(SAMPLES, 1):
        sample = by_id[sid]
        print(f"\n######## [{i}/{len(SAMPLES)}] {sid} ########", flush=True)
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
            tool_report = inspect_tool_issues(arch)
            row["tool_report"] = tool_report
            row["arch_ok"] = _answer_correct(
                sample.question_type, arch.get("predicted_answer"), sample.answer
            )
            summary.append(row)
            (out_root / "summary.json").write_text(
                json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
            )
            print(
                f"[result] pred={row['arch_pred']} gold={row['gold']} ok={row['arch_ok']} "
                f"tools={row['arch_tool_calls']} unresolved={tool_report['unresolved']} "
                f"tool_ok={tool_report['successes']}/{tool_report['attempted']}",
                flush=True,
            )
            if tool_report["stop"]:
                stopped = True
                stop_payload = {"sample_id": sid, "tool_report": tool_report, "row": row}
                print(f"[STOP] tool/call issue on {sid}: {tool_report['reason']}", flush=True)
                break
        except Exception as exc:
            tb = traceback.format_exc()
            err_text = str(exc)
            low = err_text.lower()
            is_oom = ("out of memory" in low) or ("cuda" in low and "memory" in low)
            is_toolish = bool(UNRESOLVED_RE.search(err_text)) or (
                "WorkflowExecutor" in err_text or "KeyError" in err_text
            )
            row = {
                "sample_id": sid,
                "gold": sample.answer,
                "arch_pred": None,
                "arch_ok": False,
                "error": err_text,
                "traceback": tb,
                "oom": is_oom,
            }
            summary.append(row)
            (out_root / "summary.json").write_text(
                json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
            )
            (out_root / "last_exception.txt").write_text(tb, encoding="utf-8")
            print(f"[exception] {sid}: {err_text}", flush=True)
            stopped = True
            stop_payload = {
                "sample_id": sid,
                "exception": err_text,
                "oom": is_oom,
                "toolish": is_toolish,
                "traceback": tb,
            }
            print(
                f"[STOP] exception on {sid} (oom={is_oom} toolish={is_toolish})",
                flush=True,
            )
            break

    meta = {
        "stopped": stopped,
        "stop_payload": stop_payload,
        "completed": len(summary),
        "total": len(SAMPLES),
        "correct": sum(1 for r in summary if r.get("arch_ok")),
    }
    (out_root / "run_meta.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(
        "[done] meta=",
        json.dumps(
            {k: meta[k] for k in ("stopped", "completed", "total", "correct")},
            ensure_ascii=False,
        ),
        flush=True,
    )


if __name__ == "__main__":
    main()
