#!/usr/bin/env python3
"""Run multiple InWild samples and dump all agent LLM I/O per sample."""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
os.environ.setdefault("HF_HUB_OFFLINE", "1")
os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")
os.environ.setdefault("PYTHONUNBUFFERED", "1")

from ts_agent.core.llm import build_provider
from ts_agent.core.utils import ensure_dir, load_yaml
from ts_agent.data.mmts import MMTSBenchDataset
from ts_agent.pipelines.experiment import ExperimentPipeline

# Diverse InWild picks (excluding already-tested :860):
# - 923: 4-series inductive (local segment)
# - 897: 3-series causal
# - 663: 2-series causal (long)
# - 234: 1-series deductive (True/False)
DEFAULT_SAMPLE_IDS = [
    "InWild:tsqa_1084:923",
    "InWild:tsqa_1084:897",
    "InWild:tsqa_1084:663",
    "InWild:tsqa_1084:234",
]

EXP_NAME = "inwild_io_batch4"


def _safe_dir_name(sample_id: str) -> str:
    return sample_id.replace(":", "_").replace("/", "_")


def _write_md(path: Path, sample_id: str, sample, arch, base) -> None:
    md_lines = [
        f"# InWild IO dump: `{sample_id}`",
        "",
        f"- Question: {sample.question}",
        f"- Options: {sample.option}",
        f"- Gold: `{sample.answer}`",
        f"- Architecture pred: `{arch.predicted_answer}` (success={arch.success})",
        f"- Baseline pred: `{base.predicted_answer}` (success={base.success})",
        f"- Architecture model_calls={arch.model_calls}, tool_calls={arch.tool_calls}, "
        f"latency={arch.latency_sec:.1f}s",
        f"- n_series={len(sample.series)} lengths={[len(x) for x in sample.series]} "
        f"task={sample.task_type}",
        "",
    ]
    calls = (arch.details or {}).get("llm_calls") or []
    for c in calls:
        md_lines.append(f"## Call {c.get('call_index')}: `{c.get('call_tag')}`")
        md_lines.append("")
        md_lines.append(
            f"tokens prompt={c.get('prompt_tokens')} completion={c.get('completion_tokens')} "
            f"latency={float(c.get('latency_sec') or 0):.2f}s cached={c.get('cached')}"
        )
        md_lines.append("")
        for m in c.get("messages") or []:
            md_lines.append(f"### INPUT role=`{m.get('role')}`")
            md_lines.append("")
            md_lines.append("```")
            md_lines.append(str(m.get("content", "")))
            md_lines.append("```")
            md_lines.append("")
        md_lines.append("### OUTPUT")
        md_lines.append("")
        md_lines.append("```")
        md_lines.append(str(c.get("response_text", "")))
        md_lines.append("```")
        md_lines.append("")

    md_lines.append("# Baseline LLM calls")
    md_lines.append("")
    for c in (base.details or {}).get("llm_calls") or []:
        md_lines.append(f"## Call {c.get('call_index')}: `{c.get('call_tag')}`")
        md_lines.append("")
        md_lines.append(
            f"tokens prompt={c.get('prompt_tokens')} completion={c.get('completion_tokens')} "
            f"latency={float(c.get('latency_sec') or 0):.2f}s cached={c.get('cached')}"
        )
        md_lines.append("")
        for m in c.get("messages") or []:
            md_lines.append(f"### INPUT role=`{m.get('role')}`")
            md_lines.append("")
            md_lines.append("```")
            md_lines.append(str(m.get("content", "")))
            md_lines.append("```")
            md_lines.append("")
        md_lines.append("### OUTPUT")
        md_lines.append("")
        md_lines.append("```")
        md_lines.append(str(c.get("response_text", "")))
        md_lines.append("```")
        md_lines.append("")

    path.write_text("\n".join(md_lines), encoding="utf-8")


