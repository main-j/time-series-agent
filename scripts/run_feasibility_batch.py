#!/usr/bin/env python3
"""Run the 19-task feasibility sample set (all MMTS subsets)."""
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

EXP_NAME = "feasibility_test_19"
DEFAULT_IDS_FILE = ROOT / "outputs" / EXP_NAME / "sample_ids.txt"


def _safe_dir_name(sample_id: str) -> str:
    return sample_id.replace(":", "_").replace("/", "_")


def _answer_correct(question_type: str, predicted: Any, ground_truth: Any) -> bool:
    if predicted is None or str(predicted).strip() == "":
        return False
    if question_type == "numerical":
        try:
            pred = float(predicted)
            gold = float(ground_truth)
        except (TypeError, ValueError):
            return False
        if gold == 0:
            return pred == 0
        return abs(pred - gold) / abs(gold) <= 0.05
    return str(predicted).strip().upper()[:1] == str(ground_truth).strip().upper()[:1]


def _write_md(path: Path, sample_id: str, sample, arch, base=None) -> None:
    md_lines = [
        f"# Feasibility IO dump: `{sample_id}`",
        "",
        f"- Question: {sample.question}",
        f"- Options: {sample.option}",
        f"- Gold: `{sample.answer}`",
        f"- Architecture pred: `{arch.predicted_answer}` (success={arch.success})",
        (
            f"- Baseline pred: `{base.predicted_answer}` (success={base.success})"
            if base is not None
            else "- Baseline: skipped"
        ),
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

    if base is not None:
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


def _agent_label(call_tag: str) -> str:
    tag = str(call_tag or "unknown")
    if tag == "planner":
        return "Planner"
    if tag == "integration":
        return "Integration"
    if tag.startswith("homogeneous:"):
        parts = tag.split(":")
        scale = parts[1] if len(parts) > 1 else "?"
        round_no = parts[2] if len(parts) > 2 else "?"
        return f"Homogeneous ({scale}, {round_no})"
    if tag.startswith("heterogeneous:"):
        parts = tag.split(":")
        role = parts[1] if len(parts) > 1 else "?"
        round_no = parts[2] if len(parts) > 2 else "?"
        return f"Heterogeneous ({role}, {round_no})"
    if tag == "baseline":
        return "Baseline"
    return tag


def _write_agent_io_summary(path: Path, sample_id: str, arch) -> None:
    calls = (arch.details or {}).get("llm_calls") or []
    lines = [
        f"# Agent IO summary: `{sample_id}`",
        "",
        f"- Architecture pred: `{arch.predicted_answer}` (success={arch.success})",
        f"- model_calls={arch.model_calls}, tool_calls={arch.tool_calls}, latency={arch.latency_sec:.1f}s",
        "",
    ]
    for c in calls:
        tag = str(c.get("call_tag") or "unknown")
        lines.append(f"## {_agent_label(tag)} — `{tag}`")
        lines.append("")
        lines.append(
            f"tokens prompt={c.get('prompt_tokens')} completion={c.get('completion_tokens')} "
            f"latency={float(c.get('latency_sec') or 0):.2f}s"
        )
        lines.append("")
        for m in c.get("messages") or []:
            lines.append(f"### INPUT ({m.get('role')})")
            lines.append("")
            lines.append("```")
            lines.append(str(m.get("content", "")))
            lines.append("```")
            lines.append("")
        lines.append("### OUTPUT")
        lines.append("")
        lines.append("```")
        lines.append(str(c.get("response_text", "")))
        lines.append("```")
        lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def run_one(
    pipe: ExperimentPipeline,
    sample,
    out_root: Path,
    *,
    run_baseline: bool = True,
) -> Dict[str, Any]:
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

    base = None
    if run_baseline:
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
        "baseline": None if base is None else base.model_dump(),
    }
    out_json = out_dir / "full_io.json"
    out_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    _write_md(out_dir / "full_io.md", sid, sample, arch, base)
    _write_agent_io_summary(out_dir / "agent_io_summary.md", sid, arch)

    return {
        "sample_id": sid,
        "subset": str(sample.subset),
        "n_series": len(sample.series),
        "series_lengths": [len(x) for x in sample.series],
        "task_type": sample.task_type,
        "gold": sample.answer,
        "arch_pred": arch.predicted_answer,
        "arch_ok": _answer_correct(sample.question_type, arch.predicted_answer, sample.answer),
        "baseline_pred": None if base is None else base.predicted_answer,
        "baseline_ok": (
            None
            if base is None
            else _answer_correct(sample.question_type, base.predicted_answer, sample.answer)
        ),
        "arch_model_calls": arch.model_calls,
        "arch_tool_calls": arch.tool_calls,
        "arch_latency_sec": arch.latency_sec,
        "arch_error": arch.error,
        "out_dir": str(out_dir),
    }


def _load_ids(path: Path) -> List[str]:
    return [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def main(sample_ids: Optional[Sequence[str]] = None, ids_file: Optional[Path] = None) -> None:
    ids = list(sample_ids or _load_ids(ids_file or DEFAULT_IDS_FILE))
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

    out_root = ensure_dir(ROOT / "outputs" / EXP_NAME / "runs")
    summary: List[Dict[str, Any]] = []
    for sample in ordered:
        summary.append(run_one(pipe, sample, out_root))
        # checkpoint after each sample
        (out_root / "summary.json").write_text(
            json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    lines = ["# Feasibility test summary (19 tasks)", ""]
    lines.append("| sample | subset | n_series | task | gold | arch | base | arch_ok | base_ok | tools | latency_s |")
    lines.append("|---|---|---:|---|---|---|---|---|---|---:|---:|")
    for r in summary:
        lines.append(
            f"| `{r['sample_id']}` | {r['subset']} | {r['n_series']} | {r['task_type']} | {r['gold']} | "
            f"{r['arch_pred']} | {r['baseline_pred']} | {r['arch_ok']} | {r['baseline_ok']} | "
            f"{r['arch_tool_calls']} | {r['arch_latency_sec']:.1f} |"
        )
    lines.append("")
    n_ok = sum(1 for r in summary if r["arch_ok"])
    lines.append(f"Architecture correct: **{n_ok}/{len(summary)}**")
    (out_root / "summary.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"[done] summary → {out_root / 'summary.json'}", flush=True)
    print(f"[done] architecture correct {n_ok}/{len(summary)}", flush=True)


if __name__ == "__main__":
    argv_ids = [a for a in sys.argv[1:] if ":" in a and not a.startswith("-")]
    ids_file = None
    for i, a in enumerate(sys.argv[1:]):
        if a == "--ids-file" and i + 2 <= len(sys.argv):
            ids_file = Path(sys.argv[i + 2])
    main(argv_ids or None, ids_file=ids_file)