def run_one(pipe: ExperimentPipeline, sample, out_root: Path) -> Dict[str, Any]:
    sid = sample.sample_id
    out_dir = ensure_dir(out_root / _safe_dir_name(sid))
    print(
        f"\n[info] === {sid} n_series={len(sample.series)} "
        f"lens={[len(x) for x in sample.series]} task={sample.task_type} gold={sample.answer}",
        flush=True,
    )
    print(f"[info] Q: {sample.question[:200]}", flush=True)

    print("[info] running architecture...", flush=True)
    arch = pipe.run_architecture(sample)
    print(
        f"[info] architecture pred={arch.predicted_answer} gold={arch.ground_truth} "
        f"ok={arch.success} calls={arch.model_calls} tools={arch.tool_calls} "
        f"latency={arch.latency_sec:.1f}s error={arch.error}",
        flush=True,
    )

    print("[info] running baseline...", flush=True)
    base = pipe.run_baseline(sample)
    print(
        f"[info] baseline pred={base.predicted_answer} gold={base.ground_truth} "
        f"ok={base.success} calls={base.model_calls} latency={base.latency_sec:.1f}s",
        flush=True,
    )

    payload = {
        "sample_id": sid,
        "question": sample.question,
        "options": sample.option,
        "gold": sample.answer,
        "task_type": sample.task_type,
        "n_series": len(sample.series),
        "series_lengths": [len(x) for x in sample.series],
        "architecture": arch.model_dump(),
        "baseline": base.model_dump(),
    }
    out_json = out_dir / "full_io.json"
    out_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    _write_md(out_dir / "full_io.md", sid, sample, arch, base)

    n_arch = len((arch.details or {}).get("llm_calls") or [])
    n_base = len((base.details or {}).get("llm_calls") or [])
    print(f"[done] wrote {out_json} (arch_calls={n_arch}, baseline_calls={n_base})", flush=True)

    return {
        "sample_id": sid,
        "n_series": len(sample.series),
        "series_lengths": [len(x) for x in sample.series],
        "task_type": sample.task_type,
        "gold": sample.answer,
        "arch_pred": arch.predicted_answer,
        "arch_ok": bool(arch.predicted_answer) and str(arch.predicted_answer).strip().upper()[:1]
        == str(sample.answer).strip().upper()[:1],
        "baseline_pred": base.predicted_answer,
        "baseline_ok": bool(base.predicted_answer) and str(base.predicted_answer).strip().upper()[:1]
        == str(sample.answer).strip().upper()[:1],
        "arch_model_calls": arch.model_calls,
        "arch_tool_calls": arch.tool_calls,
        "arch_latency_sec": arch.latency_sec,
        "out_dir": str(out_dir),
    }


def main(sample_ids: Optional[Sequence[str]] = None) -> None:
    ids = list(sample_ids or DEFAULT_SAMPLE_IDS)
    cfg = load_yaml(ROOT / "configs" / "experiment.yaml")
    cfg["experiment"]["use_mock_llm"] = False
    cfg["experiment"]["max_series_text_chars"] = None
    cfg["experiment"]["cache_dir"] = str(ROOT / "outputs" / EXP_NAME / "llm_cache")
    cfg["model"]["device_map"] = "cuda:0"

    print(f"[info] loading {len(ids)} samples...", flush=True)
    ds = MMTSBenchDataset(
        cfg["data"]["processed_dir"],
        raw_dir=cfg["data"]["raw_dir"],
        max_series_text_chars=None,
    )
    samples = ds.filter(sample_ids=ids)
    found = {s.sample_id for s in samples}
    missing = [x for x in ids if x not in found]
    if missing:
        raise SystemExit(f"samples not found: {missing}")
    # preserve requested order
    by_id = {s.sample_id: s for s in samples}
    ordered = [by_id[i] for i in ids]

    print("[info] building LLM provider (Qwen2.5-14B)...", flush=True)
    llm = build_provider(cfg)
    llm.record_io = True
    pipe = ExperimentPipeline(
        llm,
        cfg["experiment"]["prompt_dir"],
        max_tool_rounds=int(cfg["experiment"].get("max_tool_rounds", 3)),
    )

    out_root = ensure_dir(ROOT / "outputs" / EXP_NAME)
    summary: List[Dict[str, Any]] = []
    for sample in ordered:
        summary.append(run_one(pipe, sample, out_root))

    summary_path = out_root / "summary.json"
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    # markdown overview
    lines = ["# InWild IO batch summary", ""]
    lines.append("| sample | n_series | task | gold | arch | base | arch_ok | base_ok | calls | tools | latency_s |")
    lines.append("|---|---:|---|---|---|---|---|---|---:|---:|---:|")
    for r in summary:
        lines.append(
            f"| `{r['sample_id']}` | {r['n_series']} | {r['task_type']} | {r['gold']} | "
            f"{r['arch_pred']} | {r['baseline_pred']} | {r['arch_ok']} | {r['baseline_ok']} | "
            f"{r['arch_model_calls']} | {r['arch_tool_calls']} | {r['arch_latency_sec']:.1f} |"
        )
    lines.append("")
    for r in summary:
        lines.append(f"- `{r['sample_id']}` → `{r['out_dir']}/full_io.md`")
    (out_root / "summary.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"[done] summary → {summary_path}", flush=True)
    n_ok = sum(1 for r in summary if r["arch_ok"])
    print(f"[done] architecture correct {n_ok}/{len(summary)}", flush=True)


if __name__ == "__main__":
    argv_ids = [a for a in sys.argv[1:] if a.startswith("InWild:")]
    main(argv_ids or None)
